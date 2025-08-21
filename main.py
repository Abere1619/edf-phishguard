from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import redis
from minio import Minio
from minio.error import S3Error
import os
import uuid
from datetime import datetime

from db import get_db, engine, Base
from tasks import analyze_artifact

app = FastAPI(title="EDF PhishGuard", version="1.0.0")

# Initialize database tables
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "EDF PhishGuard API", "status": "healthy", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Redis connection
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        r = redis.from_url(redis_url)
        r.ping()
        redis_status = "connected"
    except Exception as e:
        redis_status = f"error: {str(e)}"
    
    return {
        "status": "healthy", 
        "database": db_status, 
        "redis": redis_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT version()")
        version = result.scalar()
        return {"message": "Database connection successful!", "version": version}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())
        
        # For now, just queue the analysis task
        task = analyze_artifact.delay(analysis_id, file.filename)
        
        return {
            "message": "Analysis started",
            "analysis_id": analysis_id,
            "task_id": task.id,
            "filename": file.filename,
            "description": description
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/task/{task_id}")
async def get_task_result(task_id: str):
    try:
        from tasks import celery
        result = celery.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.ready() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")
