import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, func, Boolean, ForeignKey, text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, enum.Enum):
    seeker = "seeker"
    recruiter = "recruiter"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable = False)
    email = Column(String(255), unique = True, nullable = False)
    password_hash = Column(String(255), nullable = False)
    role = Column(Enum(UserRole, name =  "user_role"), nullable = False)
    resume_url = Column(Text, nullable = True)
    company_name = Column(String(200), nullable = True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    


class JobType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    internship = "internship"

class ExperienceLevel(str, enum.Enum):
    entry = "entry"
    mid = "mid"
    senior = "senior"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    recruiter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(120), nullable=False)
    category = Column(String(80), nullable=False)
    job_type = Column(Enum(JobType, name = "job_type"), nullable=False)
    experience_level = Column(Enum(ExperienceLevel, name = "experience_level"), nullable=False)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("job_id", "candidate_id", name="uq_application_job_candidate"),
    )

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_url = Column(Text, nullable=False)
    status = Column(Enum(ApplicationStatus, name="application_status"), nullable=False, server_default="pending")
    applied_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    job = relationship("Job")
    candidate = relationship("User")




