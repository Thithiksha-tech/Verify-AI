import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from auth import (
    can_access_application,
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from database import SessionLocal
from models import Application, Document, User
from schemas import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
    DocumentResponse,
    UserCreate,
    UserLogin,
)

load_dotenv()

app = FastAPI(title="VerifyAI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORAGE_DIR = Path(os.getenv("UPLOAD_DIR", Path(__file__).parent / "storage"))
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
ALLOWED_CONTENT_TYPES = {"application/pdf", "image/png", "image/jpeg"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_owned_application(
    application_id: int,
    db: Session,
    current_user: dict,
) -> Application:
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None or not can_access_application(application, current_user):
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.get("/")
def root():
    return {"message": "VerifyAI API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role="applicant",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user is None or not verify_password(
        user.password, existing_user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "access_token": create_access_token(existing_user.id, existing_user.role),
        "token_type": "bearer",
    }


@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.post("/applications", response_model=ApplicationResponse)
def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("applicant", "admin")),
):
    new_application = Application(
        applicant_id=current_user["user_id"],
        application_type=application.application_type,
        status="pending",
    )
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application


@app.get("/applications", response_model=list[ApplicationResponse])
def get_applications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    query = db.query(Application)
    if current_user["role"] != "admin":
        query = query.filter(Application.applicant_id == current_user["user_id"])
    return query.order_by(Application.created_at.desc()).all()


@app.get("/applications/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return get_owned_application(application_id, db, current_user)


@app.put("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_data: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    application = get_owned_application(application_id, db, current_user)
    application.application_type = application_data.application_type
    db.commit()
    db.refresh(application)
    return application


@app.post(
    "/applications/{application_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    application_id: int,
    document_type: str = Form(..., min_length=1, max_length=100),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    application = get_owned_application(application_id, db, current_user)
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG, and JPEG files are accepted",
        )

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{extension}"
    destination = STORAGE_DIR / stored_name
    size = 0

    with destination.open("wb") as output:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE:
                break
            output.write(chunk)
    if size > MAX_FILE_SIZE:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=413, detail="File exceeds the 10 MB limit")

    document = Document(
        application_id=application.id,
        document_type=document_type,
        filename=file.filename or stored_name,
        file_path=str(destination),
        status="uploaded",
    )
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError:
        db.rollback()
        destination.unlink(missing_ok=True)
        raise
    return document


@app.get(
    "/applications/{application_id}/documents",
    response_model=list[DocumentResponse],
)
def get_documents(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    application = get_owned_application(application_id, db, current_user)
    return (
        db.query(Document)
        .filter(Document.application_id == application.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
