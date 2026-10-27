from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import require_role
from app.models import Application, Job, User, UserRole, ApplicationStatus
from app.schemas import ApplicationOut, MyApplicationOut, JobApplicationOut, ApplicationStatusUpdate
from app.routers.jobs import get_owned_job

router = APIRouter(tags=["applications"])

def get_application_for_recruiter(application_id: int, db: Session, current_user: User) -> Application:
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    get_owned_job(application.job_id, db, current_user)
    return application

@router.post("/jobs/{job_id}/apply", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.seeker))):
    job = db.get(Job,job_id)
    if job is None or not job.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if not current_user.resume_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Upload a resume before applying")
    
    existing = (db.query(Application).filter(Application.job_id==job_id, Application.candidate_id==current_user.id).first())
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already applied to this job")

    application = Application(job_id=job_id, candidate_id = current_user.id, resume_url = current_user.resume_url)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/me/applications", response_model=list[MyApplicationOut])
def my_applications(db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.seeker))):
    return (db.query(Application).options(joinedload(Application.job)).filter(Application.candidate_id == current_user.id).order_by(Application.applied_at.desc()).all())

@router.get("/jobs/{job_id}/applications", response_model=list[JobApplicationOut])
def job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter)),
):
    get_owned_job(job_id, db, current_user)
    return (
        db.query(Application)
        .options(joinedload(Application.candidate))
        .filter(Application.job_id == job_id)
        .order_by(Application.applied_at.desc())
        .all()
    )


@router.patch("/applications/{application_id}/status", response_model= JobApplicationOut)
def update_application_Status(application_id: int, payload: ApplicationStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.recruiter))):
    application = get_application_for_recruiter(application_id, db, current_user)
    application.status = ApplicationStatus(payload.status)
    db.commit()
    db.refresh(application)
    return application

@router.get("/applications/{application_id}/resume")
def download_resume(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.recruiter)),
):
    application = get_application_for_recruiter(application_id, db, current_user)
    path = Path(application.resume_url)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found")
    return FileResponse(path, media_type="application/pdf", filename=f"resume_{application.id}.pdf")