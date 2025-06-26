from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="WageLift API",
    description="Robust WageLift Backend API with Enhanced Error Handling",
    version="1.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "WageLift API is running!",
        "status": "success",
        "version": "1.0.1",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    logger.info("Health check accessed")
    return {
        "status": "healthy",
        "service": "wagelift-backend",
        "version": "1.0.1",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational"
    }

@app.get("/api/test")
async def test_endpoint():
    return {"message": "Backend is working!", "data": "test data"}

# Add salary calculation endpoint with error handling
@app.post("/api/salary/calculate")
async def calculate_salary():
    try:
        logger.info("Salary calculation requested")
        return {
            "message": "Salary calculation endpoint",
            "status": "mock", 
            "timestamp": datetime.now().isoformat(),
            "data": {
                "current_salary": 75000,
                "recommended_raise": 8500,
                "market_adjustment": 12.5,
                "inflation_adjustment": 3.2,
                "calculation_date": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error in salary calculation: {str(e)}")
        raise HTTPException(status_code=500, detail="Salary calculation failed")

# Add user endpoints to prevent crashes
@app.get("/api/user/profile")
async def get_user_profile():
    try:
        logger.info("User profile requested")
        return {
            "message": "Mock user profile",
            "user": None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@app.get("/api/auth/session")
async def get_auth_session():
    try:
        logger.info("Auth session requested")
        return {
            "authenticated": False,
            "user": None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting auth session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get auth session")

# Add additional API endpoints for frontend compatibility
@app.get("/api/raise-letter/templates")
async def get_letter_templates():
    try:
        logger.info("Letter templates requested")
        return {
            "templates": [
                {"id": "professional", "name": "Professional", "description": "Formal and professional tone"},
                {"id": "confident", "name": "Confident", "description": "Assertive and confident approach"},
                {"id": "collaborative", "name": "Collaborative", "description": "Team-focused and collaborative"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting letter templates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get letter templates")

@app.post("/api/raise-letter/generate")
async def generate_raise_letter():
    try:
        logger.info("Raise letter generation requested")
        return {
            "id": f"letter_{int(datetime.now().timestamp())}",
            "content": "Mock generated raise letter content",
            "subject": "Request for Salary Review",
            "status": "generated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating raise letter: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate raise letter")

@app.post("/api/email/send")
async def send_email():
    try:
        logger.info("Email send requested")
        return {
            "id": f"email_{int(datetime.now().timestamp())}",
            "status": "sent",
            "message": "Email sent successfully (mock)",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send email")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)