import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# IMPORTANT: Update these keys to match the exact column names in your CSV file
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
csv_file_path = 'your_movie_dataset.csv' # The name of your CSV file
# --------------------

print(f"Loading data from {csv_file_path}...")
# Load only the columns we need to save memory
df = pd.read_csv(csv_file_path, usecols=list(column_mapping.values()), low_memory=False)

# Drop rows where the main description is missing
df.dropna(subset=[column_mapping["description"]], inplace=True)

# Using a smaller subset for faster processing. Increase this number for your final build.
df = df.head(5000)
print(f"Processing {len(df)} movies...")

# Create LangChain Document objects
documents = []
for _, row in df.iterrows():
    # Combine the most descriptive text fields for semantic search
    page_content = (
        f"Title: {row[column_mapping['title']]}\n"
        f"Genres: {row[column_mapping['genres']]}\n"
        f"Description: {row[column_mapping['description']]}"
    )
    
    # Store all the structured data in metadata
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

# Initialize Gemini embeddings model
print("Initializing embeddings model...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Create the FAISS vector store from the documents
print("Creating vector store... (This may take a few minutes)")
vector_store = FAISS.from_documents(documents, embeddings)

# Save the vector store locally
vector_store.save_local("movie_faiss_index")

print("\nVector store updated successfully in 'movie_faiss_index' folder.")