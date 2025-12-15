"""Tests for Healthcare Management System"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.models import User, Patient, UserRole, Base
from app.auth import hash_password
import os

# Create test client
client = TestClient(app)

# Test data
TEST_ADMIN = {
    "username": "admin_test",
    "email": "admin@test.com",
    "password": "admin123"
}

TEST_CLINICIAN = {
    "username": "clinician_test",
    "email": "clinician@test.com",
    "password": "clinician123"
}

TEST_PATIENT = {
    "username": "patient_test",
    "email": "patient@test.com",
    "password": "patient123"
}


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    db = SessionLocal()
    
    # Create admin user
    admin = User(
        username=TEST_ADMIN["username"],
        email=TEST_ADMIN["email"],
        hashed_password=hash_password(TEST_ADMIN["password"]),
        role=UserRole.ADMIN
    )
    db.add(admin)
    
    # Create clinician user
    clinician = User(
        username=TEST_CLINICIAN["username"],
        email=TEST_CLINICIAN["email"],
        hashed_password=hash_password(TEST_CLINICIAN["password"]),
        role=UserRole.CLINICIAN
    )
    db.add(clinician)
    
    # Create patient user
    patient_user = User(
        username=TEST_PATIENT["username"],
        email=TEST_PATIENT["email"],
        hashed_password=hash_password(TEST_PATIENT["password"]),
        role=UserRole.PATIENT
    )
    db.add(patient_user)
    db.commit()
    
    # Create patient profile
    patient = Patient(
        user_id=patient_user.id,
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-01",
        phone="555-0001",
        address="123 Main St"
    )
    db.add(patient)
    db.commit()
    
    yield db
    
    db.close()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Healthcare Management System" in response.json()["message"]


# Authentication Tests
def test_register_user():
    """Test user registration"""
    response = client.post("/auth/register", json={
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "newpass123",
        "role": "patient"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_register_duplicate_user():
    """Test duplicate user registration"""
    # First registration
    client.post("/auth/register", json={
        "username": "duplicate_user",
        "email": "duplicate@test.com",
        "password": "pass123",
        "role": "patient"
    })
    
    # Second registration with same username
    response = client.post("/auth/register", json={
        "username": "duplicate_user",
        "email": "other@test.com",
        "password": "pass123",
        "role": "patient"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login(setup_database):
    """Test user login"""
    response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post("/auth/login", json={
        "username": "nonexistent",
        "password": "wrongpass"
    })
    assert response.status_code == 401


# Appointment Tests
def test_schedule_appointment(setup_database):
    """Test scheduling an appointment"""
    # Login as patient
    login_response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get clinician ID (first clinician from DB)
    db = SessionLocal()
    clinician = db.query(User).filter(User.role == UserRole.CLINICIAN).first()
    db.close()
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/patients/1/appointments",
        json={
            "clinician_id": clinician.id,
            "appointment_date": "2024-12-20T10:00:00",
            "reason": "Checkup",
            "notes": "Routine checkup"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["reason"] == "Checkup"


def test_list_appointments(setup_database):
    """Test listing appointments"""
    # Login as patient
    login_response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/appointments", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_appointment(setup_database):
    """Test updating appointment status"""
    # Login as clinician
    login_response = client.post("/auth/login", json={
        "username": TEST_CLINICIAN["username"],
        "password": TEST_CLINICIAN["password"]
    })
    token = login_response.json()["access_token"]
    
    # Get appointment ID (first appointment from DB)
    db = SessionLocal()
    appointment = db.query(User).filter(User.username == TEST_CLINICIAN["username"]).first()
    if appointment:
        from app.models.models import Appointment
        appt = db.query(Appointment).filter(Appointment.clinician_id == appointment.id).first()
        if appt:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.patch(
                f"/appointments/{appt.id}",
                json={"status": "confirmed", "notes": "Confirmed"},
                headers=headers
            )
            assert response.status_code == 200
            assert response.json()["status"] == "confirmed"
    db.close()


# Medical Record Tests
def test_add_medical_record(setup_database):
    """Test adding a medical record"""
    # Login as clinician
    login_response = client.post("/auth/login", json={
        "username": TEST_CLINICIAN["username"],
        "password": TEST_CLINICIAN["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/patients/1/records",
        json={
            "record_type": "diagnosis",
            "content": "Patient diagnosed with hypertension"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["record_type"] == "diagnosis"


def test_get_medical_records(setup_database):
    """Test retrieving medical records"""
    # Login as patient
    login_response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/patients/1/records", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Prescription Tests
def test_issue_prescription(setup_database):
    """Test issuing a prescription"""
    # Login as clinician
    login_response = client.post("/auth/login", json={
        "username": TEST_CLINICIAN["username"],
        "password": TEST_CLINICIAN["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/patients/1/prescriptions",
        json={
            "medication_name": "Lisinopril",
            "dosage": "10mg",
            "frequency": "Once daily",
            "duration": "30 days",
            "notes": "Take in morning"
        },
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["medication_name"] == "Lisinopril"


def test_get_prescriptions(setup_database):
    """Test retrieving prescriptions"""
    # Login as patient
    login_response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/patients/1/prescriptions", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Media/File Tests
def test_upload_media(setup_database):
    """Test uploading media file"""
    # Login as patient
    login_response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create test file
    from io import BytesIO
    test_file = ("test.pdf", BytesIO(b"Test PDF content"), "application/pdf")
    
    response = client.post(
        "/patients/1/media?file_type=lab_report",
        files={"file": test_file},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["original_filename"] == "test.pdf"


def test_list_media(setup_database):
    """Test listing media files"""
    # Login as patient
    login_response = client.post("/auth/login", json={
        "username": TEST_PATIENT["username"],
        "password": TEST_PATIENT["password"]
    })
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/patients/1/media", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
