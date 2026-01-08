from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routes import auth, chat, data_upload
import os

app = FastAPI(
    title="AI - Physio bot",
    description="AI-powered physiotherapy assistant by HASSAN",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(data_upload.router)

@app.get("/")
async def root():
    """Serve the main frontend page"""
    return FileResponse('frontend/index.html')

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Physio Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)