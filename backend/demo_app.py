"""
Demo FastAPI application for WageLift - Simplified version for demonstration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict, Any

# Create FastAPI application
app = FastAPI(
    title="WageLift API Demo",
    version="1.0.0",
    description="AI-powered platform to help employees quantify purchasing-power loss and craft evidence-based raise requests"
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
    """Root endpoint"""
    return {
        "message": "Welcome to WageLift API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "CPI Gap Calculation",
            "Salary Benchmarking", 
            "AI-Powered Raise Letters",
            "Gusto Integration",
            "Email Services"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "WageLift API",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/v1/demo/salary-analysis")
async def demo_salary_analysis():
    """Demo salary analysis endpoint"""
    return {
        "current_salary": 85000,
        "adjusted_salary": 95000,
        "percentage_gap": -10.5,
        "dollar_gap": -10000,
        "inflation_rate": 12.3,
        "years_elapsed": 2,
        "message": "You are behind inflation by $10,000",
        "recommendation": "Consider requesting a salary adjustment"
    }

@app.get("/api/v1/demo/benchmark")
async def demo_benchmark():
    """Demo salary benchmark endpoint"""
    return {
        "job_title": "Software Engineer",
        "location": "United States",
        "market_salary": {
            "p25": 75000,
            "p50": 90000,
            "p75": 110000,
            "p90": 130000
        },
        "your_position": "Below median",
        "percentile": 35,
        "recommendation": "Your salary is below market median"
    }

@app.post("/api/v1/demo/raise-letter")
async def demo_raise_letter():
    """Demo raise letter generation endpoint"""
    return {
        "letter_content": """Dear [Manager Name],

I hope this message finds you well. I am writing to request a meeting to discuss my current compensation package.

Based on my analysis using current market data and inflation trends, I have identified that my purchasing power has decreased by approximately 10.5% since my last salary adjustment. This represents a gap of $10,000 between my current compensation and what would maintain my original purchasing power.

Key points supporting this request:
• Market analysis shows similar roles paying 15-25% above my current salary
• My contributions have increased significantly over the past year
• Inflation has outpaced my salary growth by 10.5%

I would appreciate the opportunity to discuss this matter with you and explore options for bringing my compensation in line with current market conditions and my contributions to the team.

Thank you for your time and consideration.

Best regards,
[Your Name]""",
        "analysis_summary": {
            "inflation_gap": "$10,000",
            "market_position": "Below median",
            "recommended_increase": "15-20%"
        },
        "status": "generated",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/v1/demo/features")
async def demo_features():
    """Demo features overview"""
    return {
        "features": {
            "cpi_calculation": {
                "name": "CPI Gap Analysis",
                "description": "Calculate purchasing power loss due to inflation",
                "status": "available",
                "demo_endpoint": "/api/v1/demo/salary-analysis"
            },
            "salary_benchmarking": {
                "name": "Market Salary Comparison", 
                "description": "Compare your salary against market rates",
                "status": "available",
                "demo_endpoint": "/api/v1/demo/benchmark"
            },
            "ai_raise_letters": {
                "name": "AI-Powered Raise Request Letters",
                "description": "Generate professional raise request letters",
                "status": "available", 
                "demo_endpoint": "/api/v1/demo/raise-letter"
            },
            "gusto_integration": {
                "name": "Gusto OAuth Integration",
                "description": "Automatically sync salary data from Gusto",
                "status": "implemented",
                "endpoints": [
                    "/api/v1/gusto/authorize",
                    "/api/v1/gusto/callback", 
                    "/api/v1/gusto/sync"
                ]
            },
            "email_services": {
                "name": "Email & PDF Services",
                "description": "Send raise letters via email with PDF attachments",
                "status": "implemented"
            }
        },
        "completion_status": "93.33% (14/15 tasks completed)",
        "latest_feature": "Gusto OAuth Integration with encrypted token storage"
    }

if __name__ == "__main__":
    print("🚀 Starting WageLift Demo API...")
    print("📱 Frontend will be available at: http://localhost:3000")
    print("🔧 API Documentation: http://localhost:8000/docs")
    print("📊 Demo Features: http://localhost:8000/api/v1/demo/features")
    
    uvicorn.run(
        "demo_app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 