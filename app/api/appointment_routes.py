"""Appointment routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.models import Appointment, Patient, User, AppointmentStatus
from app.models.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse, AppointmentListResponse
from app.auth import get_current_user, get_current_clinician, check_patient_access

router = APIRouter(prefix="/patients", tags=["appointments"])


@router.post("/{patient_id}/appointments", response_model=AppointmentResponse)
async def schedule_appointment(
    patient_id: int,
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule a new appointment for a patient"""
    # Check if patient exists and user has access
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not check_patient_access(patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's data"
        )
    
    # Verify clinician exists
    clinician = db.query(User).filter(User.id == appointment.clinician_id).first()
    if not clinician:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinician not found"
        )
    
    # Create appointment
    new_appointment = Appointment(
        patient_id=patient_id,
        clinician_id=appointment.clinician_id,
        appointment_date=appointment.appointment_date,
        reason=appointment.reason,
        notes=appointment.notes
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return new_appointment


@router.get("/appointments", response_model=list[AppointmentListResponse])
async def list_appointments(
    current_user: User = Depends(get_current_user),
    status_filter: str = Query(None),
    db: Session = Depends(get_db)
):
    """List appointments with optional filters"""
    query = db.query(Appointment)
    
    # Filter by user role
    if current_user.role.value == "patient":
        # Patients can only see their own appointments
        patient = current_user.patient_profile
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found"
            )
        query = query.filter(Appointment.patient_id == patient.id)
    elif current_user.role.value == "clinician":
        # Clinicians can see appointments they are assigned to
        query = query.filter(Appointment.clinician_id == current_user.id)
    # Admins can see all appointments
    
    # Apply status filter if provided
    if status_filter:
        try:
            status_enum = AppointmentStatus[status_filter.upper()]
            query = query.filter(Appointment.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    appointments = query.order_by(Appointment.appointment_date).all()
    return appointments


@router.get("/{patient_id}/appointments", response_model=list[AppointmentListResponse])
async def get_patient_appointments(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific patient"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not check_patient_access(patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's data"
        )
    
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.appointment_date).all()
    
    return appointments


@router.patch("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    current_user: User = Depends(get_current_clinician),
    db: Session = Depends(get_db)
):
    """Update appointment status (clinician only)"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Verify clinician can update this appointment
    if current_user.role.value != "admin" and appointment.clinician_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own appointments"
        )
    
    # Update appointment
    appointment.status = appointment_update.status
    if appointment_update.notes:
        appointment.notes = appointment_update.notes
    appointment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    
    return appointment
