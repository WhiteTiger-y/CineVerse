import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os

# --- THIS IS THE UPDATED PATH LOGIC ---
# Get the directory of the current script (backend)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (the main project root)
PROJECT_ROOT_DIR = os.path.dirname(BACKEND_DIR)
# Construct the path to the .env file inside the backend folder
dotenv_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)
# ------------------------------------

# --- Configuration ---
# Update these keys to match the exact column names in your CSV file
column_mapping = {
    "title": "title",
    "year": "year",
    "duration": "duration",
    "rating": "rating",
    "description": "description",
    "genres": "genres",
    "languages": "languages",
    "release_date": "release_date"
}
# Make sure your CSV file is in the main project folder
csv_file_path = os.path.join(PROJECT_ROOT_DIR, 'your_movie_dataset.csv')
# --------------------

print(f"Loading data from {csv_file_path}...")
df = pd.read_csv(csv_file_path, usecols=list(column_mapping.values()), low_memory=False)
df.dropna(subset=[column_mapping["description"]], inplace=True)
df = df.head(5000)
print(f"Processing {len(df)} movies...")

documents = []
for _, row in df.iterrows():
    page_content = (
        f"Title: {row[column_mapping['title']]}\n"
        f"Genres: {row[column_mapping['genres']]}\n"
        f"Description: {row[column_mapping['description']]}"
    )
    metadata = {
        "title": row[column_mapping['title']],
        "year": row[column_mapping['year']],
        "duration": row[column_mapping['duration']],
        "rating": row[column_mapping['rating']],
        "genres": row[column_mapping['genres']],
        "languages": row[column_mapping['languages']],
        "release_date": row[column_mapping['release_date']]
    }
    documents.append(Document(page_content=page_content, metadata=metadata))

print("Initializing embeddings model...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

print("Creating vector store... (This may take a few minutes)")
vector_store = FAISS.from_documents(documents, embeddings)

# --- SAVE TO THE CORRECT LOCATION ---
# Construct the full path to save the index in the main project folder
faiss_index_path_to_save = os.path.join(PROJECT_ROOT_DIR, "movie_faiss_index")
vector_store.save_local(faiss_index_path_to_save)
# ------------------------------------

print(f"\nVector store created and saved successfully in '{faiss_index_path_to_save}' folder.")