"""
VoxCPM WebUI Backend - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import tts, voice_clone, voice_design, health, ultimate_clone

app = FastAPI(
    title="VoxCPM WebUI API",
    description="API for VoxCPM2 Text-to-Speech, Voice Design, Voice Cloning, and Ultimate Cloning",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
app.include_router(tts.router, prefix="/api/v1/tts", tags=["tts"])
app.include_router(voice_design.router, prefix="/api/v1/voice-design", tags=["voice-design"])
app.include_router(voice_clone.router, prefix="/api/v1/voice-clone", tags=["voice-clone"])
app.include_router(ultimate_clone.router, prefix="/api/v1/ultimate-clone", tags=["ultimate-clone"])

@app.get("/")
async def root():
    return {"message": "VoxCPM WebUI API is running"}