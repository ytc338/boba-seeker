"""
Tests for the Shops API endpoints.
"""


class TestListShops:
    """Tests for GET /api/shops"""

    def test_list_shops_empty(self, client):
        """Returns empty list when no shops exist."""
        response = client.get("/api/shops")
        assert response.status_code == 200
        data = response.json()
        assert data["shops"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_shops_returns_shops(self, client, sample_shops):
        """Returns shops when they exist."""
        response = client.get("/api/shops")
        assert response.status_code == 200
        data = response.json()
        assert len(data["shops"]) == 4
        assert data["total"] == 4

    def test_list_shops_pagination_page(self, client, sample_shops):
        """Pagination returns correct page."""
        response = client.get("/api/shops", params={"page": 1, "page_size": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["shops"]) == 2
        assert data["total"] == 4
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_list_shops_pagination_page_2(self, client, sample_shops):
        """Second page returns remaining shops."""
        response = client.get("/api/shops", params={"page": 2, "page_size": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["shops"]) == 2
        assert data["page"] == 2

    def test_list_shops_filter_country_us(self, client, sample_shops):
        """Filter by country returns only US shops."""
        response = client.get("/api/shops", params={"country": "US"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for shop in data["shops"]:
            assert shop["country"] == "US"

    def test_list_shops_filter_country_tw(self, client, sample_shops):
        """Filter by country returns only Taiwan shops."""
        response = client.get("/api/shops", params={"country": "TW"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["shops"][0]["country"] == "TW"

    def test_list_shops_filter_city(self, client, sample_shops):
        """Filter by city returns only matching shops."""
        response = client.get("/api/shops", params={"city": "San Francisco"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for shop in data["shops"]:
            assert shop["city"] == "San Francisco"

    def test_list_shops_filter_brand(self, client, sample_shops, sample_brands):
        """Filter by brand_id returns only matching shops."""
        brand_id = sample_brands[0].id  # Gong Cha
        response = client.get("/api/shops", params={"brand_id": brand_id})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # Gong Cha has 2 shops
        for shop in data["shops"]:
            assert shop["brand_id"] == brand_id


class TestSearchShops:
    """Tests for GET /api/shops/search"""

    def test_search_shops_by_name(self, client, sample_shops):
        """Search finds shops by name."""
        response = client.get("/api/shops/search", params={"q": "Gong Cha"})
        assert response.status_code == 200
        shops = response.json()
        assert len(shops) >= 1
        assert any("Gong Cha" in shop["name"] for shop in shops)

    def test_search_shops_by_name_case_insensitive(self, client, sample_shops):
        """Search is case insensitive."""
        response = client.get("/api/shops/search", params={"q": "gong cha"})
        assert response.status_code == 200
        shops = response.json()
        assert len(shops) >= 1

    def test_search_shops_by_address(self, client, sample_shops):
        """Search finds shops by address."""
        response = client.get("/api/shops/search", params={"q": "Market"})
        assert response.status_code == 200
        shops = response.json()
        assert len(shops) >= 1

    def test_search_shops_no_results(self, client, sample_shops):
        """Search returns empty list when no matches."""
        response = client.get("/api/shops/search", params={"q": "NonExistent"})
        assert response.status_code == 200
        shops = response.json()
        assert shops == []

    def test_search_shops_with_limit(self, client, sample_shops):
        """Search respects limit parameter."""
        response = client.get("/api/shops/search", params={"q": "a", "limit": 2})
        assert response.status_code == 200
        shops = response.json()
        assert len(shops) <= 2

    def test_search_shops_min_query_length(self, client):
        """Validates minimum query length."""
        response = client.get("/api/shops/search", params={"q": ""})
        assert response.status_code == 422  # Validation error


class TestNearbyShops:
    """Tests for GET /api/shops/nearby"""

    def test_nearby_shops_returns_results(self, client, sample_shops):
        """Returns shops within radius."""
        # SF coordinates
        response = client.get(
            "/api/shops/nearby",
            params={"lat": 37.7749, "lng": -122.4194, "radius_km": 10},
        )
        assert response.status_code == 200
        shops = response.json()
        # Should find SF and Oakland shops
        assert len(shops) >= 2

    def test_nearby_shops_filters_by_distance(self, client, sample_shops):
        """Filters out shops beyond radius."""
        # SF coordinates with small radius
        response = client.get(
            "/api/shops/nearby",
            params={"lat": 37.7749, "lng": -122.4194, "radius_km": 1},
        )
        assert response.status_code == 200
        shops = response.json()
        # Should only find very nearby SF shops
        for shop in shops:
            assert shop["city"] in ["San Francisco"]

    def test_nearby_shops_empty_area(self, client, sample_shops):
        """Returns empty list when no shops nearby."""
        # Middle of Pacific Ocean
        response = client.get(
            "/api/shops/nearby", params={"lat": 0.0, "lng": -140.0, "radius_km": 5}
        )
        assert response.status_code == 200
        shops = response.json()
        assert shops == []

    def test_nearby_shops_lat_validation_min(self, client):
        """Validates latitude minimum value."""
        response = client.get(
            "/api/shops/nearby", params={"lat": -91, "lng": 0, "radius_km": 5}
        )
        assert response.status_code == 422

    def test_nearby_shops_lat_validation_max(self, client):
        """Validates latitude maximum value."""
        response = client.get(
            "/api/shops/nearby", params={"lat": 91, "lng": 0, "radius_km": 5}
        )
        assert response.status_code == 422

    def test_nearby_shops_lng_validation_min(self, client):
        """Validates longitude minimum value."""
        response = client.get(
            "/api/shops/nearby", params={"lat": 0, "lng": -181, "radius_km": 5}
        )
        assert response.status_code == 422

    def test_nearby_shops_lng_validation_max(self, client):
        """Validates longitude maximum value."""
        response = client.get(
            "/api/shops/nearby", params={"lat": 0, "lng": 181, "radius_km": 5}
        )
        assert response.status_code == 422

    def test_nearby_shops_radius_validation_min(self, client):
        """Validates radius minimum value."""
        response = client.get(
            "/api/shops/nearby",
            params={"lat": 37.7749, "lng": -122.4194, "radius_km": 0.05},
        )
        assert response.status_code == 422

    def test_nearby_shops_radius_validation_max(self, client):
        """Validates radius maximum value."""
        response = client.get(
            "/api/shops/nearby",
            params={"lat": 37.7749, "lng": -122.4194, "radius_km": 51},
        )
        assert response.status_code == 422


class TestGetShop:
    """Tests for GET /api/shops/{shop_id}"""

    def test_get_shop_exists(self, client, sample_shop):
        """Returns shop when ID exists."""
        response = client.get(f"/api/shops/{sample_shop.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_shop.id
        assert data["name"] == sample_shop.name
        assert data["address"] == sample_shop.address

    def test_get_shop_includes_brand(self, client, sample_shop, sample_brand):
        """Returns shop with brand information."""
        response = client.get(f"/api/shops/{sample_shop.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["brand"] is not None
        assert data["brand"]["name"] == sample_brand.name

    def test_get_shop_not_found(self, client):
        """Returns 404 when shop doesn't exist."""
        response = client.get("/api/shops/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Shop not found"


class TestCreateShop:
    """Tests for POST /api/shops"""

    def test_create_shop_success(self, client, sample_brand):
        """Creates shop with valid data."""
        shop_data = {
            "name": "New Test Shop",
            "brand_id": sample_brand.id,
            "address": "789 New St, San Francisco, CA",
            "city": "San Francisco",
            "country": "US",
            "latitude": 37.7850,
            "longitude": -122.4000,
        }
        response = client.post("/api/shops", json=shop_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Shop"
        assert data["id"] is not None

    def test_create_shop_without_brand(self, client):
        """Creates shop without brand (independent shop)."""
        shop_data = {
            "name": "Independent Shop",
            "address": "999 Solo Ave, Oakland, CA",
            "country": "US",
            "latitude": 37.8000,
            "longitude": -122.2700,
        }
        response = client.post("/api/shops", json=shop_data)
        assert response.status_code == 201
        data = response.json()
        assert data["brand_id"] is None

    def test_create_shop_missing_required_fields(self, client):
        """Validates required fields."""
        shop_data = {
            "name": "Missing Fields Shop",
            # Missing address, country, latitude, longitude
        }
        response = client.post("/api/shops", json=shop_data)
        assert response.status_code == 422

    def test_create_shop_with_optional_fields(self, client, sample_brand):
        """Creates shop with all optional fields."""
        shop_data = {
            "name": "Full Test Shop",
            "brand_id": sample_brand.id,
            "address": "100 Full St, San Francisco, CA",
            "city": "San Francisco",
            "country": "US",
            "latitude": 37.7750,
            "longitude": -122.4100,
            "rating": 4.8,
            "rating_count": 250,
            "phone": "+1-555-123-4567",
            "hours": '{"monday": "9am-9pm"}',
            "photo_url": "https://example.com/photo.jpg",
            "google_place_id": "unique_place_id_123",
        }
        response = client.post("/api/shops", json=shop_data)
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 4.8
        assert data["phone"] == "+1-555-123-4567"
        assert data["google_place_id"] == "unique_place_id_123"
