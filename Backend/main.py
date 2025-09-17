import os
import boto3
import sys

# --- THIS IS THE CRUCIAL PATHING FIX FOR DEPLOYMENT ---
# This block makes your application's imports work reliably on any server.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
# ----------------------------------------------------

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import List
from huggingface_hub import InferenceClient

# LangChain Imports
from langchain_core.embeddings import Embeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.tools import Tool
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

# --- Load Environment Variables ---
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Local Imports (now absolute from the project root) ---
from Backend import crud, schemas, security, database, email_utils
from Backend.database import SessionLocal

# --- Custom Hugging Face Embeddings Class (using huggingface_hub) ---
class CustomHuggingFaceHubEmbeddings(Embeddings):
    def __init__(self, api_key: str, model_name: str):
        self.client = InferenceClient(token=api_key)
        self.model_name = model_name

    def _embed(self, texts: List[str]) -> List[List[float]]:
        response = self.client.feature_extraction(
            texts,
            model=self.model_name
        )
        return response.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]

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

# Static uploads dir
UPLOAD_DIR = os.path.join(current_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Auth dependency ---
def get_current_user(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    payload = security.verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload

# --- Authentication and User Endpoints ---

@app.post("/signup", response_model=schemas.User)
def signup_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Basic password policy
    msg = security.validate_password_policy(user.password)
    if msg:
        raise HTTPException(status_code=400, detail=msg)
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_mobile = crud.get_user_by_mobile(db, mobile_no=user.mobile_no)
    if db_user_by_mobile:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    # Unique username generator derived from email local-part
    base_username = user.email.split('@')[0]
    username = base_username
    suffix = 0
    while crud.get_user_by_username(db, username=username):
        suffix += 1
        username = f"{base_username}{suffix}"

    # Generate OTP
    import random, datetime
    otp_code = f"{random.randint(0, 999999):06d}"
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    new_user = crud.create_user(db=db, user=user, override_username=username)
    # Save OTP fields
    new_user.otp_code = otp_code
    new_user.otp_expires_at = expires
    new_user.is_verified = False
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # send welcome + otp
    email_utils.send_welcome_email(
        to_email=new_user.email,
        first_name=new_user.first_name,
        username=new_user.username,
        otp_code=otp_code,
    )
    # Also send a separate OTP email for redundancy (optional)
    try:
        email_utils.send_otp_email(new_user.email, new_user.first_name, otp_code)
    except Exception:
        pass
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
    
    # Require verification
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified. Please enter the OTP sent to your email.")

    # Issue JWT access token
    access_token = security.create_access_token(user_id=db_user.id, username=db_user.username, email=db_user.email)
    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "email": db_user.email,
        "username": db_user.username,
        "access_token": access_token,
    }

@app.post("/verify-otp")
def verify_otp(body: schemas.VerifyOtpRequest, db: Session = Depends(get_db)):
    # Allow using email or username as identifier
    user = crud.get_user_by_email(db, email=body.identifier) or crud.get_user_by_username(db, username=body.identifier)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    import datetime
    if not user.otp_code or user.otp_code != body.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    if not user.otp_expires_at or datetime.datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Account verified successfully."}

@app.post("/resend-otp")
def resend_otp(body: schemas.ResendOtpRequest, db: Session = Depends(get_db)):
    # Redis-based throttle: max 5 per hour per identifier
    from Backend import security
    throttle_key = f"otp:resend:{body.identifier}"
    if not security.rate_limit_ok(throttle_key, max_requests=5, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Too many OTP requests. Please wait before trying again.")
    user = crud.get_user_by_email(db, email=body.identifier) or crud.get_user_by_username(db, username=body.identifier)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    import random, datetime
    otp_code = f"{random.randint(0, 999999):06d}"
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    user.otp_code = otp_code
    user.otp_expires_at = expires
    db.add(user)
    db.commit()
    db.refresh(user)
    email_utils.send_otp_email(user.email, user.first_name, otp_code)
    return {"message": "OTP resent."}

@app.post("/account/profile-pic/upload", response_model=schemas.User)
def upload_profile_pic(file: UploadFile = File(...), db: Session = Depends(get_db), current=Depends(get_current_user)):
    user_id = int(current.get('sub'))
    filename = f"user_{user_id}_{int(__import__('time').time())}_{file.filename}"
    # S3 config
    bucket = os.getenv("AWS_S3_BUCKET")
    region = os.getenv("AWS_S3_REGION")
    if bucket and region:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region,
        )
        s3.upload_fileobj(file.file, bucket, filename, ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})
        public_url = f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"
        # Optionally: presigned = s3.generate_presigned_url(...)
    else:
        dest_path = os.path.join(UPLOAD_DIR, filename)
        with open(dest_path, 'wb') as f:
            f.write(file.file.read())
        public_url = f"/uploads/{filename}"
    return crud.update_profile_pic_url(db=db, user_id=user_id, url=public_url)

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
def update_user_username(request: schemas.UsernameUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if request.user_id != int(current.get("sub")):
        raise HTTPException(status_code=403, detail="Not allowed")
    existing_user = crud.get_user_by_username(db, username=request.new_username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already taken.")
    return crud.update_username(db=db, user_id=request.user_id, new_username=request.new_username)

@app.put("/account/password")
def update_user_password_route(request: schemas.PasswordUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if request.user_id != int(current.get("sub")):
        raise HTTPException(status_code=403, detail="Not allowed")
    # Policy check
    msg = security.validate_password_policy(request.new_password)
    if msg:
        raise HTTPException(status_code=400, detail=msg)
    user = crud.get_user_by_id(db, user_id=request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not security.verify_password(request.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password.")
    crud.update_user_password(db=db, user=user, new_password=request.new_password)
    return {"message": "Password updated successfully."}

@app.put("/account/profile-pic", response_model=schemas.User)
def update_user_profile_pic(request: schemas.ProfilePicUpdate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if request.user_id != int(current.get("sub")):
        raise HTTPException(status_code=403, detail="Not allowed")
    return crud.update_profile_pic_url(db=db, user_id=request.user_id, url=request.url)


# --- LangChain Agent Setup ---
INDEX_NAME = "cineverse-ai"
NAMESPACE = "movies"
chat_histories = {} 

# Initialize Models
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)

# Initialize Custom Embedding Model
embeddings = CustomHuggingFaceHubEmbeddings(
    api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Connect to the existing Pinecone index
print(f"Connecting to Pinecone index '{INDEX_NAME}'...")
vector_store = PineconeVectorStore.from_existing_index(
    index_name=INDEX_NAME,
    embedding=embeddings,
    namespace=NAMESPACE
)
retriever = vector_store.as_retriever()
print(f"Successfully connected to Pinecone, using namespace '{NAMESPACE}'.")

# Define Agent Tools
retriever_tool = create_retriever_tool(
    retriever,
    "movie_database_search",
    "Searches and returns information about movies from a database."
)

def scrape_webpage(url: str) -> str:
    try:
        headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36" }
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
You are CineVerse AI, a friendly, empathetic, and highly conversational movie chatbot.
Your top priority is to make the user feel heard and understood. Start each conversation by gently asking about their day or mood, and use their responses to guide your tone and recommendations. Do not immediately ask for movie names or preferences—focus on building rapport and understanding how they're feeling first.

Always reply in a concise, back-and-forth style, as if chatting with a friend. Avoid long paragraphs—keep answers short, clear, and engaging. Use markdown for formatting (e.g., **bold**, *italics*, lists, and code blocks for movie recommendations or examples). If the user asks for a list, use bullet points or tables. If you don't know, say so honestly.

If the user shares their mood or something about their day, acknowledge it and adapt your suggestions accordingly. For example, if they're tired, suggest relaxing movies; if they're excited, suggest something fun or adventurous. If they seem sad, be extra supportive and offer uplifting or comforting recommendations.

**When you recommend a movie, always try to provide a direct link to watch it on an OTT streaming platform (like Netflix, Prime Video, Disney+, etc.) if available. If you can't find an OTT link, provide the IMDb link for the movie instead. Format these links clearly in your markdown reply.**

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
Final Answer: the final answer to the original input question. Format your answer using markdown for readability and friendliness.

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def handle_chat(request: ChatRequest, db: Session = Depends(get_db), current=Depends(get_current_user), x_forwarded_for: str | None = Header(default=None)):
    # Rate limiting per user
    rl_key = f"chat:{current.get('sub')}"
    if not security.rate_limit_ok(rl_key, max_requests=30, window_seconds=60):
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")

    # Load recent chat history from DB (last 20 messages)
    from Backend.database import ChatMessage
    history_rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == request.session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    chat_history = []
    for row in history_rows[-40:]:
        if row.sender == 'user':
            chat_history.append(HumanMessage(content=row.message))
        else:
            chat_history.append(AIMessage(content=row.message))

    response = await agent_executor.ainvoke({
        "input": request.message,
        "chat_history": chat_history,
    })
    output = response.get('output', "I'm sorry, I encountered an issue.")

    # Persist both user and bot messages
    db.add(ChatMessage(session_id=request.session_id, user_id=int(current.get('sub')), sender='user', message=request.message))
    db.add(ChatMessage(session_id=request.session_id, user_id=int(current.get('sub')), sender='bot', message=output))
    db.commit()

    return {"sender": "bot", "message": output}


# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting CineVerse AI server on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
