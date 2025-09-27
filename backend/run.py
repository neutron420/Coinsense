#!/usr/bin/env python3
"""
Startup script for the Crypto AI Chatbot Backend
"""
import uvicorn
import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def main():
    """Main startup function"""
    print(" Starting Crypto AI Chatbot Backend...")
    print("Loading ML models...")
    print("Initializing authentication...")
    print("Starting FastAPI server...")
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
