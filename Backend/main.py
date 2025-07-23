import os
import sys
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
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

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
FAISS_INDEX_PATH = "movie_faiss_index"

# --- In-memory store for conversation histories ---
chat_histories = {}

# --- Initialize Models and Vector Store ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4, convert_system_message_to_human=True)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Check if the vector store index exists before loading
if not os.path.isdir(FAISS_INDEX_PATH):
    print(f"Error: FAISS index not found at '{os.path.abspath(FAISS_INDEX_PATH)}'.", file=sys.stderr)
    print("Please run 'Backend/create_vectorstore.py' first to generate the index.", file=sys.stderr)
    sys.exit(1)

# Load the local FAISS vector store
print(f"Loading FAISS index from '{FAISS_INDEX_PATH}'...")
vector_store = FAISS.load_local(
    FAISS_INDEX_PATH,
    embeddings,
    allow_dangerous_deserialization=True # Required for loading FAISS index
)
retriever = vector_store.as_retriever()
print("FAISS index loaded successfully.")


# --- Define Agent Tools ---

# 1. Movie Database Search Tool
retriever_tool = create_retriever_tool(
    retriever,
    "movie_database_search",
    "Searches and returns information about movies from a database. Use it to answer questions about movies, plots, or genres for films released before 2024."
)

# 2. Web Scraper Tool
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
    description="A tool to scrape a single webpage. Use this to get information on the very latest movies (e.g., from late 2024 onwards) or for movies not found in the database. Input should be a single URL."
)

tools = [retriever_tool, web_scraper_tool]


# --- Create the Agent ---

# This is the corrected prompt template with the required variables
prompt_template = """
You are CineVerse AI, a friendly, empathetic, and conversational chatbot. Your main goal is to chat with the user and help them discover a movie they'll love.
Instead of waiting for direct questions, engage the user in a natural conversation. Ask indirect, open-ended questions to understand what they might be feeling or looking for. For example, ask "How was your day?" or "Looking for something to lift your spirits or a deep story to dive into?". Analyze their response to infer their mood and taste.

Answer the following questions as best you can. You have access to the following tools:
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

# Create the agent
agent = create_react_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True, 
    handle_parsing_errors=True
)


# --- Create FastAPI App ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.get("/")
def read_root():
    return {"message": "CineVerse AI Backend is running. Please use the frontend to interact."}

@app.post("/chat")
async def handle_chat(request: ChatRequest):
    """Handles incoming chat requests by invoking the agent."""
    print(f"Received message: '{request.message}' for session: {request.session_id}")

    # Get or create chat history for the session
    chat_history = chat_histories.get(request.session_id, [])
    
    response = await agent_executor.ainvoke({
        "input": request.message,
        "chat_history": chat_history,
    })

    output = response.get('output', "I'm sorry, I encountered an issue and can't respond right now.")

    # Update the history with the new interaction
    chat_history.extend([
        HumanMessage(content=request.message),
        AIMessage(content=output),
    ])
    chat_histories[request.session_id] = chat_history

    return {"sender": "bot", "message": output}

# --- Add entry point to run the app ---
if __name__ == "__main__":
    print("Starting CineVerse AI server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)