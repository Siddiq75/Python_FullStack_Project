from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
from datetime import datetime

# Add the Front-End directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Front-End'))
from db import Database
app = FastAPI(title="Job Application Tracker API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

# Pydantic models
class ApplicationCreate(BaseModel):
    user_id: str
    company: str                                                                          
    role: str
    status: str = "applied"
    notes: Optional[str] = None 

class ApplicationUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class JobPostingCreate(BaseModel):
    user_id: str
    title: str
    description: str
    requirements: str
    deadline: str

class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    role: str

# Validation functions (moved from logic.py)
def validate_application_data(company, role, status):
    errors = []
    if not company or len(company.strip()) == 0:
        errors.append("Company name is required")
    if not role or len(role.strip()) == 0:
        errors.append("Job role is required")
    if status not in ['applied', 'interview', 'offer', 'rejected']:
        errors.append("Invalid status")
    return errors

def validate_job_posting_data(title, description, deadline):
    errors = []
    if not title or len(title.strip()) == 0:
        errors.append("Job title is required")
    if not description or len(description.strip()) == 0:
        errors.append("Job description is required")
    if deadline and deadline < datetime.now().date():
        errors.append("Deadline cannot be in the past")
    return errors

def get_application_stats(applications):
    if not applications:
        return {
            "total": 0,
            "applied": 0,
            "interview": 0,
            "offer": 0,
            "rejected": 0,
            "success_rate": 0
        }
    
    # Simple counting (pandas not available in basic setup)
    total = len(applications)
    status_counts = {}
    for app in applications:
        status = app.get('status', 'applied')
        status_counts[status] = status_counts.get(status, 0) + 1
    
    success_rate = round((status_counts.get('offer', 0) / total) * 100, 2) if total > 0 else 0
    
    return {
        "total": total,
        "applied": status_counts.get('applied', 0),
        "interview": status_counts.get('interview', 0),
        "offer": status_counts.get('offer', 0),
        "rejected": status_counts.get('rejected', 0),
        "success_rate": success_rate
    }

# API Routes
@app.get("/")
async def root():
    return {"message": "Job Application Tracker API"}

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    profile = db.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/api/profile")
async def create_profile(profile: UserProfile):
    new_profile = db.create_user_profile(
        profile.id, profile.username, profile.email, profile.role
    )
    if not new_profile:
        raise HTTPException(status_code=400, detail="Failed to create profile")
    return new_profile

# Application endpoints
@app.get("/api/applications/{user_id}")
async def get_applications(user_id: str):
    applications = db.get_applications(user_id)
    return applications

@app.post("/api/applications")
async def create_application(application: ApplicationCreate):
    errors = validate_application_data(
        application.company, application.role, application.status
    )
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    new_app = db.add_application(
        application.user_id, application.company, application.role,
        application.status, application.notes
    )
    if not new_app:
        raise HTTPException(status_code=400, detail="Failed to create application")
    return new_app

@app.put("/api/applications/{application_id}")
async def update_application(application_id: int, update: ApplicationUpdate):
    updated = db.update_application_status(application_id, update.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Application not found")
    return updated

@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: int):
    success = db.delete_application(application_id)
    if not success:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted successfully"}

# Job Posting endpoints
@app.get("/api/jobpostings/{user_id}")
async def get_job_postings(user_id: str):
    postings = db.get_job_postings(user_id)
    return postings

@app.post("/api/jobpostings")
async def create_job_posting(posting: JobPostingCreate):
    deadline = datetime.strptime(posting.deadline, "%Y-%m-%d").date()
    
    errors = validate_job_posting_data(
        posting.title, posting.description, deadline
    )
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    
    new_posting = db.add_job_posting(
        posting.user_id, posting.title, posting.description,
        posting.requirements, posting.deadline
    )
    if not new_posting:
        raise HTTPException(status_code=400, detail="Failed to create job posting")
    return new_posting

@app.put("/api/jobpostings/{job_id}")
async def update_job_posting(job_id: int, status: str):
    if status not in ['active', 'closed']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    updated = db.update_job_posting(job_id, status=status)
    if not updated:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return updated

@app.delete("/api/jobpostings/{job_id}")
async def delete_job_posting(job_id: int):
    success = db.delete_job_posting(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return {"message": "Job posting deleted successfully"}

# Analytics endpoints
@app.get("/api/analytics/{user_id}")
async def get_analytics(user_id: str):
    applications = db.get_applications(user_id)
    stats = get_application_stats(applications)
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)