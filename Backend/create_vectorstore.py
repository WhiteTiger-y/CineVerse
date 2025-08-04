import os
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.docstore.document import Document
from dotenv import load_dotenv

# --- Load Environment Variables ---
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(BACKEND_DIR)
dotenv_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Pinecone and Data Configuration ---
INDEX_NAME = "cineverse-movies" 

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
csv_file_path = os.path.join(PROJECT_ROOT_DIR, 'your_movie_dataset.csv')

# --- Data Loading and Processing ---
print(f"Loading data from {csv_file_path}...")
df = pd.read_csv(csv_file_path, usecols=list(column_mapping.values()), low_memory=False)
df.dropna(subset=[column_mapping["description"]], inplace=True)
df = df.head(63510)
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

# --- Initialize Hugging Face Embedding Model ---
print("Initializing Hugging Face embeddings model...")
model_name = "microsoft/multilingual-e5-large"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# --- Upload to Pinecone ---
print(f"Uploading {len(documents)} documents to Pinecone index '{INDEX_NAME}'... (This may take a while the first time as the model downloads)")
PineconeVectorStore.from_documents(documents, embeddings, index_name=INDEX_NAME)

print(f"\nVector store populated in Pinecone index '{INDEX_NAME}' successfully.")