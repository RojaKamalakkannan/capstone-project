"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

from app.api import auth_routes, appointment_routes, medical_record_routes, prescription_routes, media_routes

app = FastAPI(
    title="Healthcare Management System",
    description="Secure healthcare management system with patient data, appointments, medical records, prescriptions, and media",
    version="1.0.0",
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(auth_routes.router)
app.include_router(appointment_routes.router)
app.include_router(medical_record_routes.router)
app.include_router(prescription_routes.router)
app.include_router(media_routes.router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Healthcare Management System",
        "app_name": "Healthcare Management System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

