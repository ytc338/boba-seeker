"""
Bay Area Boba Import Experiment
Tests the new Places API (New) with minimal Pro-tier fields.

This is a cost experiment to verify:
1. API works with minimal FieldMask
2. We get name, address, location, Google Maps link
3. No Enterprise charges

Usage:
    python test_bayarea_import.py --dry-run
    python test_bayarea_import.py
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime, timezone

# Load environment variables
from dotenv import load_dotenv
load_dotenv("../.env")

sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app.models import Brand, Shop
from app.services.google_places_v2 import GooglePlacesServiceV2

# Create/update tables
Base.metadata.create_all(bind=engine)

# Bay Area grid points
BAY_AREA_GRID = [
    {"name": "San Francisco (Downtown)", "lat": 37.7749, "lng": -122.4194},
    {"name": "San Francisco (Sunset)", "lat": 37.7587, "lng": -122.4757},
    {"name": "Berkeley", "lat": 37.8715, "lng": -122.2730},
    {"name": "Oakland (Chinatown)", "lat": 37.8044, "lng": -122.2712},
    {"name": "San Jose (Downtown)", "lat": 37.3382, "lng": -121.8863},
    {"name": "Cupertino", "lat": 37.3230, "lng": -122.0322},
]

# Test brands - just a few for the experiment
TEST_BRANDS = [
    {"name": "Boba Guys", "name_zh": "Boba Guys", "description": "SF-based artisan boba", "origin_country": "US"},
    {"name": "TP Tea", "name_zh": "茶湯會", "description": "Taiwanese tea specialist", "origin_country": "TW"},
    {"name": "Gong Cha", "name_zh": "貢茶", "description": "International favorite", "origin_country": "TW"},
]


def get_or_create_brand(db, brand_data: dict) -> Brand:
    """Get existing brand or create new one."""
    brand = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
    if not brand:
        brand = Brand(**brand_data)
        db.add(brand)
        db.flush()
        print(f"  ✅ Created brand: {brand_data['name']}")
    else:
        print(f"  ℹ️  Found existing brand: {brand_data['name']}")
    return brand


def shop_exists(db, google_place_id: str) -> bool:
    """Check if shop already exists by Google Place ID."""
    return db.query(Shop).filter(Shop.google_place_id == google_place_id).first() is not None


async def import_brand(
    service: GooglePlacesServiceV2,
    db,
    brand: Brand,
    grid_points: list[dict],
    session_place_ids: set,
    dry_run: bool = False
) -> int:
    """Import shops for a brand using text search at each grid point."""
    imported = 0
    
    for point in grid_points:
        print(f"    📍 {point['name']}")
        
        try:
            shops_data = await service.text_search(
                query=f"{brand.name} boba",
                lat=point["lat"],
                lng=point["lng"],
                radius_meters=15000,
                max_results=20,
                country="US"
            )
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue
        
        point_imported = 0
        for shop_data in shops_data:
            place_id = shop_data.get("google_place_id")
            if not place_id:
                continue
            
            # Skip duplicates
            if place_id in session_place_ids:
                continue
            
            if shop_exists(db, place_id):
                session_place_ids.add(place_id)
                continue
            
            # Verify brand name is in shop name (loose match)
            shop_name = shop_data.get("name", "")
            if brand.name.lower().split()[0] not in shop_name.lower():
                continue  # Skip non-matching results
            
            session_place_ids.add(place_id)
            
            if dry_run:
                print(f"      [DRY] {shop_name}")
                print(f"            Address: {shop_data.get('address', 'N/A')}")
                print(f"            Maps: {shop_data.get('google_maps_uri', 'N/A')}")
                imported += 1
                point_imported += 1
                continue
            
            # Create shop
            shop = Shop(
                name=shop_name,
                brand_id=brand.id,
                address=shop_data.get("address", ""),
                city="Bay Area",
                country="US",
                latitude=shop_data.get("latitude"),
                longitude=shop_data.get("longitude"),
                google_place_id=place_id,
                status="active",
                last_verified=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
            )
            db.add(shop)
            imported += 1
            point_imported += 1
        
        if point_imported > 0:
            print(f"      ✅ +{point_imported} shops")
        
        # Small delay between requests
        await asyncio.sleep(0.5)
    
    return imported


async def main():
    parser = argparse.ArgumentParser(description="Bay Area boba import experiment")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to database")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧪 BAY AREA IMPORT EXPERIMENT")
    print("=" * 60)
    print("📋 Testing Places API (New) with minimal Pro-tier fields")
    print("📋 Fields: id, displayName, formattedAddress, location, googleMapsUri")
    print()
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No database writes")
    
    service = GooglePlacesServiceV2()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return
    
    db = SessionLocal()
    
    try:
        # Pre-load existing place IDs
        existing_ids = db.query(Shop.google_place_id).all()
        session_place_ids = set(id[0] for id in existing_ids if id[0])
        print(f"📥 Loaded {len(session_place_ids)} existing place IDs")
        
        print(f"\n🚀 Testing {len(TEST_BRANDS)} brand(s) across {len(BAY_AREA_GRID)} grid points...\n")
        
        total_imported = 0
        
        for brand_data in TEST_BRANDS:
            print(f"\n🏷️  {brand_data['name']}")
            
            if not args.dry_run:
                brand = get_or_create_brand(db, brand_data)
            else:
                brand = type('Brand', (), {'id': 0, 'name': brand_data['name']})()
            
            count = await import_brand(
                service=service,
                db=db,
                brand=brand,
                grid_points=BAY_AREA_GRID,
                session_place_ids=session_place_ids,
                dry_run=args.dry_run
            )
            total_imported += count
            
            if not args.dry_run:
                db.commit()
                print(f"    💾 Committed {brand.name}")
        
        print("\n" + "=" * 60)
        print(f"✅ Experiment complete! Found {total_imported} shops")
        print("=" * 60)
        
        if not args.dry_run:
            new_total = db.query(Shop).filter(Shop.country == "US").count()
            print(f"\n📊 Database now contains {new_total} US shops")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
