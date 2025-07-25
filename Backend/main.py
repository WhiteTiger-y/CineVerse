import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pathlib import Path
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import Tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

# Local imports for authentication and database
from . import crud, schemas, security, database
from .database import SessionLocal

# Load environment variables from the .env file in the same directory as this script
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- Get API Key and validate ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.", file=sys.stderr)
    print(f"Please ensure a .env file exists at '{dotenv_path}' with your GOOGLE_API_KEY.", file=sys.stderr)
    sys.exit(1)


# --- Create Database Tables ---
# This line creates the 'users' and 'suggested_movies' tables if they don't exist
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


# --- Authentication Endpoints ---

@app.post("/signup", response_model=schemas.User)
def signup_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Creates a new user in the database."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/login")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Logs in a user and returns their ID."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not security.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"message": "Login successful", "user_id": db_user.id, "email": db_user.email}

@app.post("/check-email")
def check_user_email(request: schemas.EmailCheck, db: Session = Depends(get_db)):
    """Checks if a user with the given email already exists."""
    db_user = crud.get_user_by_email(db, email=request.email)
    if db_user:
        return {"exists": True}
    return {"exists": False}
# --- LangChain Agent Setup ---

# Configuration
FAISS_INDEX_PATH = "movie_faiss_index"

# In-memory store for conversation histories (to be replaced by DB later)
chat_histories = {}

# Initialize Models and Vector Store
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.4)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

# Check if the vector store index exists before loading
if not os.path.isdir(FAISS_INDEX_PATH):
    print(f"Error: FAISS index not found at '{os.path.abspath(FAISS_INDEX_PATH)}'.", file=sys.stderr)
    print("Please run 'create_vectorstore.py' first to generate the index.", file=sys.stderr)
    sys.exit(1)

# Load the local FAISS vector store
print(f"Loading FAISS index from '{FAISS_INDEX_PATH}'...")
vector_store = FAISS.load_local(
    FAISS_INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = vector_store.as_retriever()
print("FAISS index loaded successfully.")

# Define Agent Tools
retriever_tool = create_retriever_tool(
    retriever,
    "movie_database_search",
    "Searches and returns information about movies from a database."
)

def scrape_webpage(url: str) -> str:
    """Takes a URL and returns the text content of the webpage."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        loader = WebBaseLoader(url, requests_kwargs={"headers": headers})
        docs = loader.load()
        return "".join(doc.page_content for doc in docs)
    except Exception as e:
        return f"Error scraping website: {e}"

web_scraper_tool = Tool(
    name="web_scraper_tool",
    func=scrape_webpage,
    description="A tool to scrape a single webpage. Use for very recent movies."
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

# --- Chat Endpoint ---

class ChatRequest(BaseModel):
    message: str
    session_id: str # We'll replace this with user_id later

@app.get("/")
def read_root():
    return {"message": "CineVerse AI Backend is running."}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    """Handles incoming chat requests by invoking the agent."""
    print(f"Received message: '{request.message}' for session: {request.session_id}")

    chat_history = chat_histories.get(request.session_id, [])

    response = await agent_executor.ainvoke({
        "input": request.message,
        "chat_history": chat_history,
    })

    output = response.get('output', "I'm sorry, I encountered an issue and can't respond right now.")

    chat_history.extend([
        HumanMessage(content=request.message),
        AIMessage(content=output),
    ])
    chat_histories[request.session_id] = chat_history

    return {"sender": "bot", "message": output}