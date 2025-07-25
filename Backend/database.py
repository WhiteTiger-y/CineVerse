from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# 1. Define the database file location
SQLALCHEMY_DATABASE_URL = "sqlite:///./cineverse.db"

# 2. Create the SQLAlchemy engine for database connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a session object to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base class for our declarative data models
Base = declarative_base()


# --- Define Database Models (Tables) ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # This creates a link between a User and their suggested movies
    suggested_movies = relationship("SuggestedMovie", back_populates="owner")

class SuggestedMovie(Base):
    __tablename__ = "suggested_movies"

    id = Column(Integer, primary_key=True, index=True)
    movie_title = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # This creates a link back to the User who owns the suggestion
    owner = relationship("User", back_populates="suggested_movies")


def create_db_and_tables():
    """A helper function to create the database file and all defined tables."""
    print("Creating database and tables...")
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully.")

# This part allows you to run `python database.py` once to create the database
if __name__ == "__main__":
    create_db_and_tables()