# backend/schemas.py
from pydantic import BaseModel, EmailStr

# Add this new class
class EmailCheck(BaseModel):
    email: EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True