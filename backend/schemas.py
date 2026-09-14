from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ApplicationCreate(BaseModel):
    application_type: str = Field(min_length=1, max_length=100)


class ApplicationUpdate(BaseModel):
    application_type: str = Field(min_length=1, max_length=100)


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    applicant_id: int
    application_type: str
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    document_type: str
    filename: str
    file_path: str
    status: str
    uploaded_at: datetime
