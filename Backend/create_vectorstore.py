import os
import sys
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables from the .env file in the same directory as this script
dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# --- Get API Key and validate ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables.", file=sys.stderr)
    print(f"Please ensure a .env file exists at '{dotenv_path}' with your GOOGLE_API_KEY.", file=sys.stderr)
    sys.exit(1)

def create_vector_store(csv_path: str, index_name: str, chunk_size: int = 5000):
    """Loads data from a CSV, creates embeddings, and saves them to a FAISS vector store."""
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
    # --------------------

    print(f"Loading data from '{csv_path}'...")
    try:
        # Load only the columns we need to save memory
        df = pd.read_csv(csv_path, usecols=list(column_mapping.values()), low_memory=False)
    except FileNotFoundError:
        print(f"Error: The file '{csv_path}' was not found. Make sure it's in the correct directory.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Mismatch between CSV columns and column_mapping. Please check your CSV file. Details: {e}", file=sys.stderr)
        sys.exit(1)

    # Drop rows where the main description is missing
    df.dropna(subset=[column_mapping["description"]], inplace=True)

    # Using a smaller subset for faster processing. Increase this number for your final build.
    df = df.head(chunk_size)
    print(f"Processing {len(df)} movies...")

    # Create LangChain Document objects
    documents = []
    for _, row in df.iterrows():
        # Combine the most descriptive text fields for semantic search
        page_content = (
            f"Title: {row.get(column_mapping['title'], 'N/A')}\n"
            f"Genres: {row.get(column_mapping['genres'], 'N/A')}\n"
            f"Description: {row.get(column_mapping['description'], 'N/A')}"
        )
        
        # Store all the structured data in metadata
        metadata = {key: row.get(val, None) for key, val in column_mapping.items()}
        
        documents.append(Document(page_content=page_content, metadata=metadata))

    # Initialize Gemini embeddings model
    print("Initializing embeddings model...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

    # Create the FAISS vector store from the documents
    print("Creating vector store... (This may take a few minutes)")
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save the vector store locally
    vector_store.save_local(index_name)

    print(f"\nVector store created successfully in '{index_name}' folder.")

if __name__ == "__main__":
    # This script should be run from the project's root directory.
    # e.g., python Backend/create_vectorstore.py
    
    # Make sure to replace 'your_movie_dataset.csv' with the actual filename
    # and ensure it is located in the 'Backend' directory.
    csv_file = os.path.join("Backend", "final_dataset.csv")
    
    # The index will be created in the project root, where main.py expects it.
    index_folder = "movie_faiss_index"
    
    create_vector_store(csv_path=csv_file, index_name=index_folder)