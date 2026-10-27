import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import User, UserRole
from app.schemas import UserOut

router = APIRouter(prefix="/me", tags=["profile"])

RESUME_DIR = Path("uploads/resumes")
MAX_RESUME_SIZE = 2 * 1024 * 1024

@router.post("/resume", response_model=UserOut)
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.seeker))):
    contents = file.file.read(MAX_RESUME_SIZE + 1)
    if len(contents) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=413, detail="Resume must be under 2 MB")
    if not contents.startswith(b"%PDF"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed")

    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.pdf"
    (RESUME_DIR / filename).write_bytes(contents)

    current_user.resume_url = f"uploads/resumes/{filename}"
    db.commit()
    db.refresh(current_user)
    return current_user

