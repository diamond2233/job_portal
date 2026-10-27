from pydantic import BaseModel, EmailStr, Field
from app.models import UserRole, JobType, ExperienceLevel, ApplicationStatus
from datetime import datetime
from typing import Literal

class UserCreate(BaseModel):
    name: str = Field(min_length = 1, max_length = 120)
    email: EmailStr
    password: str = Field(min_length = 8, max_length = 72)
    role: UserRole
    company_name: str | None = None

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    company_name: str | None = None
    resume_url: str | None = None

    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class JobCreate(BaseModel):
    title : str = Field(min_length=1, max_length=200)
    description : str = Field(min_length=1)
    location : str = Field(min_length=1, max_length=120)
    category : str = Field(min_length=1, max_length=80)
    job_type : JobType
    experience_level : ExperienceLevel
    salary_min : int | None = Field(default=None, ge=0)
    salary_max : int | None = Field(default=None, ge=0)

class JobOut(BaseModel):
    id: int
    recruiter_id: int
    title: str
    description: str
    location: str
    category: str
    job_type: JobType
    experience_level: ExperienceLevel
    salary_min: int | None = None
    salary_max: int | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_url: str
    status: ApplicationStatus
    applied_at: datetime

    model_config = {"from_attributes": True}

class MyApplicationOut(BaseModel):
    id: int
    status: ApplicationStatus
    applied_at: datetime
    job: JobOut

    model_config = {"from_attributes": True}


class ApplicantOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}

class JobApplicationOut(BaseModel):
    id: int
    status: ApplicationStatus
    applied_at: datetime
    candidate: ApplicantOut

    model_config = {"from_attributes": True}


class ApplicationStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected"]
