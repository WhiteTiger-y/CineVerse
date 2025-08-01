# backend/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# This defines the fields for creating a new user
class UserCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None # last_name is optional
    mobile_no: str
    email: EmailStr
    password: str

# This defines the fields that will be returned by the API (never return the password)
class User(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    mobile_no: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

# --- Schemas for existing and future features ---

class UserLogin(BaseModel):
    identifier: str
    password: str

class EmailCheck(BaseModel):
    email: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class MobileCheck(BaseModel):
    mobile_no: str