"""
Bay Area Boba Import - Comprehensive Hybrid Approach
Uses Places API (New) with Pro-tier fields only (FREE-ish, minimal cost).

Brands researched from: Reddit, SF Travel, SF Chronicle, Bay Area blogs 2024

Usage:
    python import_bayarea.py              # Full import
    python import_bayarea.py --brands "Boba Guys,TP Tea"  # Specific brands
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv("../.env")

sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app.models import Brand, Shop
from app.services.google_places_v2 import GooglePlacesServiceV2

Base.metadata.create_all(bind=engine)


def sync_to_database(target_url: str):
    """
    Sync Bay Area shops from local database to production.
    NO API calls - just copies existing data.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 60)
    print("🔄 BAY AREA SYNC TO PRODUCTION")
    print("=" * 60)
    print(f"📤 Source: Local SQLite")
    print(f"📥 Target: PostgreSQL")
    print()
    
    source_db = SessionLocal()
    target_engine = create_engine(target_url)
    TargetSession = sessionmaker(bind=target_engine)
    target_db = TargetSession()
    
    try:
        Base.metadata.create_all(bind=target_engine)
        
        # Get Bay Area shops
        ba_shops = source_db.query(Shop).filter(Shop.city == "Bay Area").all()
        print(f"📊 Found {len(ba_shops)} Bay Area shops to sync")
        
        # Sync brands first
        ba_brand_ids = set(shop.brand_id for shop in ba_shops if shop.brand_id)
        ba_brands = source_db.query(Brand).filter(Brand.id.in_(ba_brand_ids)).all()
        print(f"🏷️  Found {len(ba_brands)} brands to sync")
        
        brand_id_map = {}
        brands_added = 0
        
        for brand in ba_brands:
            existing = target_db.query(Brand).filter(Brand.name == brand.name).first()
            if existing:
                brand_id_map[brand.id] = existing.id
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
        
        for shop in ba_shops:
            if shop.google_place_id:
                existing = target_db.query(Shop).filter(
                    Shop.google_place_id == shop.google_place_id
                ).first()
                if existing:
                    shops_skipped += 1
                    continue
            
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
        
        # Update sequences
        target_db.execute(text("SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id) FROM brands), 1), true)"))
        target_db.execute(text("SELECT setval('shops_id_seq', COALESCE((SELECT MAX(id) FROM shops), 1), true)"))
        target_db.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Sync complete!")
        print(f"   Brands: +{brands_added}")
        print(f"   Shops: +{shops_added} new, {shops_skipped} already existed")
        print("=" * 60)
        
        # Final stats
        target_total = target_db.query(Shop).count()
        target_ba = target_db.query(Shop).filter(Shop.city == "Bay Area").count()
        print(f"\n📊 Production database now contains:")
        print(f"   • {target_total} total shops")
        print(f"   • {target_ba} Bay Area shops")
        
    except Exception as e:
        target_db.rollback()
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        source_db.close()
        target_db.close()


# ============================================================
# BAY AREA BOBA BRANDS - HYBRID APPROACH
# ============================================================

