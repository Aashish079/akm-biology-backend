from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    
class UserLogin(UserBase):
    password: str

class UserCreate(UserBase):
    password: str
    role: str = "student"

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    role: str
    must_change_password: bool

    class Config:
        from_attributes = True

class StudentRegistration(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    location: str
    # File will be uploaded separately via Form

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
