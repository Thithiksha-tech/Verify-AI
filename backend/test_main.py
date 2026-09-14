import io
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, ".")

from database import Base
from main import app, get_db


TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    db = TestingSession()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


def register_and_login(email: str) -> str:
    response = client.post(
        "/auth/register",
        json={"name": email, "email": email, "password": "password123"},
    )
    assert response.status_code == 200
    response = client.post(
        "/auth/login",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_application_ownership_and_update():
    first_token = register_and_login("first@example.com")
    second_token = register_and_login("second@example.com")
    created = client.post(
        "/applications",
        headers=auth(first_token),
        json={"application_type": "Student"},
    )
    assert created.status_code == 200
    application_id = created.json()["id"]
    assert created.json()["status"] == "pending"
    assert client.get(f"/applications/{application_id}", headers=auth(first_token)).status_code == 200
    assert client.get(f"/applications/{application_id}", headers=auth(second_token)).status_code == 404
    assert client.put(
        f"/applications/{application_id}",
        headers=auth(first_token),
        json={"application_type": "Updated"},
    ).status_code == 200


def test_document_upload_and_ownership():
    owner_token = register_and_login("owner@example.com")
    other_token = register_and_login("other@example.com")
    application = client.post(
        "/applications",
        headers=auth(owner_token),
        json={"application_type": "Student"},
    ).json()
    application_id = application["id"]
    upload = client.post(
        f"/applications/{application_id}/documents",
        headers=auth(owner_token),
        data={"document_type": "identity"},
        files={"file": ("identity.pdf", io.BytesIO(b"%PDF-1.7 test"), "application/pdf")},
    )
    assert upload.status_code == 201
    assert upload.json()["status"] == "uploaded"
    assert client.get(
        f"/applications/{application_id}/documents", headers=auth(other_token)
    ).status_code == 404
    assert client.post(
        f"/applications/{application_id}/documents",
        headers=auth(other_token),
        data={"document_type": "identity"},
        files={"file": ("identity.pdf", io.BytesIO(b"%PDF"), "application/pdf")},
    ).status_code == 404


def test_missing_invalid_and_expired_tokens_are_rejected():
    assert client.get("/applications").status_code == 401
    assert client.get("/applications", headers=auth("not-a-token")).status_code == 401
    assert client.get(
        "/applications", headers=auth(
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxIiwiZXhwIjoxfQ.invalid"
        )
    ).status_code == 401


def test_upload_validation():
    token = register_and_login("files@example.com")
    application_id = client.post(
        "/applications",
        headers=auth(token),
        json={"application_type": "Student"},
    ).json()["id"]
    invalid = client.post(
        f"/applications/{application_id}/documents",
        headers=auth(token),
        data={"document_type": "identity"},
        files={"file": ("script.txt", io.BytesIO(b"not allowed"), "text/plain")},
    )
    assert invalid.status_code == 400
    oversized = client.post(
        f"/applications/{application_id}/documents",
        headers=auth(token),
        data={"document_type": "identity"},
        files={"file": ("large.pdf", io.BytesIO(b"x" * (10 * 1024 * 1024 + 1)), "application/pdf")},
    )
    assert oversized.status_code == 413
