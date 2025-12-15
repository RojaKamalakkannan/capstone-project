"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import auth_routes, appointment_routes, medical_record_routes, prescription_routes, media_routes

# Initialize database
init_db()

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
