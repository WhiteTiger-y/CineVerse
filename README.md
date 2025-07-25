-----

# 🎬 CineVerse AI

> A smart, conversational movie recommender powered by Google Gemini and LangChain.


-----

## 🤖 About The Project

CineVerse AI is more than just a search engine for movies; it's a conversational partner designed to help you find the perfect film. It goes beyond simple genre or title searches by engaging in natural conversation to understand your mood and preferences. By analyzing the nuances of the chat, it suggests movies that you're truly in the mood for.

The project features a sleek, modern UI with a futuristic purple-and-black theme, complete with smooth animations and a 3D "floating" interface.

-----

## ✨ Key Features

  * **Conversational AI:** Powered by Google's Gemini Pro, the agent can hold natural, friendly conversations.
  * **Semantic Movie Search:** Utilizes a FAISS vector database to find movies based on plot, theme, and mood, not just keywords.
  * **Live Web Access:** Can access live websites (like IMDb) to fetch information on the very latest movie releases.
  * **Persistent Chat History:** Remembers your current conversation even if you refresh the page, using the browser's `localStorage`.
  * **Stylish & Animated UI:** A custom-built React frontend with Tailwind CSS and Framer Motion for a fluid and engaging user experience.

-----

## 🛠️ Tech Stack

This project is a full-stack application composed of a Python backend and a React frontend.

**Backend:**

  * **Framework:** FastAPI
  * **AI/LLM Orchestration:** LangChain
  * **LLM:** Google Gemini Pro
  * **Embeddings & Vector DB:** Google Generative AI Embeddings & FAISS
  * **Web Scraping:** BeautifulSoup4

**Frontend:**

  * **Framework:** React & Next.js
  * **Styling:** Tailwind CSS
  * **Animations:** Framer Motion

-----

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

  * Node.js and npm installed
  * Python 3.9+ and pip installed

### Installation

1.  **Clone the repo**

    ```sh
    git clone https://your-github-repo-url.com/CineVerse-Project.git
    cd CineVerse-Project
    ```

2.  **Setup the Backend**

    ```sh
    cd backend

    # Create a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

    # Create a requirements.txt file (if you haven't already)
    pip freeze > requirements.txt

    # Install Python packages
    pip install -r requirements.txt

    # Create a .env file and add your Google API Key
    echo 'GOOGLE_API_KEY="YOUR_API_KEY"' > .env

    # Build the movie knowledge base
    python create_vectorstore.py

    # Run the backend server
    uvicorn main:app --reload
    ```

3.  **Setup the Frontend**

    ```sh
    # In a new terminal, navigate to the frontend directory
    cd frontend

    # Install NPM packages
    npm install

    # Run the frontend dev server
    npm run dev
    ```

Your app will be available at `http://localhost:3000`.

-----

## 🗺️ Roadmap & Future Features

This is just the beginning\! Here are the exciting features planned for the next version:

  * **Vercel Deployment (Coming Soon\!)**

      * The application will be deployed to Vercel, making it live and accessible to anyone with a link.

  * **Version 2.0: Full User Authentication**

      * **User Accounts:** A complete signup and login system where users can create their own accounts with an email and password.
      * **Personalized History:** Chat history and movie suggestions will be tied to individual user accounts, creating a truly personalized experience.
      * **Long-Term Memory:** The agent will remember all movies suggested to a specific user (up to 50) to avoid recommending the same film twice.

-----
