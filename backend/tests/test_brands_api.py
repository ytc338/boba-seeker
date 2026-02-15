"""
Tests for the Brands API endpoints.
"""

import pytest


class TestListBrands:
    """Tests for GET /api/brands"""

    def test_list_brands_empty(self, client):
        """Returns empty list when no brands exist."""
        response = client.get("/api/brands")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_brands_returns_all(self, client, sample_brands):
        """Returns all brands."""
        response = client.get("/api/brands")
        assert response.status_code == 200
        brands = response.json()
        assert len(brands) == 3

    def test_list_brands_filter_country_with_shops(
        self, client, sample_shops, sample_brands
    ):
        """Filter by country returns brands with shops in that country."""
        response = client.get("/api/brands", params={"country": "US"})
        assert response.status_code == 200
        brands = response.json()
        # Gong Cha (US shops), Tiger Sugar (US shop), Boba Guys (US shop)
        assert len(brands) == 3
        brand_names = [b["name"] for b in brands]
        assert "Gong Cha" in brand_names
        assert "Tiger Sugar" in brand_names
        assert "Boba Guys" in brand_names

    def test_list_brands_filter_country_tw(self, client, sample_shops, sample_brands):
        """Filter by Taiwan country."""
        response = client.get("/api/brands", params={"country": "TW"})
        assert response.status_code == 200
        brands = response.json()
        # Only Gong Cha has a shop in TW
        assert len(brands) == 1
        assert brands[0]["name"] == "Gong Cha"

    def test_list_brands_filter_country_no_shops(self, client, sample_brands):
        """Filter by country with no shops returns empty."""
        response = client.get("/api/brands", params={"country": "JP"})
        assert response.status_code == 200
        assert response.json() == []

    def test_list_brands_includes_all_fields(self, client, sample_brands):
        """Returns all brand fields."""
        response = client.get("/api/brands")
        assert response.status_code == 200
        brands = response.json()
        gong_cha = next(b for b in brands if b["name"] == "Gong Cha")
        assert "id" in gong_cha
        assert gong_cha["name_zh"] == "貢茶"
        assert gong_cha["description"] == "International boba chain"
        assert gong_cha["origin_country"] == "TW"


class TestGetBrand:
    """Tests for GET /api/brands/{brand_id}"""

    def test_get_brand_exists(self, client, sample_brand):
        """Returns brand when ID exists."""
        response = client.get(f"/api/brands/{sample_brand.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_brand.id
        assert data["name"] == sample_brand.name
        assert data["name_zh"] == sample_brand.name_zh

    def test_get_brand_not_found(self, client):
        """Returns 404 when brand doesn't exist."""
        response = client.get("/api/brands/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Brand not found"


class TestCreateBrand:
    """Tests for POST /api/brands"""

    def test_create_brand_success(self, client):
        """Creates brand with valid data."""
        brand_data = {
            "name": "New Boba Brand",
            "name_zh": "新品牌",
            "description": "A new test brand",
            "origin_country": "TW",
            "website": "https://newboba.example.com",
        }
        response = client.post("/api/brands", json=brand_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Boba Brand"
        assert data["id"] is not None

    def test_create_brand_minimal(self, client):
        """Creates brand with only required fields."""
        brand_data = {"name": "Minimal Brand"}
        response = client.post("/api/brands", json=brand_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Brand"
        assert data["name_zh"] is None
        assert data["description"] is None

    def test_create_brand_missing_name(self, client):
        """Validates name is required."""
        brand_data = {"description": "Missing name"}
        response = client.post("/api/brands", json=brand_data)
        assert response.status_code == 422

    def test_create_brand_duplicate_name(self, client, sample_brand):
        """Handles duplicate brand names - raises IntegrityError."""
        from sqlalchemy.exc import IntegrityError

        brand_data = {
            "name": sample_brand.name  # Try to create duplicate
        }
        # SQLAlchemy raises IntegrityError for duplicate unique constraint
        # In production, this should be handled with a proper 409 Conflict
        with pytest.raises(IntegrityError):
            client.post("/api/brands", json=brand_data)