BRANDS = [
    # === TIER 1: National/International Chains ===
    {"name": "Gong Cha", "name_zh": "貢茶", "description": "Popular Taiwanese chain, milk foam series", "origin_country": "TW"},
    {"name": "TP Tea", "name_zh": "茶湯會", "description": "Taiwan Professional Tea, tied to original boba shop", "origin_country": "TW"},
    {"name": "Kung Fu Tea", "name_zh": "功夫茶", "description": "Largest US boba franchise", "origin_country": "US"},
    {"name": "Tiger Sugar", "name_zh": "老虎堂", "description": "Brown sugar boba specialist", "origin_country": "TW"},
    {"name": "The Alley", "name_zh": "鹿角巷", "description": "Deerioca specialty, creme brulee", "origin_country": "TW"},
    {"name": "Happy Lemon", "name_zh": "快樂檸檬", "description": "Lemon tea and cheese foam", "origin_country": "CN"},
    {"name": "CoCo Fresh Tea & Juice", "name_zh": "CoCo都可", "description": "Global chain, panda milk tea", "origin_country": "TW"},
    {"name": "Sharetea", "name_zh": "歇腳亭", "description": "Classic Taiwanese bubble tea", "origin_country": "TW"},
    {"name": "Yi Fang Taiwan Fruit Tea", "name_zh": "一芳", "description": "Authentic fruit teas, real fruit", "origin_country": "TW"},
    {"name": "Ten Ren", "name_zh": "天仁茗茶", "description": "Traditional tea legend since 1953", "origin_country": "TW"},
    
    # === TIER 2: Bay Area Regional Favorites ===
    # SF-based
    {"name": "Boba Guys", "name_zh": "Boba Guys", "description": "SF icon, OG Bay Area brand", "origin_country": "US"},
    {"name": "Asha Tea House", "name_zh": "Asha", "description": "Premium whole-leaf teas, matcha", "origin_country": "US"},
    {"name": "Urban Ritual", "name_zh": "Urban Ritual", "description": "Healthy boba, creme brulee original", "origin_country": "US"},
    {"name": "Little Sweet", "name_zh": "Little Sweet", "description": "Local SF chain, traditional recipes", "origin_country": "US"},
    {"name": "Feng Cha Teahouse", "name_zh": "奉茶", "description": "Cheese foam, reliable quality", "origin_country": "CN"},
    {"name": "Black Sugar Boba Bar", "name_zh": "Black Sugar", "description": "Black sugar specialty", "origin_country": "US"},
    
    # South Bay / Peninsula
    {"name": "Sunright Tea Studio", "name_zh": "日青良月", "description": "Dirty boba, Instagram-worthy", "origin_country": "US"},
    {"name": "Chicha San Chen", "name_zh": "吃茶三千", "description": "Michelin-level tea, Lishan Mountain", "origin_country": "TW"},
    {"name": "Fantasia Coffee & Tea", "name_zh": "Fantasia", "description": "South Bay OG since 1990s", "origin_country": "US"},
    {"name": "Ume Tea", "name_zh": "Ume Tea", "description": "Cupertino favorite, fruit teas", "origin_country": "US"},
    {"name": "Pekoe", "name_zh": "Pekoe", "description": "Premium loose-leaf, split drinks", "origin_country": "US"},
    {"name": "7 Leaves Cafe", "name_zh": "7 Leaves", "description": "Vietnamese-style, mung bean", "origin_country": "US"},
    {"name": "Tastea", "name_zh": "Tastea", "description": "Fruity blends, smoothies", "origin_country": "US"},
    {"name": "Teaspoon", "name_zh": "Teaspoon", "description": "Mini tapioca, quality teas", "origin_country": "US"},
    
    # East Bay
    {"name": "Purple Kow", "name_zh": "Purple Kow", "description": "Berkeley classic, customizable", "origin_country": "US"},
    {"name": "Mr. Green Bubble", "name_zh": "Mr. Green Bubble", "description": "Oakland since 2010", "origin_country": "US"},
    {"name": "Boba Bliss", "name_zh": "Boba Bliss", "description": "Dublin favorite, high quality", "origin_country": "US"},
    
    # Premium/Trending
    {"name": "HEYTEA", "name_zh": "喜茶", "description": "Chinese premium cheese tea", "origin_country": "CN"},
    {"name": "Molly Tea", "name_zh": "Molly Tea", "description": "Jasmine milk tea specialist", "origin_country": "TW"},
    {"name": "Xing Fu Tang", "name_zh": "幸福堂", "description": "Stir-fried brown sugar boba", "origin_country": "TW"},
]

