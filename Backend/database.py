import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# --- THIS IS THE UPDATED SECTION ---
# Find the absolute path to the .env file and load it
# This ensures it's found regardless of where you run the script from
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BACKEND_DIR, '.env')
load_dotenv(dotenv_path=dotenv_path)
# ------------------------------------

# This line will now work because the .env file has been loaded
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")



engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Define Database Models (Tables) ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True) # Optional field
    mobile_no = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    suggested_movies = relationship("SuggestedMovie", back_populates="owner")

class SuggestedMovie(Base):
    __tablename__ = "suggested_movies"

    id = Column(Integer, primary_key=True, index=True)
    movie_title = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="suggested_movies")


def create_db_and_tables():
    """A helper function to create the database file and all defined tables."""
    print("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully.")

# This part allows you to run `python backend/database.py` once to create the database
if __name__ == "__main__":
    create_db_and_tables()