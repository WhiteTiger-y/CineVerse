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
    profile_pic_url: Optional[str] = None  # New field for profile picture URL
    is_verified: bool
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

class UsernameUpdate(BaseModel):
    user_id: int
    new_username: str

class PasswordUpdate(BaseModel):
    user_id: int
    old_password: str
    new_password: str
    # Password policy: 8-64 chars, at least one letter and one digit

class ProfilePicUpdate(BaseModel):
    user_id: int
    url: str

class VerifyOtpRequest(BaseModel):
    identifier: str
    otp_code: str

class ResendOtpRequest(BaseModel):
    identifier: str