# backend/crud.py
from Backend import database, schemas, security
from sqlalchemy.orm import Session
# Change this line to make it a relative import
from . import database, schemas, security

def get_user_by_email(db: Session, email: str):
    return db.query(database.User).filter(database.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(database.User).filter(database.User.username == username).first()

def get_user_by_mobile(db: Session, mobile_no: str):
    return db.query(database.User).filter(database.User.mobile_no == mobile_no).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a new user in the database.
    This function now also saves the new user details and creates a default username.
    """
    hashed_password = security.hash_password(user.password)
    
    # Create a default username from the email address (part before the '@')
    default_username = user.email.split('@')[0]

    db_user = database.User(
        first_name=user.first_name,
        last_name=user.last_name,
        mobile_no=user.mobile_no,
        email=user.email,
        username=default_username, 
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: database.User, new_password: str):
    """Updates a user's password."""
    user.hashed_password = security.hash_password(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_profile_pic_url(db: Session, user_id: int, url: str):
    """Updates a user's profile picture URL in the database."""
    db_user = db.query(database.User).filter(database.User.id == user_id).first()
    if db_user:
        db_user.profile_pic_url = url
        db.commit()
        db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int):
    return db.query(database.User).filter(database.User.id == user_id).first()

def update_username(db: Session, user_id: int, new_username: str):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.username = new_username
        db.commit()
        db.refresh(db_user)
    return db_user