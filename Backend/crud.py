from sqlalchemy.orm import Session
from . import database, schemas, security

def get_user_by_email(db: Session, email: str):
    """Fetches a user from the database by their email address."""
    return db.query(database.User).filter(database.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user in the database."""
    hashed_password = security.hash_password(user.password)
    db_user = database.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user