# Bay Area Grid - Comprehensive Coverage
BAY_AREA_GRID = [
    # San Francisco
    {"name": "SF Downtown/Union Square", "lat": 37.7879, "lng": -122.4074},
    {"name": "SF Sunset/Richmond", "lat": 37.7600, "lng": -122.4700},
    {"name": "SF Mission/Castro", "lat": 37.7599, "lng": -122.4148},
    {"name": "SF Chinatown", "lat": 37.7941, "lng": -122.4078},
    
    # East Bay
    {"name": "Berkeley/Telegraph", "lat": 37.8716, "lng": -122.2727},
    {"name": "Oakland Chinatown", "lat": 37.8017, "lng": -122.2708},
    {"name": "Oakland Rockridge", "lat": 37.8441, "lng": -122.2516},
    {"name": "Fremont/Irvington", "lat": 37.5225, "lng": -121.9653},
    {"name": "Dublin/Pleasanton", "lat": 37.7022, "lng": -121.9358},
    
    # Peninsula
    {"name": "Daly City/Serramonte", "lat": 37.6710, "lng": -122.4647},
    {"name": "San Mateo Downtown", "lat": 37.5630, "lng": -122.3255},
    {"name": "Palo Alto", "lat": 37.4419, "lng": -122.1430},
    
    # South Bay
    {"name": "San Jose Downtown", "lat": 37.3382, "lng": -121.8863},
    {"name": "Cupertino/De Anza", "lat": 37.3230, "lng": -122.0322},
    {"name": "Milpitas/Great Mall", "lat": 37.4323, "lng": -121.8996},
    {"name": "Sunnyvale", "lat": 37.3688, "lng": -122.0363},
    {"name": "Santa Clara", "lat": 37.3541, "lng": -121.9552},
]

# Brand name variations for matching
BRAND_ALIASES = {
    "Gong Cha": ["Gong Cha", "貢茶", "GongCha"],
    "TP Tea": ["TP Tea", "TP TEA", "茶湯會", "Tpumps"],
    "Kung Fu Tea": ["Kung Fu Tea", "功夫茶", "KFT"],
    "Tiger Sugar": ["Tiger Sugar", "老虎堂"],
    "The Alley": ["The Alley", "鹿角巷", "Alley"],
    "Happy Lemon": ["Happy Lemon", "快樂檸檬"],
    "CoCo Fresh Tea & Juice": ["CoCo", "CoCo都可", "Coco Fresh"],
    "Sharetea": ["Sharetea", "歇腳亭"],
    "Yi Fang Taiwan Fruit Tea": ["Yi Fang", "一芳", "Yifang"],
    "Ten Ren": ["Ten Ren", "天仁", "Ten Ren's Tea"],
    "Boba Guys": ["Boba Guys"],
    "Asha Tea House": ["Asha", "Asha Tea"],
    "Urban Ritual": ["Urban Ritual"],
    "Little Sweet": ["Little Sweet"],
    "Feng Cha Teahouse": ["Feng Cha", "奉茶"],
    "Black Sugar Boba Bar": ["Black Sugar"],
    "Sunright Tea Studio": ["Sunright", "Sunright Tea"],
    "Chicha San Chen": ["Chicha", "吃茶三千", "ChiCha San Chen"],
    "Fantasia Coffee & Tea": ["Fantasia"],
    "Ume Tea": ["Ume Tea", "Ume"],
    "Pekoe": ["Pekoe"],
    "7 Leaves Cafe": ["7 Leaves", "Seven Leaves"],
    "Tastea": ["Tastea"],
    "Teaspoon": ["Teaspoon", "Tea Spoon"],
    "Purple Kow": ["Purple Kow"],
    "Mr. Green Bubble": ["Mr. Green Bubble", "Mr Green Bubble"],
    "Boba Bliss": ["Boba Bliss"],
    "HEYTEA": ["HEYTEA", "喜茶", "Hey Tea"],
    "Molly Tea": ["Molly Tea", "Molly"],
    "Xing Fu Tang": ["Xing Fu Tang", "幸福堂"],
}


