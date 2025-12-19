"""
Google Places API (New) integration for fetching boba shop data.
Uses the new API with FieldMask to REQUEST ONLY PRO-TIER FIELDS (cheapest).

Pricing (as of 2024):
- Pro SKU: $6.40 per 1,000 requests (fields: displayName, location, address, id, types)
- Enterprise SKU: +$$ for rating, phone, hours, website
- Starting March 2025: 5,000 free Pro calls/month

To minimize cost, we ONLY request Pro fields:
- places.id
- places.displayName
- places.formattedAddress
- places.location
- places.types

We explicitly EXCLUDE (Enterprise tier, costs extra):
- places.rating
- places.userRatingCount
- places.internationalPhoneNumber
- places.regularOpeningHours
- places.websiteUri
"""

import os
import httpx
from typing import Optional


class GooglePlacesServiceV2:
    """
    New Places API service using FieldMask for cost control.
    Only requests Pro-tier fields to minimize billing.
    """
    
    BASE_URL = "https://places.googleapis.com/v1"
    
    # MINIMAL Pro-tier fields only (cheapest)
    # All these are in Pro tier - no Enterprise charges
    # Excludes: rating, userRatingCount, phone, hours, website, photos (Enterprise/extra cost)
    FIELD_MASK = "places.id,places.displayName,places.formattedAddress,places.location,places.googleMapsUri"
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            print("Warning: GOOGLE_PLACES_API_KEY not set. Google Places features disabled.")
    
    async def nearby_search(
        self,
        lat: float,
        lng: float,
        keyword: str = None,
        included_types: list[str] = None,
        radius_meters: int = 15000,
        max_results: int = 20,
        country: str = "US"
    ) -> list[dict]:
        """
        Search for places near a location using the new API.
        Uses FieldMask to only request Pro-tier fields (cheapest).
        
        Args:
            lat: Latitude of search center
            lng: Longitude of search center
            keyword: Text query to filter results (e.g., "boba tea", "Tiger Sugar")
            included_types: Place types to include (e.g., ["cafe", "restaurant"])
            radius_meters: Search radius (max 50000)
            max_results: Max results to return (max 20 per request)
            country: Country code for result parsing
            
        Returns:
            List of shop data dicts
        """
        if not self.api_key:
            return []
        
        # Build request body
        body = {
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": float(radius_meters)
                }
            },
            "maxResultCount": min(max_results, 20)  # API max is 20
        }
        
        # Add keyword as text query if provided
        if keyword:
            body["textQuery"] = keyword
        
        # Add place types if provided
        if included_types:
            body["includedTypes"] = included_types
        
        # Add language for better results
        body["languageCode"] = "en"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/places:searchNearby",
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": self.FIELD_MASK
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"Nearby search error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            shops = []
            for place in data.get("places", []):
                shops.append(self._parse_place(place, country))
            
            return shops
    
    async def text_search(
        self,
        query: str,
        lat: float = None,
        lng: float = None,
        radius_meters: int = 50000,
        max_results: int = 20,
        country: str = "US"
    ) -> list[dict]:
        """
        Search for places by text query using the new API.
        Uses FieldMask to only request Pro-tier fields (cheapest).
        
        Args:
            query: Text query (e.g., "Boba Guys San Francisco")
            lat: Optional latitude to bias results
            lng: Optional longitude to bias results
            radius_meters: Search radius if lat/lng provided
            max_results: Max results to return (max 20)
            country: Country code for result parsing
            
        Returns:
            List of shop data dicts
        """
        if not self.api_key:
            return []
        
        body = {
            "textQuery": query,
            "maxResultCount": min(max_results, 20),
            "languageCode": "en"
        }
        
        # Add location bias if coordinates provided
        if lat is not None and lng is not None:
            body["locationBias"] = {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": float(radius_meters)
                }
            }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/places:searchText",
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                    "X-Goog-FieldMask": self.FIELD_MASK
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"Text search error: {response.status_code} - {response.text}")
                return []
            
            data = response.json()
            
            shops = []
            for place in data.get("places", []):
                shops.append(self._parse_place(place, country))
            
            return shops
    
    async def nearby_search_with_keyword(
        self,
        lat: float,
        lng: float,
        keyword: str,
        radius_meters: int = 15000,
        country: str = "US"
    ) -> list[dict]:
        """
        Search for places near a location with a keyword filter.
        Uses Text Search internally since Nearby Search doesn't support textQuery.
        
        This is the main method for brand-specific imports.
        """
        # Nearby Search (New) doesn't support textQuery/keyword directly
        # Use Text Search with location bias instead
        return await self.text_search(
            query=keyword,
            lat=lat,
            lng=lng,
            radius_meters=radius_meters,
            max_results=20,
            country=country
        )
    
    def _parse_place(self, place: dict, country: str) -> dict:
        """Parse Places API (New) response into our shop format."""
        
        # Extract location
        location = place.get("location", {})
        lat = location.get("latitude")
        lng = location.get("longitude")
        
        # Extract display name
        display_name = place.get("displayName", {})
        name = display_name.get("text", "Unknown")
        
        # Extract ID
        place_id = place.get("id", "")
        
        # Google Maps URI for directions (FREE in Pro tier)
        google_maps_uri = place.get("googleMapsUri", "")
        
        return {
            "name": name,
            "address": place.get("formattedAddress", ""),
            "country": country,
            "latitude": lat,
            "longitude": lng,
            # NOT requesting these (Enterprise tier = costs extra)
            "rating": None,
            "rating_count": None,
            "google_place_id": place_id,
            # Google Maps link for directions (FREE)
            "google_maps_uri": google_maps_uri,
            # Not requesting photos (extra cost)
            "photo_url": None
        }


# Convenience function to test the service
async def test_nearby_search():
    """Test the new API with a sample search."""
    service = GooglePlacesServiceV2()
    
    # Test: Search for boba in San Francisco
    results = await service.text_search(
        query="boba tea",
        lat=37.7749,
        lng=-122.4194,
        radius_meters=5000
    )
    
    print(f"Found {len(results)} results:")
    for shop in results[:5]:
        print(f"  - {shop['name']}: {shop['address']}")
    
    return results


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_nearby_search())
