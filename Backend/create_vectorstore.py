import os
import pandas as pd
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from dotenv import load_dotenv
from tqdm import tqdm
from typing import List
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError  # Import the specific error
import time  # Import the time module for waiting

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
        # The API now returns a list of floats directly, ensure it's a list
        if isinstance(response, list) and all(isinstance(r, list) for r in response):
            return response
        # Handle older versions or unexpected formats by converting
        return response.tolist()


    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]

# --- Custom Hugging Face Embeddings Class ---
# This lightweight class uses the Hugging Face API without heavy local libraries
class CustomHuggingFaceInferenceAPIEmbeddings(Embeddings):
    """Lightweight embedding client for HF Inference API.
    Uses E5-style prefixes for better retrieval performance.
    """
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
            raise Exception(
                f"HuggingFace API request failed with status {response.status_code}: {response.text}"
            )
        return response.json()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # E5 family expects 'passage: ' prefix for documents
        texts_with_prefix = [f"passage: {t}" for t in texts]
        return self._embed(texts_with_prefix)

    def embed_query(self, text: str) -> List[float]:
        # E5 family expects 'query: ' prefix for queries
        return self._embed([f"query: {text}"])[0]

# --- Load Environment Variables ---
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(BACKEND_DIR)
dotenv_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Pinecone and Data Configuration ---
INDEX_NAME = "cineverse-ai"
NAMESPACE = "movies"

# Update these keys to match the exact column names in your CSV file
column_mapping = {
    "id": "id",
    "title": "title",
    "vote_average": "vote_average",
    "runtime": "runtime",
    "adult": "adult",
    "imdb_id": "imdb_id",
    "original_language": "original_language",
    "original_title": "original_title",
    "overview": "overview",
    "popularity": "popularity",
    "tagline": "tagline",
    "genres": "genres",
    "production_countries": "production_countries",
    "spoken_languages": "spoken_languages",
    "keywords": "keywords",
    "release_date": "release_date"
}
<<<<<<< HEAD
csv_file_path = os.path.join(BACKEND_DIR, 'final_dataset.csv') 
=======
csv_file_path = os.path.join(BACKEND_DIR, 'TMDB_movie_dataset_v11.csv')
>>>>>>> dedfcda47342541d21af8d7cc8127b613139501c

# --- Data Loading and Processing ---
print(f"Loading data from {csv_file_path}...")
df = pd.read_csv(csv_file_path, usecols=list(column_mapping.values()), low_memory=False)
df.dropna(subset=[column_mapping["overview"]], inplace=True)
print(f"Loaded {len(df)} movies, now cleaning and filtering data...")

# --- Data Cleaning Section ---
for col_key, col_name in column_mapping.items():
    if df[col_name].dtype == 'object':
        df[col_name] = df[col_name].fillna('')
    else:
        df[col_name] = df[col_name].fillna(0)

# --- THIS IS THE NEW DATA FILTERING SECTION ---
# Convert release_date to datetime objects, coercing errors
release_date_col = column_mapping['release_date']
df[release_date_col] = pd.to_datetime(df[release_date_col], errors='coerce')

# Drop rows where the date could not be parsed
df.dropna(subset=[release_date_col], inplace=True)

# Filter the DataFrame to keep only movies between 1980 and 2025
df = df[
    (df[release_date_col].dt.year >= 1980) &
    (df[release_date_col].dt.year <= 2025)
]
# ---------------------------------------------

<<<<<<< HEAD
# Limit to a subset for testing, you can remove .head() for the full dataset
df = df.head(64000) 
print(f"Processing {len(df)} cleaned movies...")
=======
print(f"Processing {len(df)} cleaned and filtered movies...")
>>>>>>> dedfcda47342541d21af8d7cc8127b613139501c

# Create LangChain Document objects
documents = []
for _, row in df.iterrows():
    page_content = (
        f"Title: {row[column_mapping['title']]}\n"
        f"Tagline: {row[column_mapping['tagline']]}\n"
        f"Genres: {row[column_mapping['genres']]}\n"
        f"Keywords: {row[column_mapping['keywords']]}\n"
        f"Overview: {row[column_mapping['overview']]}"
    )
    metadata = {
        "id": str(row[column_mapping['id']]),
        "title": str(row[column_mapping['title']]),
        "vote_average": float(row[column_mapping['vote_average']]),
        "runtime": float(row[column_mapping['runtime']]),
        "adult": str(row[column_mapping['adult']]),
        "imdb_id": str(row[column_mapping['imdb_id']]),
        "original_language": str(row[column_mapping['original_language']]),
        "original_title": str(row[column_mapping['original_title']]),
        "popularity": float(row[column_mapping['popularity']]),
        "tagline": str(row[column_mapping['tagline']]),
        "genres": str(row[column_mapping['genres']]),
        "production_countries": str(row[column_mapping['production_countries']]),
        "spoken_languages": str(row[column_mapping['spoken_languages']]),
        "keywords": str(row[column_mapping['keywords']]),
        "release_date": str(row[column_mapping['release_date']].strftime('%Y-%m-%d'))
    }
    documents.append(Document(page_content=page_content, metadata=metadata))

# --- Initialize Hugging Face Embedding Model ---
<<<<<<< HEAD
print("Initializing Custom Hugging Face embeddings via API...")
embeddings = CustomHuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    # Use the same model as runtime for consistency
    model_name="intfloat/multilingual-e5-large"
=======
print("Initializing Hugging Face embeddings via official client...")
embeddings = CustomHuggingFaceHubEmbeddings(
    api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
>>>>>>> dedfcda47342541d21af8d7cc8127b613139501c
)

# --- Upload to Pinecone in Batches with Retry Logic ---
print(f"Uploading {len(documents)} documents to Pinecone index '{INDEX_NAME}' in namespace '{NAMESPACE}'...")

batch_size = 100
index = PineconeVectorStore.from_existing_index(INDEX_NAME, embeddings)

for i in tqdm(range(0, len(documents), batch_size), desc="Uploading Batches"):
    batch = documents[i:i + batch_size]
    
    # === NEW: RETRY LOGIC BLOCK ===
    max_retries = 10
    for attempt in range(max_retries):
        try:
            # Attempt to add the documents
            index.add_documents(batch, namespace=NAMESPACE)
            # If successful, break the loop for this batch
            break
        except HfHubHTTPError as e:
            # Check if the error is a server-side issue (5xx)
            if e.response.status_code >= 500:
                if attempt < max_retries - 1:
                    # Wait for an exponentially increasing amount of time
                    wait_time = 2 ** (attempt + 1)
                    print(f"  > Server error occurred. Waiting {wait_time} seconds before retry {attempt + 2}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    # If all retries fail, print an error and re-raise the exception
                    print(f"  > All {max_retries} retries failed for this batch. Aborting.")
                    raise
            else:
                # If it's a different client-side error (e.g., 4xx), don't retry and just raise it
                print(f"  > A non-server error occurred: {e}")
                raise
    # ============================

print(f"\nVector store populated in namespace '{NAMESPACE}' successfully.")
