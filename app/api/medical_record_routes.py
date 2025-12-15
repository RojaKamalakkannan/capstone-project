"""Medical record routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import MedicalRecord, Patient, User, UserRole
from app.models.schemas import MedicalRecordCreate, MedicalRecordResponse
from app.auth import get_current_user, get_current_clinician, check_patient_access
from app.security import encrypt_data, decrypt_data

router = APIRouter(prefix="/patients", tags=["medical_records"])


@router.post("/{patient_id}/records", response_model=MedicalRecordResponse)
async def add_medical_record(
    patient_id: int,
    record: MedicalRecordCreate,
    current_user: User = Depends(get_current_clinician),
    db: Session = Depends(get_db)
):
    """Add encrypted medical record (clinician only)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Encrypt the record content
    encrypted_content = encrypt_data(record.content)
    
    # Create medical record
    new_record = MedicalRecord(
        patient_id=patient_id,
        clinician_id=current_user.id,
        record_type=record.record_type,
        content=encrypted_content
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    # Decrypt content before returning (only clinician sees it)
    return MedicalRecordResponse(
        id=new_record.id,
        patient_id=new_record.patient_id,
        clinician_id=new_record.clinician_id,
        record_type=new_record.record_type,
        content=decrypt_data(new_record.content),
        created_at=new_record.created_at
    )


@router.get("/{patient_id}/records", response_model=list[MedicalRecordResponse])
async def get_medical_records(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get medical records (access-controlled)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not check_patient_access(patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's medical records"
        )
    
    records = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient_id
    ).order_by(MedicalRecord.created_at.desc()).all()
    
    # Decrypt content for authorized users
    decrypted_records = []
    for record in records:
        decrypted_records.append(MedicalRecordResponse(
            id=record.id,
            patient_id=record.patient_id,
            clinician_id=record.clinician_id,
            record_type=record.record_type,
            content=decrypt_data(record.content),
            created_at=record.created_at
        ))
    
    return decrypted_records


@router.get("/records/{record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve and decrypt specific medical record (tight RBAC)"""
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    # Check access permissions
    if not check_patient_access(record.patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this medical record"
        )
    
    # Additional check: if patient, only allow access to own records
    if current_user.role == UserRole.PATIENT:
        if current_user.patient_profile.id != record.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own records"
            )
    
    return MedicalRecordResponse(
        id=record.id,
        patient_id=record.patient_id,
        clinician_id=record.clinician_id,
        record_type=record.record_type,
        content=decrypt_data(record.content),
        created_at=record.created_at
    )
