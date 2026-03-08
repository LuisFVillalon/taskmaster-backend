"""Pytest configuration and shared fixtures for TaskMaster tests."""
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    yield


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create session for test to use if needed
    session = TestingSessionLocal()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Create FastAPI test client with overridden database."""
    from fastapi.testclient import TestClient
    return TestClient(app)


# Pytest configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "validation: mark test as a validation test"
    )
    config.addinivalue_line(
        "markers", "hierarchy: mark test as testing task hierarchy"
    )


# Collection modifiers
def pytest_collection_modifyitems(config, items):
    """Automatically add markers to test items based on their names."""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "validation" in item.nodeid or "validate" in item.nodeid:
            item.add_marker(pytest.mark.validation)
        if "hierarchy" in item.nodeid.lower():
            item.add_marker(pytest.mark.hierarchy)
