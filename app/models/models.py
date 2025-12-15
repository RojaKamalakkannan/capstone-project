"""Database models for healthcare system"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "admin"
    CLINICIAN = "clinician"
    PATIENT = "patient"


class AppointmentStatus(str, enum.Enum):
    """Appointment statuses"""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    clinician_appointments = relationship("Appointment", back_populates="clinician", foreign_keys="Appointment.clinician_id")
    clinician_records = relationship("MedicalRecord", back_populates="clinician")
    clinician_prescriptions = relationship("Prescription", back_populates="clinician")


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(String)
    phone = Column(String)
    address = Column(String)
    medical_history = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")
    media_files = relationship("MediaFile", back_populates="patient", cascade="all, delete-orphan")


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    clinician_id = Column(Integer, ForeignKey("users.id"), index=True)
    appointment_date = Column(DateTime, index=True)
    reason = Column(String)
    notes = Column(Text, default="")
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    clinician = relationship("User", back_populates="clinician_appointments", foreign_keys=[clinician_id])


class MedicalRecord(Base):
    """Medical Record model (sensitive - encrypted)"""
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    clinician_id = Column(Integer, ForeignKey("users.id"), index=True)
    record_type = Column(String)  # note, diagnosis, test_result, etc.
    content = Column(Text)  # Encrypted content
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    clinician = relationship("User", back_populates="clinician_records")


class Prescription(Base):
    """Prescription model"""
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    clinician_id = Column(Integer, ForeignKey("users.id"), index=True)
    medication_name = Column(String)
    dosage = Column(String)
    frequency = Column(String)
    duration = Column(String)
    notes = Column(Text, default="")
    issued_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="prescriptions")
    clinician = relationship("User", back_populates="clinician_prescriptions")


class MediaFile(Base):
    """Media/File model (encrypted storage)"""
    __tablename__ = "media_files"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    original_filename = Column(String)
    file_type = Column(String)  # lab_report, imaging, etc.
    file_path = Column(String)  # Path to encrypted file
    encrypted_content = Column(Text)  # Base64 encoded encrypted content
    file_size = Column(Integer)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="media_files")
