"""
Tests for database models.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from app.models import Brand, Shop


class TestBrandModel:
    """Tests for the Brand model."""
    
    def test_brand_creation(self, test_db):
        """Brand model creates with valid data."""
        brand = Brand(
            name="Test Brand",
            name_zh="測試品牌",
            description="A test brand",
            origin_country="TW",
            website="https://example.com"
        )
        test_db.add(brand)
        test_db.commit()
        test_db.refresh(brand)
        
        assert brand.id is not None
        assert brand.name == "Test Brand"
        assert brand.name_zh == "測試品牌"
    
    def test_brand_name_required(self, test_db):
        """Brand requires name field."""
        brand = Brand(description="No name brand")
        test_db.add(brand)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_brand_name_unique(self, test_db):
        """Brand name must be unique."""
        brand1 = Brand(name="Unique Brand")
        test_db.add(brand1)
        test_db.commit()
        
        brand2 = Brand(name="Unique Brand")
        test_db.add(brand2)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_brand_optional_fields(self, test_db):
        """Brand optional fields can be null."""
        brand = Brand(name="Minimal Brand")
        test_db.add(brand)
        test_db.commit()
        test_db.refresh(brand)
        
        assert brand.name_zh is None
        assert brand.logo_url is None
        assert brand.description is None
        assert brand.origin_country is None
        assert brand.website is None


class TestShopModel:
    """Tests for the Shop model."""
    
    def test_shop_creation(self, test_db, sample_brand):
        """Shop model creates with valid data."""
        shop = Shop(
            name="Test Shop",
            brand_id=sample_brand.id,
            address="123 Test St",
            city="Test City",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
        )
        test_db.add(shop)
        test_db.commit()
        test_db.refresh(shop)
        
        assert shop.id is not None
        assert shop.name == "Test Shop"
        assert shop.brand_id == sample_brand.id
    
    def test_shop_brand_relationship(self, test_db, sample_shop, sample_brand):
        """Shop correctly references Brand."""
        assert sample_shop.brand is not None
        assert sample_shop.brand.id == sample_brand.id
        assert sample_shop.brand.name == sample_brand.name
    
    def test_brand_shops_relationship(self, test_db, sample_shop, sample_brand):
        """Brand has shops collection."""
        test_db.refresh(sample_brand)
        assert len(sample_brand.shops) >= 1
        assert sample_shop.id in [s.id for s in sample_brand.shops]
    
    def test_shop_without_brand(self, test_db):
        """Shop can exist without brand (independent shop)."""
        shop = Shop(
            name="Independent Shop",
            brand_id=None,
            address="456 Solo Ave",
            country="US",
            latitude=37.8000,
            longitude=-122.2700,
        )
        test_db.add(shop)
        test_db.commit()
        test_db.refresh(shop)
        
        assert shop.id is not None
        assert shop.brand_id is None
        assert shop.brand is None
    
    def test_shop_name_required(self, test_db):
        """Shop requires name field."""
        shop = Shop(
            address="123 Test St",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
        )
        test_db.add(shop)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_shop_address_required(self, test_db):
        """Shop requires address field."""
        shop = Shop(
            name="No Address Shop",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
        )
        test_db.add(shop)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_shop_country_required(self, test_db):
        """Shop requires country field."""
        shop = Shop(
            name="No Country Shop",
            address="123 Test St",
            latitude=37.7749,
            longitude=-122.4194,
        )
        test_db.add(shop)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_google_place_id_unique(self, test_db, sample_brand):
        """google_place_id must be unique."""
        shop1 = Shop(
            name="Shop 1",
            address="Address 1",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
            google_place_id="same_place_id",
        )
        test_db.add(shop1)
        test_db.commit()
        
        shop2 = Shop(
            name="Shop 2",
            address="Address 2",
            country="US",
            latitude=37.8000,
            longitude=-122.2700,
            google_place_id="same_place_id",  # Duplicate
        )
        test_db.add(shop2)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_google_place_id_nullable(self, test_db):
        """google_place_id can be null."""
        shop = Shop(
            name="No Place ID Shop",
            address="123 Test St",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
            google_place_id=None,
        )
        test_db.add(shop)
        test_db.commit()
        test_db.refresh(shop)
        
        assert shop.google_place_id is None
    
    def test_shop_status_default(self, test_db):
        """Shop status defaults to active."""
        shop = Shop(
            name="Default Status Shop",
            address="123 Test St",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
        )
        test_db.add(shop)
        test_db.commit()
        test_db.refresh(shop)
        
        assert shop.status == "active"
    
    def test_shop_status_values(self, test_db):
        """Shop status accepts valid values."""
        for status in ["active", "closed", "unverified"]:
            shop = Shop(
                name=f"Shop {status}",
                address="123 Test St",
                country="US",
                latitude=37.7749,
                longitude=-122.4194,
                status=status,
            )
            test_db.add(shop)
            test_db.commit()
            test_db.refresh(shop)
            assert shop.status == status
    
    def test_timestamps_auto_set(self, test_db):
        """created_at and updated_at auto-populate."""
        shop = Shop(
            name="Timestamp Shop",
            address="123 Test St",
            country="US",
            latitude=37.7749,
            longitude=-122.4194,
        )
        test_db.add(shop)
        test_db.commit()
        test_db.refresh(shop)
        
        assert shop.created_at is not None
        assert shop.updated_at is not None
        assert isinstance(shop.created_at, datetime)
        assert isinstance(shop.updated_at, datetime)
