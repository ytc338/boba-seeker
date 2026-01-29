"""
Import Singapore boba shop data from Google Places API.

Usage:
    # Dry run (no database writes)
    python import_singapore.py --dry-run

    # Test with single brand
    python import_singapore.py --brands "LiHO Tea" --dry-run

    # Full import to local SQLite
    python import_singapore.py

    # Sync Singapore data to production (NO API calls - copies from local)
    python import_singapore.py --sync-to "postgresql://..."

    # Import fresh from API to production
    DATABASE_URL="postgresql://..." python import_singapore.py
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime
from typing import Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv("../.env")

sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app.models import Brand, Shop
from app.services.google_places import GooglePlacesService

# Create/update tables
Base.metadata.create_all(bind=engine)

# Singapore boba brands (all major chains)
BRANDS = [
    # Tier 1 - Largest presence
    {"name": "LiHO Tea", "name_zh": "里喝", "description": "Homegrown Singapore brand, cheese tea specialty (~85 outlets)", "origin_country": "SG"},
    {"name": "KOI Thé", "name_zh": "KOI", "description": "Taiwanese classic, balanced sweetness and rich milk tea", "origin_country": "TW"},
    {"name": "Each A Cup", "name_zh": "各一杯", "description": "Long-standing Singapore favorite", "origin_country": "SG"},
    {"name": "Gong Cha", "name_zh": "貢茶", "description": "Popular Taiwanese chain, customizable drinks", "origin_country": "TW"},
    
    # Tier 2 - Premium/Trending
    {"name": "ChiCha San Chen", "name_zh": "吃茶三千", "description": "Award-winning Dong Ding Oolong milk tea", "origin_country": "TW"},
    {"name": "HEYTEA", "name_zh": "喜茶", "description": "Chinese brand, iconic cheese tea and premium fruit drinks", "origin_country": "CN"},
    {"name": "Tiger Sugar", "name_zh": "老虎堂", "description": "Famous tiger stripe brown sugar boba milk", "origin_country": "TW"},
    {"name": "Xing Fu Tang", "name_zh": "幸福堂", "description": "Brown sugar boba specialist", "origin_country": "TW"},
    {"name": "The Alley", "name_zh": "鹿角巷", "description": "Deerioca tapioca pearls specialty", "origin_country": "TW"},
    {"name": "Nayuki", "name_zh": "奈雪的茶", "description": "Premium fresh fruit teas", "origin_country": "CN"},
    {"name": "Chagee", "name_zh": "霸王茶姬", "description": "Fast-growing Chinese tea chain", "origin_country": "CN"},
    
    # Tier 3 - Other notable brands
    {"name": "R&B Tea", "name_zh": "R&B巡茶", "description": "Brown Sugar Boba Milk with Cheese Brûlée", "origin_country": "TW"},
    {"name": "Hollin", "name_zh": "賀凜", "description": "Flavored pearls specialty (taro, matcha, etc.)", "origin_country": "TW"},
    {"name": "iTEA", "name_zh": "iTEA", "description": "Budget-friendly bubble tea", "origin_country": "SG"},
    {"name": "Milksha", "name_zh": "迷客夏", "description": "Fresh milk tea specialist", "origin_country": "TW"},
    {"name": "Sharetea", "name_zh": "歇腳亭", "description": "Classic Taiwanese bubble tea chain", "origin_country": "TW"},
    {"name": "PlayMade", "name_zh": "PlayMade", "description": "Handcrafted pearls, high customization", "origin_country": "TW"},
    {"name": "KEBUKE", "name_zh": "可不可", "description": "Premium aged black tea, fruit tea series", "origin_country": "TW"},
    {"name": "Yi Fang", "name_zh": "一芳", "description": "Traditional Taiwan fruit teas", "origin_country": "TW"},
    {"name": "Bober Tea", "name_zh": "Bober Tea", "description": "Brown sugar crème brûlée specialty", "origin_country": "SG"},
    {"name": "The Whale Tea", "name_zh": "大鯨魚", "description": "Honey series, collagen series, whale crystals", "origin_country": "SG"},
]

# Grid points covering Singapore
# Singapore is small (~50km x 27km), so 6 points with 15km radius each provide good coverage
SINGAPORE_GRID = [
    {"name": "Central (Orchard/City)", "lat": 1.2897, "lng": 103.8501},
    {"name": "East (Tampines/Changi)", "lat": 1.3220, "lng": 103.9430},
    {"name": "West (Jurong)", "lat": 1.3350, "lng": 103.7499},
    {"name": "North (Woodlands)", "lat": 1.4290, "lng": 103.8350},
    {"name": "Northeast (Punggol/Sengkang)", "lat": 1.3505, "lng": 103.9430},
    {"name": "South (Harbourfront)", "lat": 1.2700, "lng": 103.8200},
]

from app.services.brand_matcher import match_brand_from_name


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


def extract_area(lat: float, lng: float) -> str:
    """Estimate area from coordinates."""
    if lng > 103.9:
        return "East"
    elif lng < 103.75:
        return "West"
    elif lat > 1.38:
        return "North"
    elif lat < 1.28:
        return "South"
    else:
        return "Central"


def sync_to_database(target_url: str, country: str = "SG"):
    """
    Sync Singapore shops from local database to target database.
    NO API calls - just copies existing data.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    # Fix postgres:// to postgresql://
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 60)
    print("🔄 Singapore Data Sync (No API calls)")
    print("=" * 60)
    print(f"📤 Source: Local SQLite")
    print(f"📥 Target: PostgreSQL")
    print()
    
    # Source: local SQLite
    source_db = SessionLocal()
    
    # Target: PostgreSQL
    target_engine = create_engine(target_url)
    TargetSession = sessionmaker(bind=target_engine)
    target_db = TargetSession()
    
    try:
        # Create tables in target if needed
        Base.metadata.create_all(bind=target_engine)
        
        # Get Singapore shops from source
        sg_shops = source_db.query(Shop).filter(Shop.country == country).all()
        print(f"📊 Found {len(sg_shops)} {country} shops in source database")
        
        # Get Singapore brands from source
        sg_brand_ids = set(shop.brand_id for shop in sg_shops if shop.brand_id)
        sg_brands = source_db.query(Brand).filter(Brand.id.in_(sg_brand_ids)).all()
        print(f"🏷️  Found {len(sg_brands)} brands to sync")
        
        # Sync brands first
        brands_added = 0
        brand_id_map = {}  # old_id -> new_id (in case IDs differ)
        
        for brand in sg_brands:
            # Check if brand exists in target
            existing = target_db.query(Brand).filter(Brand.name == brand.name).first()
            if existing:
                brand_id_map[brand.id] = existing.id
                print(f"   ℹ️  Brand exists: {brand.name}")
            else:
                new_brand = Brand(
                    name=brand.name,
                    name_zh=brand.name_zh,
                    logo_url=brand.logo_url,
                    description=brand.description,
                    origin_country=brand.origin_country,
                    website=brand.website
                )
                target_db.add(new_brand)
                target_db.flush()
                brand_id_map[brand.id] = new_brand.id
                brands_added += 1
                print(f"   ✅ Created brand: {brand.name}")
        
        target_db.commit()
        
        # Sync shops
        shops_added = 0
        shops_skipped = 0
        
        for shop in sg_shops:
            # Check if shop exists in target (by google_place_id)
            if shop.google_place_id:
                existing = target_db.query(Shop).filter(
                    Shop.google_place_id == shop.google_place_id
                ).first()
                if existing:
                    shops_skipped += 1
                    continue
            
            # Create shop in target
            new_shop = Shop(
                name=shop.name,
                brand_id=brand_id_map.get(shop.brand_id) if shop.brand_id else None,
                address=shop.address,
                city=shop.city,
                country=shop.country,
                latitude=shop.latitude,
                longitude=shop.longitude,
                rating=shop.rating,
                rating_count=shop.rating_count,
                phone=shop.phone,
                hours=shop.hours,
                photo_url=shop.photo_url,
                google_place_id=shop.google_place_id,
                status=shop.status,
                last_verified=shop.last_verified,
                created_at=shop.created_at,
                updated_at=shop.updated_at,
            )
            target_db.add(new_shop)
            shops_added += 1
        
        target_db.commit()
        
        # Update sequences for PostgreSQL
        target_db.execute(text("""
            SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id) FROM brands), 1), true)
        """))
        target_db.execute(text("""
            SELECT setval('shops_id_seq', COALESCE((SELECT MAX(id) FROM shops), 1), true)
        """))
        target_db.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Sync complete!")
        print(f"   Brands: +{brands_added}")
        print(f"   Shops: +{shops_added} new, {shops_skipped} already existed")
        print("=" * 60)
        
        # Show target stats
        target_total = target_db.query(Shop).count()
        target_sg = target_db.query(Shop).filter(Shop.country == country).count()
        print(f"\n📊 Target database now contains:")
        print(f"   • {target_total} total shops")
        print(f"   • {target_sg} Singapore shops")
        
    except Exception as e:
        target_db.rollback()
        print(f"\n❌ Sync failed: {e}")
        raise
    finally:
        source_db.close()
        target_db.close()


