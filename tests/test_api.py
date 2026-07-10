import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_audits.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_audit():
    response = client.post(
        "/api/v1/audits",
        json={"url": "https://example.com"}
    )
    assert response.status_code == 202
    data = response.json()
    assert data["url"] == "https://example.com/"
    assert data["status"] == "pending"
    assert "id" in data

def test_create_audit_invalid_url():
    response = client.post(
        "/api/v1/audits",
        json={"url": "not-a-url"}
    )
    assert response.status_code == 422

def test_get_audits():
    # Create one first
    client.post("/api/v1/audits", json={"url": "https://example.com"})

    response = client.get("/api/v1/audits")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_audit():
    create_response = client.post("/api/v1/audits", json={"url": "https://example.com"})
    audit_id = create_response.json()["id"]

    response = client.get(f"/api/v1/audits/{audit_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == audit_id
    assert data["url"] == "https://example.com/"

def test_get_audit_not_found():
    response = client.get("/api/v1/audits/9999")
    assert response.status_code == 404
