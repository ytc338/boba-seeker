"""
US Major Cities Boba Import - San Diego, Los Angeles, Seattle, NYC
Uses Places API (New) with Pro-tier fields only (FREE).

Usage:
    python import_us_cities.py                    # Full import all cities
    python import_us_cities.py --city "Seattle"   # Single city
    python import_us_cities.py --sync-to "..."    # Sync to production
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


def sync_to_database(target_url: str, cities: list[str] = None):
    """Sync US city shops from local to production. NO API calls."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 60)
    print("🔄 US CITIES SYNC TO PRODUCTION")
    print("=" * 60)
    
    source_db = SessionLocal()
    target_engine = create_engine(target_url)
    TargetSession = sessionmaker(bind=target_engine)
    target_db = TargetSession()
    
    try:
        Base.metadata.create_all(bind=target_engine)
        
        # Get US shops (excluding Bay Area which was synced separately)
        if cities:
            us_shops = source_db.query(Shop).filter(
                Shop.country == "US",
                Shop.city.in_(cities)
            ).all()
        else:
            us_shops = source_db.query(Shop).filter(
                Shop.country == "US",
                Shop.city != "Bay Area"
            ).all()
        
        print(f"📊 Found {len(us_shops)} US shops to sync")
        
        # Sync brands
        brand_ids = set(shop.brand_id for shop in us_shops if shop.brand_id)
        brands = source_db.query(Brand).filter(Brand.id.in_(brand_ids)).all()
        
        brand_id_map = {}
        brands_added = 0
        
        for brand in brands:
            existing = target_db.query(Brand).filter(Brand.name == brand.name).first()
            if existing:
                brand_id_map[brand.id] = existing.id
            else:
                new_brand = Brand(
                    name=brand.name, name_zh=brand.name_zh,
                    logo_url=brand.logo_url, description=brand.description,
                    origin_country=brand.origin_country, website=brand.website
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
        
        for shop in us_shops:
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
                address=shop.address, city=shop.city, country=shop.country,
                latitude=shop.latitude, longitude=shop.longitude,
                google_place_id=shop.google_place_id,
                status=shop.status, last_verified=shop.last_verified,
                created_at=shop.created_at,
            )
            target_db.add(new_shop)
            shops_added += 1
        
        target_db.commit()
        
        target_db.execute(text("SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id) FROM brands), 1), true)"))
        target_db.execute(text("SELECT setval('shops_id_seq', COALESCE((SELECT MAX(id) FROM shops), 1), true)"))
        target_db.commit()
        
        print(f"\n✅ Sync complete! +{shops_added} new, {shops_skipped} skipped")
        
    except Exception as e:
        target_db.rollback()
        print(f"❌ Sync failed: {e}")
    finally:
        source_db.close()
        target_db.close()


# ============================================================
# CITY CONFIGURATIONS
# ============================================================

