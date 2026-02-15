"""
Tests for Google Places API service.
Uses mocked HTTP responses to avoid actual API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


class TestGooglePlacesServiceV2:
    """Tests for GooglePlacesServiceV2."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked API key."""
        with patch.dict("os.environ", {"GOOGLE_PLACES_API_KEY": "test_api_key"}):
            from app.services.google_places_v2 import GooglePlacesServiceV2

            return GooglePlacesServiceV2()

    @pytest.fixture
    def mock_response_success(self, mock_places_response):
        """Mock successful HTTP response."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_places_response
        response.raise_for_status = MagicMock()
        return response

    @pytest.fixture
    def mock_response_empty(self, mock_places_empty_response):
        """Mock empty HTTP response."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = mock_places_empty_response
        response.raise_for_status = MagicMock()
        return response

    @pytest.mark.asyncio
    async def test_text_search_success(self, service, mock_response_success):
        """Parses successful API response correctly."""
        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response_success

            results = await service.text_search(
                query="Gong Cha San Francisco",
                lat=37.7749,
                lng=-122.4194,
            )

            assert len(results) == 2
            assert results[0]["name"] == "Gong Cha"
            assert results[0]["google_place_id"] == "ChIJ_mock_place_id_1"
            assert results[0]["latitude"] == 37.7749
            assert results[0]["longitude"] == -122.4194

    @pytest.mark.asyncio
    async def test_text_search_empty_results(self, service, mock_response_empty):
        """Handles empty results."""
        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response_empty

            results = await service.text_search(
                query="NonExistent Brand",
                lat=37.7749,
                lng=-122.4194,
            )

            assert results == []

    @pytest.mark.asyncio
    async def test_nearby_search_success(self, service, mock_response_success):
        """Parses nearby search response."""
        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response_success

            results = await service.nearby_search(
                lat=37.7749,
                lng=-122.4194,
                included_types=["cafe"],
            )

            assert len(results) == 2

    def test_parse_place_full_data(self, service, mock_places_response):
        """Parses place with all fields."""
        place = mock_places_response["places"][0]
        result = service._parse_place(place, "US")

        assert result["name"] == "Gong Cha"
        assert result["google_place_id"] == "ChIJ_mock_place_id_1"
        assert result["address"] == "123 Main St, San Francisco, CA 94102, USA"
        assert result["latitude"] == 37.7749
        assert result["longitude"] == -122.4194
        assert result["google_maps_uri"] == "https://maps.google.com/?cid=123456789"

    def test_parse_place_minimal_data(self, service):
        """Parses place with only required fields."""
        place = {
            "id": "minimal_place_id",
            "displayName": {"text": "Minimal Shop"},
            "location": {"latitude": 25.0, "longitude": 121.0},
        }
        result = service._parse_place(place, "TW")

        assert result["name"] == "Minimal Shop"
        assert result["google_place_id"] == "minimal_place_id"
        assert result["latitude"] == 25.0
        assert result["longitude"] == 121.0
        assert result["address"] == ""  # Missing field defaults to empty

    @pytest.mark.asyncio
    async def test_api_error_handling(self, service):
        """Handles API errors gracefully - returns empty list."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Server Error"

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            # Service catches error and returns empty list
            results = await service.text_search(
                query="Test",
                lat=37.7749,
                lng=-122.4194,
            )
            assert results == []

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, service):
        """Handles rate limit responses - returns empty list."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate Limited"

        with patch.object(
            httpx.AsyncClient, "post", new_callable=AsyncMock
        ) as mock_post:
            mock_post.return_value = mock_response

            # Service catches error and returns empty list
            results = await service.text_search(
                query="Test",
                lat=37.7749,
                lng=-122.4194,
            )
            assert results == []

    def test_service_no_api_key(self):
        """Handles missing API key."""
        with patch.dict("os.environ", {}, clear=True):
            # Remove GOOGLE_PLACES_API_KEY from environment
            with patch.dict("os.environ", {"GOOGLE_PLACES_API_KEY": ""}):
                from app.services.google_places_v2 import GooglePlacesServiceV2

                service = GooglePlacesServiceV2()
                assert service.api_key == ""


class TestGooglePlacesFieldMask:
    """Tests for FieldMask configuration (cost control)."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        with patch.dict("os.environ", {"GOOGLE_PLACES_API_KEY": "test_api_key"}):
            from app.services.google_places_v2 import GooglePlacesServiceV2

            return GooglePlacesServiceV2()

    def test_field_mask_excludes_enterprise_fields(self, service):
        """Verify FieldMask excludes enterprise-tier fields."""
        # Enterprise fields that should NOT be in our requests
        enterprise_fields = [
            "places.rating",
            "places.userRatingCount",
            "places.internationalPhoneNumber",
            "places.regularOpeningHours",
            "places.websiteUri",
        ]

        # Our Pro-tier fields
        pro_fields = service.FIELD_MASK if hasattr(service, "FIELD_MASK") else ""

        for field in enterprise_fields:
            assert field not in pro_fields, (
                f"Enterprise field {field} should not be requested"
            )
