"""
Google Places API integration for fetching boba shop data.

To use this service, you need:
1. A Google Cloud project with Places API enabled
2. An API key with Places API access
3. Set GOOGLE_PLACES_API_KEY in your .env file

Usage:
    from app.services.google_places import GooglePlacesService

    service = GooglePlacesService()
    shops = await service.search_boba_shops("Taipei", "TW")
"""

import os
from typing import Optional

import httpx


class GooglePlacesService:
    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            print(
                "Warning: GOOGLE_PLACES_API_KEY not set. "
                "Google Places features disabled."
            )

    async def search_boba_shops(
        self, location: str, country: str = "TW", radius_meters: int = 5000
    ) -> list[dict]:
        """
        Search for boba shops near a location.

        Args:
            location: City or address to search near
            country: Country code (TW, US)
            radius_meters: Search radius in meters

        Returns:
            List of shop data dicts
        """
        if not self.api_key:
            return []

        # First, geocode the location
        coords = await self._geocode(f"{location}, {country}")
        if not coords:
            return []

        # Search for boba shops
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/nearbysearch/json",
                params={
                    "location": f"{coords['lat']},{coords['lng']}",
                    "radius": radius_meters,
                    "keyword": "boba bubble tea",
                    "type": "cafe",
                    "key": self.api_key,
                },
            )
            data = response.json()

            shops = []
            for place in data.get("results", []):
                shops.append(self._parse_place(place, country))

            return shops

    async def text_search(
        self, query: str, region: str = "tw", location: str = None
    ) -> list[dict]:
        """
        Search places by text query (e.g., '50嵐 台北').
        Better for brand-specific searches.

        Args:
            query: Text query like "50嵐 台北" or "CoCo 高雄"
            region: Region bias (tw, us)
            location: Optional "lat,lng" to bias results

        Returns:
            List of shop data dicts
        """
        if not self.api_key:
            return []

        params = {"query": query, "region": region, "key": self.api_key}

        if location:
            params["location"] = location
            params["radius"] = 50000  # 50km radius

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/textsearch/json", params=params
            )
            data = response.json()

            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(
                    f"Text search error: {data.get('status')} - "
                    f"{data.get('error_message', '')}"
                )
                return [], None

            shops = []
            for place in data.get("results", []):
                country = "TW" if region == "tw" else "US"
                shops.append(self._parse_place(place, country))

            # Handle pagination if there are more results
            next_token = data.get("next_page_token")

            return shops, next_token

    async def text_search_all_pages(
        self, query: str, region: str = "tw", max_results: int = 60
    ) -> list[dict]:
        """
        Search with pagination, up to max_results.
        """
        import asyncio

        all_shops = []
        next_token = None

        while len(all_shops) < max_results:
            if next_token:
                # Must wait 2 seconds before using next_page_token
                await asyncio.sleep(2)
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.BASE_URL}/textsearch/json",
                        params={"pagetoken": next_token, "key": self.api_key},
                    )
                    data = response.json()

                    for place in data.get("results", []):
                        country = "TW" if region == "tw" else "US"
                        all_shops.append(self._parse_place(place, country))

                    next_token = data.get("next_page_token")
            else:
                shops, next_token = await self.text_search(query, region)
                all_shops.extend(shops)

            if not next_token:
                break

        return all_shops[:max_results]

    async def nearby_search(
        self,
        lat: float,
        lng: float,
        keyword: str,
        radius_meters: int = 25000,
        country: str = "TW",
    ) -> tuple[list[dict], str]:
        """
        Search for places near a specific location.
        Better for systematic grid coverage.

        Args:
            lat: Latitude of search center
            lng: Longitude of search center
            keyword: Search keyword (brand name)
            radius_meters: Search radius (max 50000)
            country: Country code for result parsing

        Returns:
            Tuple of (shops list, next_page_token)
        """
        if not self.api_key:
            return [], None

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/nearbysearch/json",
                params={
                    "location": f"{lat},{lng}",
                    "radius": radius_meters,
                    "keyword": keyword,
                    "key": self.api_key,
                },
            )
            data = response.json()

            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                print(
                    f"Nearby search error: {data.get('status')} - "
                    f"{data.get('error_message', '')}"
                )
                return [], None

            shops = []
            for place in data.get("results", []):
                shops.append(self._parse_place(place, country))

            next_token = data.get("next_page_token")
            return shops, next_token

    async def nearby_search_all_pages(
        self,
        lat: float,
        lng: float,
        keyword: str,
        radius_meters: int = 25000,
        country: str = "TW",
        max_results: int = 60,
    ) -> list[dict]:
        """
        Nearby search with pagination, up to max_results (max 60).
        """
        import asyncio

        all_shops = []
        next_token = None

        while len(all_shops) < max_results:
            if next_token:
                await asyncio.sleep(2)  # Required wait before using page token
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.BASE_URL}/nearbysearch/json",
                        params={"pagetoken": next_token, "key": self.api_key},
                    )
                    data = response.json()

                    for place in data.get("results", []):
                        all_shops.append(self._parse_place(place, country))

                    next_token = data.get("next_page_token")
            else:
                shops, next_token = await self.nearby_search(
                    lat, lng, keyword, radius_meters, country
                )
                all_shops.extend(shops)

            if not next_token:
                break

        return all_shops[:max_results]

    async def get_place_details(self, place_id: str) -> Optional[dict]:
        """Get detailed info about a specific place"""
        if not self.api_key:
            return None

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/details/json",
                params={
                    "place_id": place_id,
                    "fields": (
                        "name,formatted_address,geometry,rating,user_ratings_total,"
                        "formatted_phone_number,opening_hours,photos"
                    ),
                    "key": self.api_key,
                },
            )
            data = response.json()

            if data.get("status") == "OK":
                return data.get("result")
            return None

    async def _geocode(self, address: str) -> Optional[dict]:
        """Convert address to coordinates"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": address, "key": self.api_key},
            )
            data = response.json()

            if data.get("results"):
                location = data["results"][0]["geometry"]["location"]
                return {"lat": location["lat"], "lng": location["lng"]}
            return None

    def _parse_place(self, place: dict, country: str) -> dict:
        """Parse Google Places result into our shop format"""
        location = place.get("geometry", {}).get("location", {})

        return {
            "name": place.get("name"),
            "address": place.get("vicinity") or place.get("formatted_address"),
            "country": country,
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "rating": place.get("rating"),
            "rating_count": place.get("user_ratings_total"),
            "google_place_id": place.get("place_id"),
            "photo_url": self._get_photo_url(place) if place.get("photos") else None,
        }

    def _get_photo_url(self, place: dict) -> Optional[str]:
        """Generate photo URL from place data"""
        photos = place.get("photos", [])
        if photos and self.api_key:
            photo_ref = photos[0].get("photo_reference")
            return (
                f"{self.BASE_URL}/photo?maxwidth=400&photo_reference={photo_ref}"
                f"&key={self.api_key}"
            )
        return None