async def import_brand_grid(
    service: GooglePlacesService,
    db,
    brand: Brand,
    grid_points: list[dict],
    session_place_ids: set,
    dry_run: bool = False
) -> int:
    """Import shops for a brand using grid-based nearby search."""
    imported = 0
    skipped_dup = 0
    skipped_name = 0
    
    for point in grid_points:
        print(f"    📍 {point['name']} ({point['lat']:.4f}, {point['lng']:.4f})")
        
        try:
            shops_data = await service.nearby_search_all_pages(
                lat=point["lat"],
                lng=point["lng"],
                keyword=brand.name,
                radius_meters=15000,  # 15km radius (Singapore is small)
                country="SG",
                max_results=60
            )
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue
        
        point_imported = 0
        for shop_data in shops_data:
            place_id = shop_data.get("google_place_id")
            if not place_id:
                continue
            
            # Skip if already added this session
            if place_id in session_place_ids:
                skipped_dup += 1
                continue
            
            # Skip if already in database
            if shop_exists(db, place_id):
                session_place_ids.add(place_id)
                skipped_dup += 1
                continue
            
            # Verify brand name matches
            shop_name = shop_data.get("name", "")
            # brand.name matches name in brand_data
            conf = match_brand_from_name(shop_name, brand.name, brand.name_zh)
            if conf < 0.9:
                skipped_name += 1
                continue
            
            # Track this place ID
            session_place_ids.add(place_id)
            
            if dry_run:
                print(f"      [DRY] {shop_name}")
                imported += 1
                point_imported += 1
                continue
            
            # Create shop
            shop = Shop(
                name=shop_name,
                brand_id=brand.id,
                address=shop_data.get("address", ""),
                city=extract_area(shop_data.get("latitude", 0), shop_data.get("longitude", 0)),
                country="SG",
                latitude=shop_data.get("latitude"),
                longitude=shop_data.get("longitude"),
                rating=shop_data.get("rating"),
                rating_count=shop_data.get("rating_count"),
                google_place_id=place_id,
                photo_url=shop_data.get("photo_url"),
                status="active",
                last_verified=datetime.utcnow(),
                created_at=datetime.utcnow(),
            )
            db.add(shop)
            imported += 1
            point_imported += 1
        
        if point_imported > 0:
            print(f"      ✅ +{point_imported} shops")
        
        # Small delay to avoid rate limits
        await asyncio.sleep(0.3)
    
    print(f"    📊 Total: +{imported} new, {skipped_dup} duplicates, {skipped_name} non-matching")
    return imported


