"""Media/File routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import MediaFile, Patient, User
from app.models.schemas import MediaFileResponse
from app.auth import get_current_user, check_patient_access
from app.security import encrypt_data, decrypt_data
import os
import base64
import io
from pathlib import Path

router = APIRouter(prefix="/patients", tags=["media"])

# Directory for storing encrypted files
MEDIA_STORAGE_DIR = Path("./media_storage")
MEDIA_STORAGE_DIR.mkdir(exist_ok=True)


@router.post("/{patient_id}/media", response_model=MediaFileResponse)
async def upload_media(
    patient_id: int,
    file: UploadFile = File(...),
    file_type: str = "lab_report",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload encrypted file (lab reports, imaging, etc.)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not check_patient_access(patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient"
        )
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    # Encrypt file content
    encrypted_content = encrypt_data(file_content.decode('latin-1'))
    encrypted_b64 = base64.b64encode(encrypted_content.encode()).decode()
    
    # Create media file record
    new_media = MediaFile(
        patient_id=patient_id,
        original_filename=file.filename,
        file_type=file_type,
        file_path=f"patient_{patient_id}/{file.filename}",
        encrypted_content=encrypted_b64,
        file_size=file_size,
        uploaded_by=current_user.id
    )
    db.add(new_media)
    db.commit()
    db.refresh(new_media)
    
    return new_media


@router.get("/{patient_id}/media", response_model=list[MediaFileResponse])
async def list_patient_media(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all media files for a patient (access-controlled)"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if not check_patient_access(patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's media files"
        )
    
    media_files = db.query(MediaFile).filter(
        MediaFile.patient_id == patient_id
    ).order_by(MediaFile.uploaded_at.desc()).all()
    
    return media_files


@router.get("/media/{media_id}")
async def download_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download decrypted file (authorized users only)"""
    media = db.query(MediaFile).filter(MediaFile.id == media_id).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )
    
    # Check access permissions
    if not check_patient_access(media.patient_id, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this file"
        )
    
    # Decrypt file content
    try:
        encrypted_data_b64 = media.encrypted_content
        encrypted_data = base64.b64decode(encrypted_data_b64)
        decrypted_content = decrypt_data(encrypted_data.decode())
        file_bytes = decrypted_content.encode('latin-1')
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decrypt file: {str(e)}"
        )
    
    # Return file as download
    return StreamingResponse(
        iter([file_bytes]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={media.original_filename}"}
    )