def get_or_create_brand(db, brand_data: dict) -> Brand:
    brand = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
    if not brand:
        brand = Brand(**brand_data)
        db.add(brand)
        db.flush()
        print(f"  ✅ Created brand: {brand_data['name']}")
    return brand


def shop_exists(db, google_place_id: str) -> bool:
    return db.query(Shop).filter(Shop.google_place_id == google_place_id).first() is not None


def matches_brand(shop_name: str, brand_name: str) -> bool:
    aliases = BRAND_ALIASES.get(brand_name, [brand_name])
    shop_lower = shop_name.lower()
    return any(alias.lower() in shop_lower for alias in aliases)


async def import_brand(
    service: GooglePlacesServiceV2,
    db,
    brand: Brand,
    grid_points: list[dict],
    session_place_ids: set,
) -> int:
    imported = 0
    
    for point in grid_points:
        try:
            shops_data = await service.text_search(
                query=f"{brand.name} boba tea",
                lat=point["lat"],
                lng=point["lng"],
                radius_meters=10000,
                max_results=20,
                country="US"
            )
        except Exception as e:
            print(f"      ❌ {point['name']}: {e}")
            continue
        
        point_imported = 0
        for shop_data in shops_data:
            place_id = shop_data.get("google_place_id")
            if not place_id or place_id in session_place_ids:
                continue
            
            if shop_exists(db, place_id):
                session_place_ids.add(place_id)
                continue
            
            shop_name = shop_data.get("name", "")
            if not matches_brand(shop_name, brand.name):
                continue
            
            session_place_ids.add(place_id)
            
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
            print(f"    📍 {point['name']}: +{point_imported}")
        
        await asyncio.sleep(0.3)
    
    return imported


async def main():
    parser = argparse.ArgumentParser(description="Import Bay Area boba shops")
    parser.add_argument("--brands", type=str, help="Comma-separated brand names")
    parser.add_argument("--sync-to", type=str, dest="sync_to",
                        help="Sync to target database URL (no API calls)")
    args = parser.parse_args()
    
    # Handle sync mode
    if args.sync_to:
        sync_to_database(args.sync_to)
        return
    
    print("=" * 60)
    print("🧋 BAY AREA BOBA IMPORT")
    print("=" * 60)
    print(f"📍 Grid points: {len(BAY_AREA_GRID)}")
    print(f"🏷️  Brands: {len(BRANDS)}")
    print("💰 Using FREE Pro-tier API fields only")
    print()
    
    service = GooglePlacesServiceV2()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return
    
    db = SessionLocal()
    
    try:
        # Load existing place IDs
        existing_ids = db.query(Shop.google_place_id).all()
        session_place_ids = set(id[0] for id in existing_ids if id[0])
        print(f"📥 Loaded {len(session_place_ids)} existing place IDs\n")
        
        # Filter brands if specified
        brands_to_import = BRANDS
        if args.brands:
            filter_names = [b.strip() for b in args.brands.split(",")]
            brands_to_import = [b for b in BRANDS if b["name"] in filter_names]
            print(f"🔍 Filtering to: {filter_names}\n")
        
        total_imported = 0
        
        for brand_data in brands_to_import:
            print(f"🏷️  {brand_data['name']}")
            
            brand = get_or_create_brand(db, brand_data)
            
            count = await import_brand(
                service=service,
                db=db,
                brand=brand,
                grid_points=BAY_AREA_GRID,
                session_place_ids=session_place_ids,
            )
            
            if count > 0:
                db.commit()
                print(f"    💾 Saved {count} shops")
            
            total_imported += count
        
        print("\n" + "=" * 60)
        print(f"✅ Complete! Imported {total_imported} new shops")
        print("=" * 60)
        
        # Final stats
        total_us = db.query(Shop).filter(Shop.country == "US").count()
        total_bayarea = db.query(Shop).filter(Shop.city == "Bay Area").count()
        print(f"\n📊 Database stats:")
        print(f"   • Total US shops: {total_us}")
        print(f"   • Bay Area shops: {total_bayarea}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