async def main():
    parser = argparse.ArgumentParser(description="Import Singapore boba shops from Google Places API")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to database")
    parser.add_argument("--brands", type=str, help="Comma-separated brand names")
    parser.add_argument("--sync-to", type=str, dest="sync_to", 
                        help="Sync SG shops to target database URL (no API calls)")
    args = parser.parse_args()
    
    # If --sync-to is specified, sync data instead of importing from API
    if args.sync_to:
        sync_to_database(args.sync_to, country="SG")
        return
    
    brand_filter = [b.strip() for b in args.brands.split(",")] if args.brands else None
    
    # Show which database we're using
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./boba_seeker.db")
    if "postgresql" in db_url:
        db_type = "🐘 PostgreSQL (Production)"
    else:
        db_type = "📁 SQLite (Local)"
    
    print("=" * 60)
    print("🧋 Singapore Boba Shop Importer")
    print("=" * 60)
    print(f"💾 Database: {db_type}")
    print(f"📍 Grid points: {len(SINGAPORE_GRID)}")
    print(f"🏷️  Brands: {len(BRANDS)}")
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE")
    
    service = GooglePlacesService()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return
    
    db = SessionLocal()
    
    try:
        # Get existing counts
        existing_shops = db.query(Shop).count()
        existing_sg_shops = db.query(Shop).filter(Shop.country == "SG").count()
        print(f"\n📊 Existing shops: {existing_shops} total, {existing_sg_shops} in Singapore")
        
        # Pre-load existing place IDs
        print("📥 Loading existing place IDs...")
        existing_ids = db.query(Shop.google_place_id).all()
        session_place_ids = set(id[0] for id in existing_ids if id[0])
        print(f"   Loaded {len(session_place_ids)} existing place IDs")
        
        brands_to_import = BRANDS
        if brand_filter:
            brands_to_import = [b for b in BRANDS if b["name"] in brand_filter]
        
        print(f"\n🚀 Importing {len(brands_to_import)} brand(s)...\n")
        
        total_imported = 0
        
        for brand_data in brands_to_import:
            print(f"\n🏷️  {brand_data['name']}")
            
            if not args.dry_run:
                brand = get_or_create_brand(db, brand_data)
            else:
                brand = type('Brand', (), {'id': 0, 'name': brand_data['name']})()
            
            count = await import_brand_grid(
                service=service,
                db=db,
                brand=brand,
                grid_points=SINGAPORE_GRID,
                session_place_ids=session_place_ids,
                dry_run=args.dry_run
            )
            total_imported += count
            
            # Commit after each brand
            if not args.dry_run:
                db.commit()
                print(f"    💾 Committed {brand.name}")
        
        print("\n" + "=" * 60)
        print(f"✅ Import complete! +{total_imported} new shops")
        print("=" * 60)
        
        if not args.dry_run:
            new_total = db.query(Shop).count()
            new_sg_total = db.query(Shop).filter(Shop.country == "SG").count()
            print(f"\n📊 Database now contains:")
            print(f"   • {new_total} total shops")
            print(f"   • {new_sg_total} Singapore shops (+{new_sg_total - existing_sg_shops})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
