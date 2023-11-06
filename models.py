# Define Pydantic models for request and response schemas
from pydantic import BaseModel

class SignUpSchema(BaseModel):
    email: str
    password: str
    username: str
    full_name: str

    class Config:
        schema_extra = {
            "example": {
                "email": "sample@gmail.com",
                "password": "samplepass123",
                "username": "sample_user",
                "full_name": "John Doe"
            }
        }

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "sample@gmail.com",
                "password": "samplepass123"
            }
        }

class UpdateUserSchema(BaseModel):
    username: str
    full_name: str

    class Config:
        schema_extra = {
            "example": {
                "username": "updated_user",
                "full_name": "Updated User"
            }
        }

class UserSchema(BaseModel):
    email: str
    username: str
    full_name: str
    created_at: str
