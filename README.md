Of course. Based on all the incredible features you've built, here is a complete and descriptive `README.md` file that you can use for your GitHub repository.

This captures the current state of your project, from the full-stack architecture to the advanced AI and authentication systems, and outlines the exciting future you have planned for it.

-----

# 🎬 CineVerse AI

> Current Version: 0.5.0 (Alpha Phase)

[](https://nextjs.org/)
[](https://fastapi.tiangolo.com/)
[](https://www.langchain.com/)
[](https://www.google.com/search?q=https://ai.google/discover/gemini/)
[](https://www.pinecone.io/)
[](https://supabase.com/)

> An intelligent, conversational movie recommendation engine powered by Google Gemini and LangChain, featuring a complete user authentication system and a sleek, modern UI.

*(**Note:** Replace this URL with a new screenshot of your live app\!)*

-----

## 🤖 About The Project

CineVerse AI is a full-stack web application that redefines the movie discovery experience. Instead of simple keyword searches, it functions as a conversational partner, engaging users with friendly, indirect questions to understand their mood and preferences. Powered by a sophisticated LangChain agent using Google's Gemini, it provides tailored movie suggestions that truly resonate with the user's current state of mind.

The project features a complete user authentication system, a futuristic "glassmorphism" UI built with React and Tailwind CSS, and an intelligent backend that can search both a static knowledge base and the live web for recommendations.

-----

## ✨ Key Features

### User Authentication & Security

  - **Secure User Signup:** Comprehensive registration with fields for first name, last name, mobile number, email, and password.
  - **Flexible Login:** Users can log in with either their unique username or their email address.
  - **Live Validation:** Real-time checks on the signup form to prevent duplicate emails or mobile numbers.
  - **Complete Password Reset Flow:** "Forgot Password" functionality that sends a secure, time-sensitive reset link via email.
  - **Welcome Emails:** New users automatically receive a welcome email with their details upon registration.
  - **Account Management:** A dedicated, protected page for logged-in users to change their username and password.

### AI Core & Functionality

  - **Conversational AI Agent:** Powered by **Google Gemini** and orchestrated with **LangChain** to provide natural, empathetic, and intelligent conversation.
  - **Dual-Tool System:**
      - **Semantic Search:** Uses a **Pinecone** vector database to perform semantic searches on a knowledge base of nearly 1 million movies.
      - **Live Web Scraping:** Can access websites like IMDb in real-time to fetch information on the very latest movie releases.

### Frontend Experience

  - **Modern UI/UX:** A high-fidelity "glassmorphism" UI built with **Next.js** and styled with **Tailwind CSS**.
  - **Rich Animations:** Smooth page transitions and satisfying micro-interactions powered by **Framer Motion**.
  - **Protected Routes:** The core chat and account pages are only accessible to authenticated users.
  - **Persistent Session:** Remembers the user's login status and chat history across page refreshes using `localStorage`.

-----

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | React, Next.js, Tailwind CSS, Framer Motion |
| **Backend** | Python, FastAPI |
| **AI/LLM** | LangChain, Google Gemini |
| **Database** | PostgreSQL (via Supabase), SQLAlchemy |
| **Vector Store**| Pinecone |
| **Email Service** | Brevo |
| **Security** | Passlib (for password hashing), Itsdangerous (for tokens) |

-----

## 🚀 Getting Started

To get a local copy up and running, follow these steps.

### Prerequisites

  - Node.js (v18 or later)
  - Python (v3.10 or later)

### Installation

1.  **Clone the Repository**

    ```sh
    git clone https://your-github-repo-url.com/CineVerse-Project.git
    cd CineVerse-Project
    ```

2.  **Backend Setup**

    ```sh
    # Navigate to the backend directory
    cd backend

    # Create and activate a virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

    # Install Python packages from requirements.txt
    pip install -r requirements.txt

    # Create the .env file for your secrets and add your keys
    ```

    Your `backend/.env` file must contain:

    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    DATABASE_URL="YOUR_SUPABASE_POSTGRES_URL_(Transaction_Pooler)"
    PINECONE_API_KEY="YOUR_PINECONE_API_KEY"
    HUGGINGFACEHUB_API_TOKEN="YOUR_HUGGINGFACE_READ_TOKEN"
    SECRET_KEY="A_LONG_RANDOM_SECRET_STRING_FOR_TOKENS"
    BREVO_API_KEY="YOUR_BREVO_API_KEY"
    SENDER_EMAIL="YOUR_VERIFIED_SENDER_EMAIL"
    ```

    ```sh
    # Run one-time setup scripts
    # 1. Create the tables on your cloud database
    python database.py

    # 2. Build the movie vector store (this can take a long time)
    python create_vectorstore.py

    # Run the backend server (from the main project root directory)
    cd .. 
    uvicorn backend.main:app --reload
    ```

3.  **Frontend Setup**

    ```sh
    # In a new terminal, navigate to the frontend directory
    cd frontend

    # Install dependencies
    npm install

    # Create the .env.local file for your frontend
    ```

    Your `frontend/.env.local` file must contain:

    ```env
    NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
    ```

    ```sh
    # Run the frontend development server
    npm run dev
    ```

    Your application will be live at `http://localhost:3000`.

-----

## 🗺️ Roadmap & Future Features

  - **Live Deployment (In Progress)**

      - The application is being deployed to a cloud platform like **Render**, making it live and accessible.

  - **Version 2.0: Enhanced Account Management**

      - **Profile Picture Setup:** Allow users to upload and display a profile picture using Supabase Storage.

  - **Version 3.0: Advanced AI & Memory**

      - **Database-Backed Chat History:** Store conversations in the database for a persistent, multi-device experience.
      - **Long-Term Movie Memory:** The agent will use the database to remember all movies suggested to a specific user to avoid repeats.
      - **Facial Expression Reader:** Integrate a custom ML model to analyze a user's live webcam feed for an even deeper understanding of their mood.
