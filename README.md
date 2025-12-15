# Healthcare Management System - FastAPI

A comprehensive microservices-based system for managing patient data, scheduling appointments, and handling medical records securely in a clinic or hospital setting.

## Features

### Appointments
- `POST /patients/{id}/appointments` — Schedule appointment
- `GET /appointments` — List appointments (with filters)
- `GET /patients/{id}/appointments` — Get patient's appointments
- `PATCH /appointments/{id}` — Update appointment status (scheduled/confirmed/cancelled/completed)

### Medical Records (Sensitive - Encrypted)
- `POST /patients/{id}/records` — Add encrypted medical record/note (clinician)
- `GET /patients/{id}/records` — List records (access-controlled)
- `GET /records/{record_id}` — Retrieve and decrypt (with tight RBAC)

### Prescriptions
- `POST /patients/{id}/prescriptions` — Issue prescription (clinician)
- `GET /patients/{id}/prescriptions` — List patient prescriptions

### Media/Files
- `POST /patients/{id}/media` — Upload encrypted file (lab reports, imaging)
- `GET /patients/{id}/media` — List media files
- `GET /media/{id}` — Download decrypted file (authorized users only)

### Authentication
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login and get JWT token
- `GET /auth/me` — Get current user info

## Prerequisites

- Python 3.8 or higher
- pip or conda package manager

## Installation

1. **Create and activate virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

The `.env` file is already configured with default values. Update `SECRET_KEY` and `ENCRYPTION_KEY` for production:

```bash
# Generate new encryption key if needed:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Database

Uses SQLite for data persistence. Database file is created automatically at `healthcare.db`

## User Roles

- **Admin**: Full access to all features
- **Clinician**: Can manage appointments, medical records, and prescriptions
- **Patient**: Can view own appointments, medical records, and prescriptions

## Security Features

- **JWT Authentication**: Token-based authentication with Bearer scheme
- **Encryption**: AES encryption for sensitive data (medical records)
- **RBAC**: Role-Based Access Control for different user types
- **CORS**: Cross-Origin Resource Sharing enabled
- **Password Hashing**: Bcrypt password hashing with salt

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration
│   ├── database.py             # SQLite configuration
│   ├── auth.py                 # Authentication & RBAC
│   ├── security.py             # Encryption utilities
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   ├── appointment_routes.py  # Appointment endpoints
│   │   ├── medical_record_routes.py  # Medical record endpoints
│   │   ├── prescription_routes.py  # Prescription endpoints
│   │   └── media_routes.py     # Media/file endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   └── schemas.py          # Pydantic validation schemas
├── tests/
│   ├── __init__.py
│   └── test_main.py            # Test suite
├── media_storage/              # Encrypted file storage
├── .env                        # Environment variables
├── .gitignore
├── requirements.txt            # Project dependencies
└── README.md
```

## Testing

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app
```

## Example Usage

### 1. Register User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secure_password",
    "role": "patient"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "secure_password"
  }'
```

### 3. Schedule Appointment

```bash
curl -X POST "http://localhost:8000/patients/1/appointments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clinician_id": 2,
    "appointment_date": "2024-12-20T10:00:00",
    "reason": "Checkup",
    "notes": "Routine checkup"
  }'
```

### 4. Add Medical Record

```bash
curl -X POST "http://localhost:8000/patients/1/records" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "record_type": "diagnosis",
    "content": "Patient diagnosed with hypertension"
  }'
```

### 5. Upload Media File

```bash
curl -X POST "http://localhost:8000/patients/1/media?file_type=lab_report" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/lab_report.pdf"
```

## License

MIT License - Feel free to use this project for educational and commercial purposes.
