import os
import pandas as pd
from langchain_huggingface import HuggingFaceInferenceAPIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.docstore.document import Document
from dotenv import load_dotenv
from tqdm import tqdm
import torch

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
# Assuming your CSV is in the Backend folder
csv_file_path = os.path.join(BACKEND_DIR, 'final_dataset.csv') 

# --- Data Loading and Processing ---
print(f"Loading data from {csv_file_path}...")
df = pd.read_csv(csv_file_path, usecols=list(column_mapping.values()), low_memory=False)
df.dropna(subset=[column_mapping["description"]], inplace=True)
print(f"Loaded {len(df)} movies, now cleaning data...")

# --- Data Cleaning Section ---
df[column_mapping['rating']] = df[column_mapping['rating']].fillna(0.0)
text_cols = [
    column_mapping['title'], 
    column_mapping['genres'], 
    column_mapping['languages'], 
    column_mapping['release_date'],
    column_mapping['duration'],
    column_mapping['year']
]
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].fillna('')

df = df.head(64000)
print(f"Processing {len(df)} cleaned movies...")

documents = []
for _, row in df.iterrows():
    page_content = (
        f"Title: {row[column_mapping['title']]}\n"
        f"Genres: {row[column_mapping['genres']]}\n"
        f"Description: {row[column_mapping['description']]}"
    )
    metadata = {
        "title": str(row[column_mapping['title']]),
        "year": str(row[column_mapping['year']]),
        "duration": str(row[column_mapping['duration']]),
        "rating": float(row[column_mapping['rating']]),
        "genres": str(row[column_mapping['genres']]),
        "languages": str(row[column_mapping['languages']]),
        "release_date": str(row[column_mapping['release_date']])
    }
    documents.append(Document(page_content=page_content, metadata=metadata))

# --- Initialize Hugging Face Embedding Model ---
print("Initializing Hugging Face embeddings model...")

# Auto-detect and select the best available device (GPU or CPU)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    model_name="intfloat/multilingual-e5-large"
)

# --- Upload to Pinecone in Batches ---
print(f"Uploading {len(documents)} documents to Pinecone index '{INDEX_NAME}'...")

batch_size = 500
index = PineconeVectorStore.from_existing_index(INDEX_NAME, embeddings)

for i in tqdm(range(0, len(documents), batch_size)):
    batch = documents[i:i + batch_size]
    index.add_documents(batch)

print(f"\nVector store populated in Pinecone index '{INDEX_NAME}' successfully.")