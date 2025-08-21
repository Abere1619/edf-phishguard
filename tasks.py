import os
from celery import Celery

# Read from environment variable, with fallback for local development
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(__name__)
celery.conf.broker_url = REDIS_URL
celery.conf.result_backend = REDIS_URL

@celery.task
def add(x, y):
    """Test task to verify Celery is working"""
    return x + y

@celery.task
def analyze_artifact(artifact_id, filename):
    """Main task for analyzing phishing artifacts"""
    # Simulate analysis work
    print(f"Analyzing artifact {artifact_id}: {filename}")
    
    # Simulate some processing time
    import time
    time.sleep(2)
    
    # Return a mock analysis result
    return {
        "artifact_id": artifact_id,
        "filename": filename,
        "verdict": "suspicious",
        "confidence": 0.85,
        "details": {
            "malicious_indicators": ["suspicious_domain", "unusual_headers"],
            "recommendation": "Quarantine and investigate further"
        }
    }
