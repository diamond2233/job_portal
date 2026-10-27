from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
# from app import models
from app.routers import auth, jobs, applications, users

# Base.metadata.create_all(bind=engine)


app = FastAPI(title = "Job Portal API")
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(jobs.recruiter_router)
app.include_router(applications.router)
app.include_router(users.router)

@app.get("/health")
def health_check(db : Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status" : "ok"}

