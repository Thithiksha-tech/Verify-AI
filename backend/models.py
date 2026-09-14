from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="applicant")
    created_at = Column(DateTime, default=datetime.utcnow)

    applications = relationship("Application", back_populates="applicant")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    application_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    applicant = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(
        Integer,
        ForeignKey("applications.id"),
        nullable=False
    )
    document_type = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, nullable=False, default="uploaded")
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    application = relationship(
        "Application",
        back_populates="documents"
    )