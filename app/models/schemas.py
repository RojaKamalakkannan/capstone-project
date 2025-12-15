"""Pydantic models for request/response validation"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    CLINICIAN = "clinician"
    PATIENT = "patient"


class AppointmentStatus(str, Enum):
    """Appointment statuses"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


# User Schemas
class UserCreate(BaseModel):
    """User creation schema"""
    username: str
    email: str
    password: str
    role: UserRole = UserRole.PATIENT


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    user: UserResponse


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


# Patient Schemas
class PatientCreate(BaseModel):
    """Patient creation schema"""
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str
    address: str
    medical_history: str = ""


class PatientUpdate(BaseModel):
    """Patient update schema"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None


class PatientResponse(BaseModel):
    """Patient response schema"""
    id: int
    user_id: int
    first_name: str
    last_name: str
    date_of_birth: str
    phone: str
    address: str
    medical_history: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Appointment Schemas
class AppointmentCreate(BaseModel):
    """Appointment creation schema"""
    clinician_id: int
    appointment_date: datetime
    reason: str
    notes: str = ""


class AppointmentUpdate(BaseModel):
    """Appointment update schema"""
    status: AppointmentStatus
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Appointment response schema"""
    id: int
    patient_id: int
    clinician_id: int
    appointment_date: datetime
    reason: str
    notes: str
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Appointment list response"""
    id: int
    patient_id: int
    clinician_id: int
    appointment_date: datetime
    reason: str
    status: AppointmentStatus
    
    class Config:
        from_attributes = True


# Medical Record Schemas
class MedicalRecordCreate(BaseModel):
    """Medical record creation schema"""
    record_type: str
    content: str


class MedicalRecordResponse(BaseModel):
    """Medical record response schema (decrypted)"""
    id: int
    patient_id: int
    clinician_id: int
    record_type: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Prescription Schemas
class PrescriptionCreate(BaseModel):
    """Prescription creation schema"""
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    notes: str = ""


class PrescriptionResponse(BaseModel):
    """Prescription response schema"""
    id: int
    patient_id: int
    clinician_id: int
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    notes: str
    issued_date: datetime
    
    class Config:
        from_attributes = True


# Media/File Schemas
class MediaFileResponse(BaseModel):
    """Media file response schema"""
    id: int
    patient_id: int
    original_filename: str
    file_type: str
    file_size: int
    uploaded_by: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class MediaFileDownloadResponse(BaseModel):
    """Media file download response"""
    filename: str
    content: bytes
    content_type: str
