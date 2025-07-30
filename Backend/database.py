from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read the database URL from your .env file
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Updated User Model ---
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
    print("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully.")

if __name__ == "__main__":
    create_db_and_tables()