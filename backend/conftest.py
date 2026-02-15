"""
Pytest fixtures for Boba Seeker backend tests.
Provides test database, sessions, sample data, and mock utilities.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import Brand, Shop
from main import app


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(test_engine, test_db):
    """Create a FastAPI test client with test database."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_brand(test_db) -> Brand:
    """Create a sample brand for testing."""
    brand = Brand(
        name="Test Boba",
        name_zh="測試珍珠",
        description="A test boba brand",
        origin_country="TW",
        website="https://testboba.example.com",
    )
    test_db.add(brand)
    test_db.commit()
    test_db.refresh(brand)
    return brand


@pytest.fixture
def sample_brands(test_db) -> list[Brand]:
    """Create multiple sample brands for testing."""
    brands = [
        Brand(
            name="Gong Cha",
            name_zh="貢茶",
            description="International boba chain",
            origin_country="TW",
        ),
        Brand(
            name="Tiger Sugar",
            name_zh="老虎堂",
            description="Famous for brown sugar boba",
            origin_country="TW",
        ),
        Brand(
            name="Boba Guys",
            name_zh="Boba Guys",
            description="SF-based artisan boba",
            origin_country="US",
        ),
    ]
    for brand in brands:
        test_db.add(brand)
    test_db.commit()
    for brand in brands:
        test_db.refresh(brand)
    return brands


@pytest.fixture
def sample_shop(test_db, sample_brand) -> Shop:
    """Create a sample shop for testing."""
    shop = Shop(
        name="Test Shop Downtown",
        brand_id=sample_brand.id,
        address="123 Test Street, San Francisco, CA 94102",
        city="San Francisco",
        country="US",
        latitude=37.7749,
        longitude=-122.4194,
        rating=4.5,
        rating_count=100,
        google_place_id="test_place_id_123",
        status="active",
        last_verified=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
    )
    test_db.add(shop)
    test_db.commit()
    test_db.refresh(shop)
    return shop


@pytest.fixture
def sample_shops(test_db, sample_brands) -> list[Shop]:
    """Create multiple sample shops for testing."""
    shops = [
        # San Francisco shops
        Shop(
            name="Gong Cha SF Downtown",
            brand_id=sample_brands[0].id,
            address="100 Market St, San Francisco, CA",
            city="San Francisco",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
            google_place_id="gongcha_sf_1",
            status="active",
        ),
        Shop(
            name="Tiger Sugar SF",
            brand_id=sample_brands[1].id,
            address="200 Powell St, San Francisco, CA",
            city="San Francisco",
            country="US",
            latitude=37.7855,
            longitude=-122.4079,
            google_place_id="tigersugar_sf_1",
            status="active",
        ),
        # Taipei shops
        Shop(
            name="貢茶 台北店",
            brand_id=sample_brands[0].id,
            address="台北市信義區松高路",
            city="Taipei",
            country="TW",
            latitude=25.0330,
            longitude=121.5654,
            google_place_id="gongcha_tw_1",
            status="active",
        ),
        # Oakland shop (different city, near SF)
        Shop(
            name="Boba Guys Oakland",
            brand_id=sample_brands[2].id,
            address="300 Broadway, Oakland, CA",
            city="Oakland",
            country="US",
            latitude=37.8044,
            longitude=-122.2712,
            google_place_id="bobaguys_oak_1",
            status="active",
        ),
    ]
    for shop in shops:
        test_db.add(shop)
    test_db.commit()
    for shop in shops:
        test_db.refresh(shop)
    return shops


# ============================================================================
# Mock Data for Google Places API
# ============================================================================


@pytest.fixture
def mock_places_response():
    """Sample Google Places API (New) response."""
    return {
        "places": [
            {
                "id": "ChIJ_mock_place_id_1",
                "displayName": {"text": "Gong Cha", "languageCode": "en"},
                "formattedAddress": "123 Main St, San Francisco, CA 94102, USA",
                "location": {"latitude": 37.7749, "longitude": -122.4194},
                "googleMapsUri": "https://maps.google.com/?cid=123456789",
                "types": ["cafe", "bubble_tea_store"],
            },
            {
                "id": "ChIJ_mock_place_id_2",
                "displayName": {"text": "Tiger Sugar SF", "languageCode": "en"},
                "formattedAddress": "456 Market St, San Francisco, CA 94103, USA",
                "location": {"latitude": 37.7855, "longitude": -122.4079},
                "googleMapsUri": "https://maps.google.com/?cid=987654321",
                "types": ["restaurant", "bubble_tea_store"],
            },
        ]
    }


@pytest.fixture
def mock_places_empty_response():
    """Empty Google Places API response."""
    return {"places": []}


@pytest.fixture
def mock_places_error_response():
    """Google Places API error response."""
    return {
        "error": {
            "code": 400,
            "message": "Invalid request",
            "status": "INVALID_ARGUMENT",
        }
    }
