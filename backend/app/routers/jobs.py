from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import User, UserRole, Job, JobType, ExperienceLevel
from app.schemas import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])

def get_owned_job(job_id: int, db: Session, current_user: User) -> Job:
    job = db.get(Job,job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.recruiter_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify your own jobs",)
    return job


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.recruiter))):
    job = Job(**payload.model_dump(), recruiter_id=current_user.id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

@router.get("", response_model=list[JobOut])
def list_jobs(search: str | None = None, location: str | None = None, category: str | None = None, job_type: JobType | None = None, experience_level: ExperienceLevel | None = None, limit: int = Query(10, ge=1, le=50), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    query = db.query(Job).filter(Job.is_active == True)

    if search:
        query = query.filter(Job.title.ilike(f"%{search}%")) 
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if category:
        query = query.filter(Job.category.ilike(category))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if experience_level:
        query = query.filter(Job.experience_level == experience_level)

    return query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if job is None or not job.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.recruiter))):
    job = get_owned_job(job_id, db, current_user)
    for field, value in payload.model_dump().items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.recruiter))):
    job = get_owned_job(job_id,db,current_user)
    db.delete(job)
    db.commit()



recruiter_router = APIRouter(prefix="/recruiter", tags = ["recruiter"])

@recruiter_router.get("/jobs", response_model= list[JobOut])
def my_jobs(db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.recruiter))):
    return (db.query(Job).filter(Job.recruiter_id == current_user.id).order_by(Job.created_at.desc()).all())