CITIES = {
    "San Diego": {
        "grid": [
            {"name": "Convoy District", "lat": 32.8329, "lng": -117.1554},
            {"name": "Mira Mesa", "lat": 32.9157, "lng": -117.1430},
            {"name": "UTC/La Jolla", "lat": 32.8721, "lng": -117.2125},
            {"name": "Downtown SD", "lat": 32.7157, "lng": -117.1611},
            {"name": "Kearny Mesa", "lat": 32.8342, "lng": -117.1425},
        ],
        "brands": [
            # National Chains
            {"name": "Kung Fu Tea", "name_zh": "功夫茶", "description": "Largest US boba franchise", "origin_country": "US"},
            {"name": "Sharetea", "name_zh": "歇腳亭", "description": "Classic Taiwanese bubble tea", "origin_country": "TW"},
            {"name": "Happy Lemon", "name_zh": "快樂檸檬", "description": "Lemon tea and cheese foam", "origin_country": "CN"},
            {"name": "Gong Cha", "name_zh": "貢茶", "description": "Taiwanese chain", "origin_country": "TW"},
            {"name": "Tiger Sugar", "name_zh": "老虎堂", "description": "Brown sugar boba", "origin_country": "TW"},
            # San Diego Regional
            {"name": "Wushiland Boba", "name_zh": "50嵐", "description": "Famous Taiwan 50 Lan US branch", "origin_country": "TW"},
            {"name": "Camellia Tea Bar", "name_zh": "Camellia", "description": "SD local tea-focused", "origin_country": "US"},
            {"name": "3CAT Tea", "name_zh": "3CAT", "description": "Mochi drinks specialty", "origin_country": "US"},
            {"name": "Sweet Vibe", "name_zh": "Sweet Vibe", "description": "Best taro in SD", "origin_country": "US"},
            {"name": "Chakaa", "name_zh": "Chakaa", "description": "Tea-based milk teas", "origin_country": "US"},
            {"name": "DaYung's Tea", "name_zh": "大苑子", "description": "Fresh fruit tea", "origin_country": "TW"},
            {"name": "Feng Cha Teahouse", "name_zh": "奉茶", "description": "Cheese foam specialty", "origin_country": "CN"},
        ]
    },
    
    "Los Angeles": {
        "grid": [
            # San Gabriel Valley
            {"name": "San Gabriel", "lat": 34.0961, "lng": -118.1058},
            {"name": "Alhambra", "lat": 34.0953, "lng": -118.1270},
            {"name": "Arcadia", "lat": 34.1397, "lng": -118.0353},
            {"name": "Rowland Heights", "lat": 33.9761, "lng": -117.9053},
            {"name": "Monterey Park", "lat": 34.0625, "lng": -118.1228},
            # LA Proper
            {"name": "Koreatown", "lat": 34.0622, "lng": -118.3015},
            {"name": "Sawtelle/West LA", "lat": 34.0350, "lng": -118.4419},
            {"name": "Downtown LA", "lat": 34.0407, "lng": -118.2468},
            # Orange County
            {"name": "Irvine", "lat": 33.6846, "lng": -117.8265},
            {"name": "Garden Grove", "lat": 33.7739, "lng": -117.9414},
        ],
        "brands": [
            # National Chains
            {"name": "Kung Fu Tea", "name_zh": "功夫茶", "description": "Largest US boba franchise", "origin_country": "US"},
            {"name": "Sharetea", "name_zh": "歇腳亭", "description": "Classic Taiwanese bubble tea", "origin_country": "TW"},
            {"name": "Gong Cha", "name_zh": "貢茶", "description": "Taiwanese chain", "origin_country": "TW"},
            {"name": "Tiger Sugar", "name_zh": "老虎堂", "description": "Brown sugar boba", "origin_country": "TW"},
            {"name": "Happy Lemon", "name_zh": "快樂檸檬", "description": "Lemon tea and cheese foam", "origin_country": "CN"},
            {"name": "The Alley", "name_zh": "鹿角巷", "description": "Deerioca specialty", "origin_country": "TW"},
            {"name": "Yi Fang Taiwan Fruit Tea", "name_zh": "一芳", "description": "Authentic fruit teas", "origin_country": "TW"},
            {"name": "CoCo Fresh Tea & Juice", "name_zh": "CoCo都可", "description": "Global chain", "origin_country": "TW"},
            # LA/SGV Regional
            {"name": "Chicha San Chen", "name_zh": "吃茶三千", "description": "Michelin-level tea", "origin_country": "TW"},
            {"name": "Sunright Tea Studio", "name_zh": "日青良月", "description": "Dirty boba, Instagram", "origin_country": "US"},
            {"name": "Bopomofo Cafe", "name_zh": "Bopomofo", "description": "Wong Fu Productions collab", "origin_country": "US"},
            {"name": "Wushiland Boba", "name_zh": "50嵐", "description": "Taiwan 50 Lan US branch", "origin_country": "TW"},
            {"name": "Factory Tea Bar", "name_zh": "Factory Tea", "description": "SGV late-night spot", "origin_country": "US"},
            {"name": "Tea Maru", "name_zh": "Tea Maru", "description": "Handmade sweet potato boba", "origin_country": "US"},
            {"name": "7 Leaves Cafe", "name_zh": "7 Leaves", "description": "Vietnamese-style", "origin_country": "US"},
            {"name": "HEYTEA", "name_zh": "喜茶", "description": "Chinese cheese tea pioneer", "origin_country": "CN"},
            {"name": "Xing Fu Tang", "name_zh": "幸福堂", "description": "Stir-fried brown sugar boba", "origin_country": "TW"},
            {"name": "Tastea", "name_zh": "Tastea", "description": "Fruity blends", "origin_country": "US"},
            {"name": "Molly Tea", "name_zh": "Molly Tea", "description": "Jasmine milk tea specialist", "origin_country": "TW"},
            {"name": "TP Tea", "name_zh": "茶湯會", "description": "Taiwan Professional Tea", "origin_country": "TW"},
        ]
    },
    
    "Seattle": {
        "grid": [
            {"name": "U-District", "lat": 47.6628, "lng": -122.3139},
            {"name": "Capitol Hill", "lat": 47.6253, "lng": -122.3222},
            {"name": "International District", "lat": 47.5982, "lng": -122.3248},
            {"name": "Bellevue Downtown", "lat": 47.6101, "lng": -122.2015},
            {"name": "Bellevue Crossroads", "lat": 47.6172, "lng": -122.1320},
            {"name": "Redmond", "lat": 47.6740, "lng": -122.1215},
            {"name": "Lynnwood", "lat": 47.8209, "lng": -122.3151},
        ],
        "brands": [
            # National Chains
            {"name": "Kung Fu Tea", "name_zh": "功夫茶", "description": "Largest US boba franchise", "origin_country": "US"},
            {"name": "Sharetea", "name_zh": "歇腳亭", "description": "Classic Taiwanese", "origin_country": "TW"},
            {"name": "Gong Cha", "name_zh": "貢茶", "description": "Taiwanese chain", "origin_country": "TW"},
            {"name": "Happy Lemon", "name_zh": "快樂檸檬", "description": "Cheese foam", "origin_country": "CN"},
            {"name": "Yi Fang Taiwan Fruit Tea", "name_zh": "一芳", "description": "Fruit teas", "origin_country": "TW"},
            {"name": "CoCo Fresh Tea & Juice", "name_zh": "CoCo都可", "description": "Global chain", "origin_country": "TW"},
            {"name": "TP Tea", "name_zh": "茶湯會", "description": "Taiwan Professional Tea", "origin_country": "TW"},
            {"name": "Sunright Tea Studio", "name_zh": "日青良月", "description": "Dirty boba", "origin_country": "US"},
            # Seattle Regional
            {"name": "Oasis Tea Zone", "name_zh": "Oasis", "description": "Seattle staple since 2001", "origin_country": "US"},
            {"name": "Don't Yell At Me", "name_zh": "不要對我尖叫", "description": "Taipei chain, cheese foam", "origin_country": "TW"},
            {"name": "Seattle Best Tea", "name_zh": "Seattle Best Tea", "description": "Top rated local", "origin_country": "US"},
            {"name": "Macu Tea", "name_zh": "Macu Tea", "description": "Fresh fruit teas", "origin_country": "US"},
            {"name": "Boba Up", "name_zh": "Boba Up", "description": "First self-serve boba PNW", "origin_country": "US"},
            {"name": "Timeless Tea", "name_zh": "Timeless Tea", "description": "Brown sugar fresh milk", "origin_country": "US"},
            {"name": "Chicha San Chen", "name_zh": "吃茶三千", "description": "Premium Taiwanese", "origin_country": "TW"},
            {"name": "HEYTEA", "name_zh": "喜茶", "description": "Chinese cheese tea", "origin_country": "CN"},
            {"name": "Moge Tee", "name_zh": "愿茶", "description": "Cheese tea chain", "origin_country": "CN"},
        ]
    },
    
    "New York City": {
        "grid": [
            {"name": "Flushing Main St", "lat": 40.7593, "lng": -73.8307},
            {"name": "Flushing New World Mall", "lat": 40.7610, "lng": -73.8273},
            {"name": "Chinatown Manhattan", "lat": 40.7158, "lng": -73.9970},
            {"name": "East Village", "lat": 40.7295, "lng": -73.9874},
            {"name": "Koreatown NYC", "lat": 40.7475, "lng": -73.9872},
            {"name": "Sunset Park Brooklyn", "lat": 40.6453, "lng": -74.0124},
            {"name": "Elmhurst Queens", "lat": 40.7379, "lng": -73.8795},
        ],
        "brands": [
            # National Chains
            {"name": "Kung Fu Tea", "name_zh": "功夫茶", "description": "Largest US franchise", "origin_country": "US"},
            {"name": "Gong Cha", "name_zh": "貢茶", "description": "Taiwanese chain", "origin_country": "TW"},
            {"name": "CoCo Fresh Tea & Juice", "name_zh": "CoCo都可", "description": "Global chain", "origin_country": "TW"},
            {"name": "Tiger Sugar", "name_zh": "老虎堂", "description": "Brown sugar boba", "origin_country": "TW"},
            {"name": "Yi Fang Taiwan Fruit Tea", "name_zh": "一芳", "description": "Fruit teas", "origin_country": "TW"},
            {"name": "The Alley", "name_zh": "鹿角巷", "description": "Deerioca specialty", "origin_country": "TW"},
            {"name": "Xing Fu Tang", "name_zh": "幸福堂", "description": "Brown sugar boba", "origin_country": "TW"},
            {"name": "Ten Ren", "name_zh": "天仁茗茶", "description": "Traditional tea legend", "origin_country": "TW"},
            {"name": "Happy Lemon", "name_zh": "快樂檸檬", "description": "Cheese foam", "origin_country": "CN"},
            # NYC Regional
            {"name": "Machi Machi", "name_zh": "麥吉", "description": "Jay Chou's favorite", "origin_country": "TW"},
            {"name": "HEYTEA", "name_zh": "喜茶", "description": "Chinese cheese tea pioneer", "origin_country": "CN"},
            {"name": "Molly Tea", "name_zh": "Molly Tea", "description": "Jasmine specialist", "origin_country": "TW"},
            {"name": "Song Tea", "name_zh": "宋茶", "description": "NYC quality spot", "origin_country": "US"},
            {"name": "Wanpo Tea Shop", "name_zh": "萬波", "description": "Distinctive flavor", "origin_country": "TW"},
            {"name": "Vivi Bubble Tea", "name_zh": "ViVi", "description": "NYC staple", "origin_country": "US"},
            {"name": "Moge Tee", "name_zh": "愿茶", "description": "Cheese tea chain", "origin_country": "CN"},
        ]
    },
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


async def import_city(
    service: GooglePlacesServiceV2,
    db,
    city_name: str,
    config: dict,
    session_place_ids: set,
) -> int:
    """Import all brands for a single city."""
    print(f"\n{'='*60}")
    print(f"🏙️  {city_name}")
    print(f"{'='*60}")
    print(f"📍 Grid points: {len(config['grid'])}")
    print(f"🏷️  Brands: {len(config['brands'])}")
    
    city_total = 0
    
    for brand_data in config["brands"]:
        print(f"\n  🏷️  {brand_data['name']}")
        brand = get_or_create_brand(db, brand_data)
        
        brand_count = 0
        for point in config["grid"]:
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
                continue
            
            for shop_data in shops_data:
                place_id = shop_data.get("google_place_id")
                if not place_id or place_id in session_place_ids:
                    continue
                
                if shop_exists(db, place_id):
                    session_place_ids.add(place_id)
                    continue
                
                shop_name = shop_data.get("name", "")
                # Simple brand matching
                if brand.name.lower().split()[0] not in shop_name.lower():
                    continue
                
                session_place_ids.add(place_id)
                
                shop = Shop(
                    name=shop_name,
                    brand_id=brand.id,
                    address=shop_data.get("address", ""),
                    city=city_name,
                    country="US",
                    latitude=shop_data.get("latitude"),
                    longitude=shop_data.get("longitude"),
                    google_place_id=place_id,
                    status="active",
                    last_verified=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                )
                db.add(shop)
                brand_count += 1
            
            await asyncio.sleep(0.3)
        
        if brand_count > 0:
            db.commit()
            print(f"      💾 +{brand_count} shops")
            city_total += brand_count
    
    return city_total


async def main():
    parser = argparse.ArgumentParser(description="Import US cities boba shops")
    parser.add_argument("--city", type=str, help="Single city to import")
    parser.add_argument("--sync-to", type=str, dest="sync_to", help="Sync to production DB")
    args = parser.parse_args()
    
    if args.sync_to:
        cities = [args.city] if args.city else None
        sync_to_database(args.sync_to, cities)
        return
    
    print("=" * 60)
    print("🧋 US MAJOR CITIES BOBA IMPORT")
    print("=" * 60)
    print("💰 Using FREE Pro-tier API fields only")
    print(f"🏙️  Cities: {', '.join(CITIES.keys())}")
    print()
    
    service = GooglePlacesServiceV2()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return
    
    db = SessionLocal()
    
    try:
        existing_ids = db.query(Shop.google_place_id).all()
        session_place_ids = set(id[0] for id in existing_ids if id[0])
        print(f"📥 Loaded {len(session_place_ids)} existing place IDs")
        
        cities_to_import = {args.city: CITIES[args.city]} if args.city else CITIES
        
        grand_total = 0
        for city_name, config in cities_to_import.items():
            count = await import_city(service, db, city_name, config, session_place_ids)
            grand_total += count
        
        print("\n" + "=" * 60)
        print(f"✅ COMPLETE! Imported {grand_total} new shops")
        print("=" * 60)
        
        # Stats per city
        for city_name in cities_to_import:
            count = db.query(Shop).filter(Shop.city == city_name).count()
            print(f"   • {city_name}: {count}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
