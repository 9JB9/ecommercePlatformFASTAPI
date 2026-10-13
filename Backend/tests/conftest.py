import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR)) # so main/models/database are importable when pytest runs from anywhere

import database

# swap in an in-memory database BEFORE main is imported, main's create_all must never touch my_database.db
# StaticPool keeps one shared connection, otherwise every new connection would get its own empty in-memory db
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
database.engine = test_engine
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

import main
import models

PASSWORD = "password123"


def get_test_db():
    with TestSession() as db:
        yield db


@pytest.fixture
def db():
    # fresh tables for every test so tests can't leak data into each other
    database.Base.metadata.create_all(bind=test_engine)
    with TestSession() as session:
        yield session
    database.Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db):
    main.app.dependency_overrides[database.get_db] = get_test_db
    with TestClient(main.app) as test_client:
        yield test_client
    main.app.dependency_overrides.clear()


@pytest.fixture
def product(db):
    shoe = models.Product(
        name="Test Shoe", price=159.99, image_url="x", gender="men", link="x", brand="B", description="d"
    )
    db.add(shoe)
    db.commit()
    db.refresh(shoe)
    return shoe


def register_and_login(client, email: str) -> dict:
    """Create a user through the API and return headers carrying their token."""
    assert client.post("/api/users", json={"email": email, "password": PASSWORD}).status_code == 201
    response = client.post("/api/users/token", data={"username": email, "password": PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def user_headers(client):
    return register_and_login(client, "customer@example.com")


@pytest.fixture
def admin_headers(client, db):
    headers = register_and_login(client, "admin@example.com")
    # promoted directly in the db, the same way make_admin.py does, the api has no way to do this
    admin = db.execute(select(models.User).where(models.User.email == "admin@example.com")).scalars().one()
    admin.is_admin = True
    db.commit()
    return headers


def place_order(client, headers: dict, product_id: int) -> dict:
    """Add one product to the cart and check out, returns the order json."""
    assert client.post("/api/cart", json={"product_id": product_id}, headers=headers).status_code == 201
    response = client.post("/api/orders", headers=headers)
    assert response.status_code == 201
    return response.json()
