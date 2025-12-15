"""API Package"""
from . import auth_routes, appointment_routes, medical_record_routes, prescription_routes, media_routes

__all__ = [
    "auth_routes",
    "appointment_routes",
    "medical_record_routes",
    "prescription_routes",
    "media_routes"
]
