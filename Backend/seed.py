import os
from dotenv import load_dotenv
from Backend.database import SessionLocal, Base, engine, User, ChatMessage
from Backend.security import hash_password


def main():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create a test user if not exists
    email = "test@example.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            first_name="Test",
            last_name="User",
            mobile_no="1234567890",
            username="testuser",
            email=email,
            hashed_password=hash_password("Testpass1"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Created test user", user.id)
    else:
        print("Test user already exists", user.id)

    # Seed some chat messages
    sid = str(user.id)
    if not db.query(ChatMessage).filter(ChatMessage.user_id == user.id).first():
        db.add(ChatMessage(session_id=sid, user_id=user.id, sender='user', message='Hi'))
        db.add(ChatMessage(session_id=sid, user_id=user.id, sender='bot', message='Hello!'))
        db.commit()
        print("Seeded chat messages")
    else:
        print("Chat messages already present for test user")

    db.close()


if __name__ == "__main__":
    main()
