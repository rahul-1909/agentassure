"""Pytest Test Configuration and Fixtures for AgentAssure."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agentassure.api.app import app
from agentassure.db.base import Base
from agentassure.db.seed_data import seed_database
from agentassure.db.session import get_db
from agentassure.utils.security import create_access_token


@pytest.fixture(scope="session")
def engine():
    """Create in-memory SQLite database engine for testing."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=test_engine)
    return test_engine


@pytest.fixture(scope="function")
def db_session(engine):
    """Provide isolated transactional database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocalTest = sessionmaker(bind=connection, expire_on_commit=False)
    session = SessionLocalTest()

    # Seed baseline data
    seed_database(session)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers():
    """Provide valid JWT bearer token headers for testing."""
    token = create_access_token(data={"sub": "test-admin-id", "username": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}
