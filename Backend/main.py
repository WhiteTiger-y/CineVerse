import os
import sys
# --- THIS IS THE CRUCIAL FIX ---
# Get the absolute path of the current file (main.py)
current_file_path = os.path.dirname(os.path.abspath(__file__))
# Get the path of the parent directory (the project root)
project_root_path = os.path.dirname(current_file_path)
# Add the project root to Python's path
sys.path.append(project_root_path)
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# LangChain Imports
import requests
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import Tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from Backend import crud, schemas, security, database, email_utils
from Backend.database import SessionLocal
class CustomHuggingFaceInferenceAPIEmbeddings(Embeddings):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def _embed(self, texts: List[str]) -> List[List[float]]:
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={"inputs": texts, "options": {"wait_for_model": True}}
        )
        if response.status_code != 200:
            raise Exception(f"HuggingFace API request failed with status {response.status_code}: {response.text}")
        return response.json()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]
    
# --- Load Environment Variables Correctly ---
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Local Imports ---
from . import crud, schemas, security, database, email_utils
from .database import SessionLocal

# --- Create Database Tables ---
database.Base.metadata.create_all(bind=database.engine)

# --- Initialize FastAPI App ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Authentication and User Endpoints ---

@app.post("/signup", response_model=schemas.User)
def signup_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    db_user_by_mobile = crud.get_user_by_mobile(db, mobile_no=user.mobile_no)
    if db_user_by_mobile:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    new_user = crud.create_user(db=db, user=user)
    
    email_utils.send_welcome_email(
        to_email=new_user.email,
        first_name=new_user.first_name,
        username=new_user.username
    )
    return new_user

@app.post("/login")
def login_user(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = None
    if "@" in user_login.identifier:
        db_user = crud.get_user_by_email(db, email=user_login.identifier)
    else:
        db_user = crud.get_user_by_username(db, username=user_login.identifier)
    
    if not db_user or not security.verify_password(user_login.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username/email or password")
    
    return {
        "message": "Login successful", 
        "user_id": db_user.id, 
        "email": db_user.email,
        "username": db_user.username
    }

@app.post("/check-email")
def check_user_email(request: schemas.EmailCheck, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=request.email)
    if db_user:
        return {"exists": True}
    return {"exists": False}

@app.post("/check-mobile")
def check_user_mobile(request: schemas.MobileCheck, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_mobile(db, mobile_no=request.mobile_no)
    if db_user:
        return {"exists": True}
    return {"exists": False}

@app.post("/forgot-password")
def forgot_password(request: schemas.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=request.email)
    if user:
        token = security.generate_reset_token(email=user.email)
        email_utils.send_password_reset_email(to_email=user.email, token=token)
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@app.post("/reset-password")
def reset_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    email = security.verify_reset_token(token=request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.update_user_password(db=db, user=user, new_password=request.new_password)
    return {"message": "Password updated successfully."}

@app.put("/account/username", response_model=schemas.User)
def update_user_username(request: schemas.UsernameUpdate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_username(db, username=request.new_username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already taken.")
    return crud.update_username(db=db, user_id=request.user_id, new_username=request.new_username)

@app.put("/account/password")
def update_user_password_route(request: schemas.PasswordUpdate, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id=request.user_id)
    if not security.verify_password(request.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password.")
    crud.update_user_password(db=db, user=user, new_password=request.new_password)
    return {"message": "Password updated successfully."}

@app.put("/account/profile-pic", response_model=schemas.User)
def update_user_profile_pic(request: schemas.ProfilePicUpdate, db: Session = Depends(get_db)):
    return crud.update_profile_pic_url(db=db, user_id=request.user_id, url=request.url)


# --- LangChain Agent Setup ---
INDEX_NAME = "cineverse-movies"
chat_histories = {} 

# Initialize Models
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, convert_system_message_to_human=True)

# Initialize Hugging Face Embedding Model
embeddings = CustomHuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    model_name="intfloat/multilingual-e5-large"
)

# Connect to the existing Pinecone index
print(f"Connecting to Pinecone index '{INDEX_NAME}'...")
vector_store = PineconeVectorStore.from_existing_index(
    index_name=INDEX_NAME,
    embedding=embeddings
)
retriever = vector_store.as_retriever()
print("Successfully connected to Pinecone.")

# Define Agent Tools
retriever_tool = create_retriever_tool(
    retriever,
    "movie_database_search",
    "Searches and returns information about movies from a database."
)

def scrape_webpage(url: str) -> str:
    try:
        headers = { "User-Agent": "Mozilla/5.0..." }
        loader = WebBaseLoader(url, requests_kwargs={"headers": headers})
        docs = loader.load()
        return "".join(doc.page_content for doc in docs)
    except Exception as e:
        return f"Error scraping website: {e}"

web_scraper_tool = Tool(
    name="web_scraper_tool",
    func=scrape_webpage,
    description="A tool to scrape a single webpage for very recent movies."
)

tools = [retriever_tool, web_scraper_tool]

# Create Agent Prompt
prompt_template = """
You are CineVerse AI, a friendly, empathetic, and conversational chatbot. Your main goal is to chat with the user and help them discover a movie they'll love.
Instead of waiting for direct questions, engage the user in a natural conversation. Ask indirect, open-ended questions to understand what they might be feeling or looking for.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question. This should be a friendly and conversational response.

Previous conversation history:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(prompt_template)

# Create the agent and executor
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


# --- API Endpoints ---
class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/")
def read_root():
    return {"message": "CineVerse AI Backend is running."}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    chat_history = chat_histories.get(request.session_id, [])
    response = await agent_executor.ainvoke({
        "input": request.message,
        "chat_history": chat_history,
    })
    output = response.get('output', "I'm sorry, I encountered an issue.")
    chat_history.extend([
        HumanMessage(content=request.message),
        AIMessage(content=output),
    ])
    chat_histories[request.session_id] = chat_history
    return {"sender": "bot", "message": output}


# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting CineVerse AI server on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)