"""Prescription routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Prescription, Patient, User, UserRole
from app.models.schemas import PrescriptionCreate, PrescriptionResponse
from app.auth import get_current_user, get_current_clinician, check_patient_access

router = APIRouter(prefix="/patients", tags=["prescriptions"])


@router.post("/{patient_id}/prescriptions", response_model=PrescriptionResponse)
async def issue_prescription(
    patient_id: int,
    prescription: PrescriptionCreate,
    current_user: User = Depends(get_current_clinician),
    db: Session = Depends(get_db)
):
    """Issue prescription for a patient (clinician only)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Create prescription
    new_prescription = Prescription(
        patient_id=patient_id,
        clinician_id=current_user.id,
        medication_name=prescription.medication_name,
        dosage=prescription.dosage,
        frequency=prescription.frequency,
        duration=prescription.duration,
        notes=prescription.notes
    )
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    
    return new_prescription


@router.get("/{patient_id}/prescriptions", response_model=list[PrescriptionResponse])
async def get_patient_prescriptions(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all prescriptions for a patient (access-controlled)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not check_patient_access(patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's prescriptions"
        )
    
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).order_by(Prescription.issued_date.desc()).all()
    
    return prescriptions


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific prescription details"""
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id
    ).first()
    
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    # Check access permissions
    if not check_patient_access(prescription.patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this prescription"
        )
    
    return prescription
