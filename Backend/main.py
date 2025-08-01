import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
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

@app.post("/check-email")
def check_user_email(request: schemas.EmailCheck, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=request.email)
    if db_user:
        return {"exists": True}
    return {"exists": False}

# --- Add this new endpoint ---
@app.post("/check-mobile")
def check_user_mobile(request: schemas.MobileCheck, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_mobile(db, mobile_no=request.mobile_no)
    if db_user:
        return {"exists": True}
    return {"exists": False}

@app.post("/signup", response_model=schemas.User)
def signup_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_mobile = crud.get_user_by_mobile(db, mobile_no=user.mobile_no)
    if db_user_by_mobile:
        raise HTTPException(status_code=400, detail="Mobile number already registered")

    new_user = crud.create_user(db=db, user=user)
    
    # Send welcome email after user is created
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


# --- LangChain Agent Setup ---
PROJECT_ROOT_DIR = os.path.dirname(BACKEND_DIR)
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT_DIR, "movie_faiss_index")
chat_histories = {} # Temporary in-memory history

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.4, convert_system_message_to_human=True)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

if not os.path.isdir(FAISS_INDEX_PATH):
    print(f"Error: FAISS index not found at '{FAISS_INDEX_PATH}'.", file=sys.stderr)
    sys.exit(1)

print(f"Loading FAISS index from '{FAISS_INDEX_PATH}'...")
vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever()
print("FAISS index loaded successfully.")

# ... (Your agent and tools setup remains here)

# --- Chat Endpoint ---
class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/")
def read_root():
    return {"message": "CineVerse AI Backend is running."}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    # This logic will be updated later to use the database for history
    chat_history = chat_histories.get(request.session_id, [])
    # ... (Your agent invocation logic remains here)

# --- Main Entry Point to Run the App ---
if __name__ == "__main__":
    print("Starting CineVerse AI server on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)