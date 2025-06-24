from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="WageLift API",
    description="Simple WageLift Backend API",
    version="1.0.0"
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
    return {"message": "WageLift API is running!", "status": "success"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "wagelift-backend"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "Backend is working!", "data": "test data"}

# Add salary calculation endpoint
@app.post("/api/salary/calculate")
async def calculate_salary():
    return {
        "message": "Salary calculation endpoint",
        "status": "mock", 
        "data": {
            "current_salary": 75000,
            "recommended_raise": 8500,
            "market_adjustment": 12.5,
            "inflation_adjustment": 3.2
        }
    }

# Add user endpoints to prevent crashes
@app.get("/api/user/profile")
async def get_user_profile():
    return {"message": "Mock user profile", "user": None}

@app.get("/api/auth/session")
async def get_auth_session():
    return {"authenticated": False, "user": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)