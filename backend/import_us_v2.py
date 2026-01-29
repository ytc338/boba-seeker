"""
US Boba Import v2 - Three-Layer Brand Coverage Strategy

Layer 1: NATIONAL_BRANDS - Searched in ALL cities
Layer 2: REGIONAL_BRANDS - Shared across geographic regions (SoCal, NorCal, PNW, etc.)
Layer 3: DISCOVERY_MODE - Generic "boba tea" search to find unlisted brands

Features:
- Shared brand lists prevent missing cross-city locations
- Discovery mode catches new/trending brands automatically
- Fuzzy brand matching links discovered shops to known brands

Usage:
    python import_us_v2.py                     # Import all cities
    python import_us_v2.py --city "Seattle"   # Single city
    python import_us_v2.py --discover-only    # Only discovery mode
    python import_us_v2.py --sync-to "..."    # Sync to production
"""

import asyncio
import argparse
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
load_dotenv("../.env")

sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app.models import Brand, Shop
from app.services.google_places_v2 import GooglePlacesServiceV2

Base.metadata.create_all(bind=engine)


# ============================================================
# LAYER 1: NATIONAL BRANDS (Searched in ALL cities)
# ============================================================
NATIONAL_BRANDS = [
    {"name": "Kung Fu Tea", "name_zh": "功夫茶", "aliases": ["KFT", "Kungfu Tea"], "origin_country": "US"},
    {"name": "Gong Cha", "name_zh": "貢茶", "aliases": ["GongCha"], "origin_country": "TW"},
    {"name": "Tiger Sugar", "name_zh": "老虎堂", "aliases": [], "origin_country": "TW"},
    {"name": "Sharetea", "name_zh": "歇腳亭", "aliases": ["Share Tea"], "origin_country": "TW"},
    {"name": "CoCo Fresh Tea & Juice", "name_zh": "CoCo都可", "aliases": ["CoCo", "Coco Tea"], "origin_country": "TW"},
    {"name": "Happy Lemon", "name_zh": "快樂檸檬", "aliases": [], "origin_country": "CN"},
    {"name": "Yi Fang Taiwan Fruit Tea", "name_zh": "一芳", "aliases": ["Yifang", "Yi Fang"], "origin_country": "TW"},
    {"name": "The Alley", "name_zh": "鹿角巷", "aliases": ["Alley"], "origin_country": "TW"},
    {"name": "TP Tea", "name_zh": "茶湯會", "aliases": ["TP TEA", "Tpumps"], "origin_country": "TW"},
    {"name": "Ten Ren", "name_zh": "天仁茗茶", "aliases": ["Ten Ren's Tea"], "origin_country": "TW"},
    {"name": "Xing Fu Tang", "name_zh": "幸福堂", "aliases": ["XFT"], "origin_country": "TW"},
    {"name": "HEYTEA", "name_zh": "喜茶", "aliases": ["Hey Tea"], "origin_country": "CN"},
    {"name": "Chicha San Chen", "name_zh": "吃茶三千", "aliases": ["ChiCha"], "origin_country": "TW"},
    {"name": "7 Leaves Cafe", "name_zh": "7 Leaves", "aliases": ["Seven Leaves"], "origin_country": "US"},
    {"name": "Sunright Tea Studio", "name_zh": "日青良月", "aliases": ["Sunright"], "origin_country": "US"},
    {"name": "Feng Cha Teahouse", "name_zh": "奉茶", "aliases": ["Feng Cha"], "origin_country": "CN"},
    {"name": "Moge Tee", "name_zh": "愿茶", "aliases": [], "origin_country": "CN"},
    {"name": "Meet Fresh", "name_zh": "鮮芋仙", "aliases": [], "origin_country": "TW"},
    {"name": "Wushiland Boba", "name_zh": "50嵐", "aliases": ["OO Tea", "50 Lan"], "origin_country": "TW"},
]

# ============================================================
# LAYER 2: REGIONAL BRANDS (Shared within regions)
# ============================================================
REGIONAL_BRANDS = {
    "SoCal": [  # LA, San Diego, Orange County
        {"name": "Bopomofo Cafe", "name_zh": "Bopomofo", "aliases": [], "origin_country": "US"},
        {"name": "OMOMO Tea Shoppe", "name_zh": "OMOMO", "aliases": ["OMOMO"], "origin_country": "TW"},
        {"name": "Factory Tea Bar", "name_zh": "Factory Tea", "aliases": [], "origin_country": "US"},
        {"name": "Tea Maru", "name_zh": "Tea Maru", "aliases": [], "origin_country": "US"},
        {"name": "Tastea", "name_zh": "Tastea", "aliases": [], "origin_country": "US"},
        {"name": "Molly Tea", "name_zh": "Molly Tea", "aliases": ["Molly"], "origin_country": "TW"},
        {"name": "3CAT Tea", "name_zh": "3CAT", "aliases": ["3 Cat"], "origin_country": "US"},
        {"name": "DaYung's Tea", "name_zh": "大苑子", "aliases": ["Da Yung"], "origin_country": "TW"},
        {"name": "Camellia Tea Bar", "name_zh": "Camellia", "aliases": ["Camellia Rd"], "origin_country": "US"},
    ],
    "NorCal": [  # Bay Area
        {"name": "Boba Guys", "name_zh": "Boba Guys", "aliases": [], "origin_country": "US"},
        {"name": "Asha Tea House", "name_zh": "Asha", "aliases": ["Asha Tea"], "origin_country": "US"},
        {"name": "Urban Ritual", "name_zh": "Urban Ritual", "aliases": [], "origin_country": "US"},
        {"name": "Little Sweet", "name_zh": "Little Sweet", "aliases": [], "origin_country": "US"},
        {"name": "Fantasia Coffee & Tea", "name_zh": "Fantasia", "aliases": [], "origin_country": "US"},
        {"name": "Pekoe", "name_zh": "Pekoe", "aliases": [], "origin_country": "US"},
        {"name": "Teaspoon", "name_zh": "Teaspoon", "aliases": ["Tea Spoon"], "origin_country": "US"},
        {"name": "Purple Kow", "name_zh": "Purple Kow", "aliases": [], "origin_country": "US"},
        {"name": "Ume Tea", "name_zh": "Ume Tea", "aliases": ["Ume"], "origin_country": "US"},
        {"name": "Black Sugar Boba Bar", "name_zh": "Black Sugar", "aliases": [], "origin_country": "US"},
    ],
    "PNW": [  # Seattle, Portland
        {"name": "Oasis Tea Zone", "name_zh": "Oasis", "aliases": [], "origin_country": "US"},
        {"name": "Don't Yell At Me", "name_zh": "不要對我尖叫", "aliases": [], "origin_country": "TW"},
        {"name": "Seattle Best Tea", "name_zh": "Seattle Best Tea", "aliases": [], "origin_country": "US"},
        {"name": "Macu Tea", "name_zh": "Macu Tea", "aliases": ["Macu"], "origin_country": "US"},
        {"name": "Boba Up", "name_zh": "Boba Up", "aliases": [], "origin_country": "US"},
        {"name": "Timeless Tea", "name_zh": "Timeless Tea", "aliases": [], "origin_country": "US"},
    ],
    "Northeast": [  # NYC, Boston, Philadelphia
        {"name": "Machi Machi", "name_zh": "麥吉", "aliases": [], "origin_country": "TW"},
        {"name": "Song Tea", "name_zh": "宋茶", "aliases": [], "origin_country": "US"},
        {"name": "Wanpo Tea Shop", "name_zh": "萬波", "aliases": ["Wanpo"], "origin_country": "TW"},
        {"name": "Vivi Bubble Tea", "name_zh": "ViVi", "aliases": ["Vivi"], "origin_country": "US"},
    ],
    "Hawaii": [  # Honolulu
        {"name": "Taste Tea", "name_zh": "Taste Tea", "aliases": [], "origin_country": "US"},
        {"name": "Teapresso Bar", "name_zh": "Teapresso", "aliases": [], "origin_country": "US"},
        {"name": "Mr. Tea Cafe", "name_zh": "Mr. Tea", "aliases": [], "origin_country": "US"},
        {"name": "Hana Tea", "name_zh": "Hana Tea", "aliases": [], "origin_country": "US"},
        {"name": "Thang's French Coffee & Bubble Tea", "name_zh": "Thang's", "aliases": [], "origin_country": "US"},
    ],
    "Texas": [  # Houston, Dallas
        {"name": "The Teahouse", "name_zh": "The Teahouse", "aliases": [], "origin_country": "US"},
        {"name": "Tea Top", "name_zh": "Tea Top", "aliases": [], "origin_country": "TW"},
        {"name": "Star Snow Ice", "name_zh": "Star Snow", "aliases": [], "origin_country": "US"},
        {"name": "Mr. Wish", "name_zh": "Mr. Wish", "aliases": [], "origin_country": "TW"},
    ],
    "Midwest": [  # Chicago
        {"name": "Joy Yee", "name_zh": "Joy Yee", "aliases": [], "origin_country": "US"},
        {"name": "Uni Uni", "name_zh": "Uni Uni", "aliases": [], "origin_country": "US"},
        {"name": "Te'Amo Boba Bar", "name_zh": "Te'Amo", "aliases": [], "origin_country": "US"},
        {"name": "Hello Jasmine", "name_zh": "Hello Jasmine", "aliases": [], "origin_country": "US"},
        {"name": "Tsaocaa", "name_zh": "Tsaocaa", "aliases": [], "origin_country": "CN"},
        {"name": "Saint's Alp Teahouse", "name_zh": "Saint's Alp", "aliases": [], "origin_country": "HK"},
    ],
}

# City to Region mapping
CITY_REGIONS = {
    "San Diego": "SoCal",
    "Los Angeles": "SoCal",
    "Bay Area": "NorCal",
    "Seattle": "PNW",
    "New York City": "Northeast",
    "Honolulu": "Hawaii",
    "Houston": "Texas",
    "Chicago": "Midwest",
}

# ============================================================
# CITY GRID CONFIGURATIONS
# ============================================================
CITY_GRIDS = {
    "San Diego": [
        {"name": "Convoy District", "lat": 32.8329, "lng": -117.1554},
        {"name": "Mira Mesa", "lat": 32.9157, "lng": -117.1430},
        {"name": "UTC/La Jolla", "lat": 32.8721, "lng": -117.2125},
        {"name": "Kearny Mesa", "lat": 32.8342, "lng": -117.1425},
    ],
    "Los Angeles": [
        {"name": "San Gabriel", "lat": 34.0961, "lng": -118.1058},
        {"name": "Alhambra", "lat": 34.0953, "lng": -118.1270},
        {"name": "Arcadia", "lat": 34.1397, "lng": -118.0353},
        {"name": "Rowland Heights", "lat": 33.9761, "lng": -117.9053},
        {"name": "Koreatown", "lat": 34.0622, "lng": -118.3015},
        {"name": "Irvine", "lat": 33.6846, "lng": -117.8265},
    ],
    "Seattle": [
        {"name": "U-District", "lat": 47.6628, "lng": -122.3139},
        {"name": "International District", "lat": 47.5982, "lng": -122.3248},
        {"name": "Bellevue Downtown", "lat": 47.6101, "lng": -122.2015},
        {"name": "Bellevue Crossroads", "lat": 47.6172, "lng": -122.1320},
        {"name": "Redmond", "lat": 47.6740, "lng": -122.1215},
    ],
    "New York City": [
        {"name": "Flushing Main St", "lat": 40.7593, "lng": -73.8307},
        {"name": "Chinatown Manhattan", "lat": 40.7158, "lng": -73.9970},
        {"name": "Koreatown NYC", "lat": 40.7475, "lng": -73.9872},
        {"name": "Sunset Park Brooklyn", "lat": 40.6453, "lng": -74.0124},
        {"name": "Elmhurst Queens", "lat": 40.7379, "lng": -73.8795},
    ],
    "Bay Area": [
        {"name": "SF Downtown", "lat": 37.7876, "lng": -122.4066},
        {"name": "SF Sunset/Richmond", "lat": 37.7634, "lng": -122.4781},
        {"name": "Oakland/Berkeley", "lat": 37.8685, "lng": -122.2680},
        {"name": "San Jose/Cupertino", "lat": 37.3190, "lng": -122.0250},
        {"name": "Palo Alto", "lat": 37.4419, "lng": -122.1430},
        {"name": "Fremont", "lat": 37.5485, "lng": -121.9886},
    ],
    "Honolulu": [
        {"name": "Ala Moana", "lat": 21.2913, "lng": -157.8450},
        {"name": "Waikiki", "lat": 21.2782, "lng": -157.8256},
        {"name": "Kaka'ako", "lat": 21.2946, "lng": -157.8590},
        {"name": "Kaimuki", "lat": 21.2806, "lng": -157.7981},
        {"name": "University of Hawaii", "lat": 21.2989, "lng": -157.8174},
    ],
    "Houston": [
        {"name": "Bellaire Chinatown", "lat": 29.7050, "lng": -95.5450},
        {"name": "Katy Asian Town", "lat": 29.7890, "lng": -95.7830},
        {"name": "Sugar Land", "lat": 29.5950, "lng": -95.6210},
    ],
    "Chicago": [
        {"name": "Chinatown", "lat": 41.8525, "lng": -87.6322},
        {"name": "Uptown Argyle", "lat": 41.9680, "lng": -87.6565},
        {"name": "Lincoln Park", "lat": 41.9213, "lng": -87.6360},
        {"name": "The Loop", "lat": 41.8781, "lng": -87.6298},
        {"name": "Hyde Park", "lat": 41.7919, "lng": -87.5828},
        {"name": "Evanston", "lat": 42.0450, "lng": -87.6810},
    ],
}


# ============================================================
# BRAND MATCHING UTILITIES
# ============================================================
# ============================================================
# BRAND MATCHING UTILITIES
# ============================================================
def get_all_brands_for_city(city: str) -> list[dict]:
    """Get national + regional brands for a city."""
    brands = list(NATIONAL_BRANDS)
    region = CITY_REGIONS.get(city)
    if region and region in REGIONAL_BRANDS:
        brands.extend(REGIONAL_BRANDS[region])
    return brands


from app.services.brand_matcher import find_best_brand_match, match_brand_from_name


# ============================================================
# IMPORT FUNCTIONS
# ============================================================
def get_or_create_brand(db, brand_data: dict) -> "Brand":
    brand = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
    if not brand:
        # Remove aliases before creating (not a DB field)
        data = {k: v for k, v in brand_data.items() if k != "aliases"}
        brand = Brand(**data)
        db.add(brand)
        db.flush()
        print(f"    ✅ Created brand: {brand_data['name']}")
    return brand


def shop_exists(db, google_place_id: str) -> bool:
    return db.query(Shop).filter(Shop.google_place_id == google_place_id).first() is not None


async def import_brands_for_city(
    service: GooglePlacesServiceV2,
    db,
    city: str,
    session_place_ids: set,
) -> int:
    """Import all brands (national + regional) for a city."""
    brands = get_all_brands_for_city(city)
    grid = CITY_GRIDS.get(city, [])
    
    print(f"\n  🏷️  Brands: {len(brands)} | Grid: {len(grid)} points")
    
    total = 0
    for brand_data in brands:
        brand = get_or_create_brand(db, brand_data)
        brand_count = 0
        
        for point in grid:
            try:
                shops_data = await service.text_search(
                    query=f"{brand.name} boba",
                    lat=point["lat"], lng=point["lng"],
                    radius_meters=10000, max_results=60, country="US"
                )
            except Exception:
                continue
            
            for shop_data in shops_data:
                place_id = shop_data.get("google_place_id")
                if not place_id or place_id in session_place_ids:
                    continue
                if shop_exists(db, place_id):
                    session_place_ids.add(place_id)
                    continue
                
                # Verify shop matches brand
                shop_name = shop_data.get("name", "")
                
                # We are verifying against a specific target brand (brand_data)
                # Check if it matches that specific brand
                conf = match_brand_from_name(
                    shop_name, 
                    brand_data["name"], 
                    brand_data.get("name_zh"), 
                    brand_data.get("aliases")
                )
                
                if conf < 0.9:
                    continue
                
                session_place_ids.add(place_id)
                db.add(Shop(
                    name=shop_name, brand_id=brand.id,
                    address=shop_data.get("address", ""), city=city,
                    country="US", latitude=shop_data.get("latitude"),
                    longitude=shop_data.get("longitude"),
                    google_place_id=place_id, status="active",
                    last_verified=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                ))
                brand_count += 1
            
            await asyncio.sleep(0.25)
        
        if brand_count > 0:
            db.commit()
            print(f"      {brand.name}: +{brand_count}")
            total += brand_count
    
    return total


async def discovery_search(
    service: GooglePlacesServiceV2,
    db,
    city: str,
    session_place_ids: set,
) -> int:
    """
    LAYER 3: Discovery mode - search generic "boba tea" to find unlisted brands.
    Attempts to link discovered shops to known brands via fuzzy matching.
    """
    grid = CITY_GRIDS.get(city, [])
    all_brands = get_all_brands_for_city(city)
    
    # Load existing brands from DB for linking
    db_brands = db.query(Brand).all()
    
    print(f"\n  🔍 Discovery mode: searching 'boba tea' at {len(grid)} points")
    
    discovered = 0
    linked = 0
    
    for point in grid:
        try:
            shops_data = await service.text_search(
                query="boba tea",
                lat=point["lat"], lng=point["lng"],
                radius_meters=5000, max_results=60, country="US"
            )
        except Exception:
            continue
        
        for shop_data in shops_data:
            place_id = shop_data.get("google_place_id")
            if not place_id or place_id in session_place_ids:
                continue
            if shop_exists(db, place_id):
                session_place_ids.add(place_id)
                continue
            
            shop_name = shop_data.get("name", "")
            
            # Try to match to known brand
            # Convert DB brands to dicts for the matcher
            # Optimization: could do this once outside loop, but for now just map it
            # actually strict types in find_best_brand_match expect dict access.
            # Let's map db_brands to dicts
            brand_dicts = [
                {"name": b.name, "name_zh": b.name_zh, "aliases": []} # Aliases not in DB yet?
                # Wait, new module relies on aliases. DB doesn't have aliases column usually?
                # `import_us_v2.py` defined aliases in constants. DB `brands` table doesn't seem to have `aliases` column in `inspect_db` output.
                # So we lose aliases here unless we merge with constants?
                # The prompt asked to "take out BRAND_ALIASES... into a file". The `brand_matcher` has them.
                # So `match_brand_from_name` inside `find_best_brand_match` will look them up from `BRAND_ALIASES` global in module if not provided!
                # Perfect.
                for b in db_brands
            ]
            
            matched_data, confidence = find_best_brand_match(shop_name, brand_dicts)
            
            # Map back to DB object
            matched_brand = next((b for b in db_brands if b.name == matched_data["name"]), None) if matched_data else None
            
            session_place_ids.add(place_id)
            
            shop = Shop(
                name=shop_name,
                brand_id=matched_brand.id if matched_brand else None,
                address=shop_data.get("address", ""),
                city=city, country="US",
                latitude=shop_data.get("latitude"),
                longitude=shop_data.get("longitude"),
                google_place_id=place_id,
                status="active",
                last_verified=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
            )
            db.add(shop)
            discovered += 1
            
            if matched_brand:
                linked += 1
                print(f"      🔗 {shop_name} → {matched_brand.name}")
            else:
                print(f"      🆕 {shop_name} (independent)")
        
        await asyncio.sleep(0.25)
    
    db.commit()
    print(f"  📊 Discovery: {discovered} total, {linked} linked to brands")
    return discovered


async def import_city(service, db, city: str, session_place_ids: set, discover: bool = True) -> int:
    """Import a single city using all three layers."""
    print(f"\n{'='*60}")
    print(f"🏙️  {city}")
    print(f"{'='*60}")
    
    total = 0
    
    # Layer 1 & 2: National + Regional brands
    total += await import_brands_for_city(service, db, city, session_place_ids)
    
    # Layer 3: Discovery
    if discover:
        total += await discovery_search(service, db, city, session_place_ids)
    
    return total


def sync_to_database(target_url: str):
    """Sync all US shops to production with optimized bulk checks."""
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)
    
    print("🔄 Syncing to production...")
    
    source_db = SessionLocal()
    target_engine = create_engine(target_url)
    TargetSession = sessionmaker(bind=target_engine)
    target_db = TargetSession()
    
    try:
        Base.metadata.create_all(bind=target_engine)
        
        us_shops = source_db.query(Shop).filter(Shop.country == "US").all()
        brand_ids = set(s.brand_id for s in us_shops if s.brand_id)
        local_brands = source_db.query(Brand).filter(Brand.id.in_(brand_ids)).all()
        
        # 1. OPTIMIZED BRAND SYNC: Fetch all existing target brands once
        target_brands = target_db.query(Brand).all()
        brand_map_by_name = {b.name: b.id for b in target_brands}
        brand_id_map = {} # Maps local_id -> target_id
        
        brands_added = 0
        for b in local_brands:
            if b.name in brand_map_by_name:
                brand_id_map[b.id] = brand_map_by_name[b.name]
            else:
                new = Brand(
                    name=b.name, 
                    name_zh=b.name_zh, 
                    description=b.description, 
                    origin_country=b.origin_country
                )
                target_db.add(new)
                target_db.flush() # Get the new ID
                brand_id_map[b.id] = new.id
                brand_map_by_name[b.name] = new.id
                brands_added += 1
        
        target_db.commit()
        if brands_added:
            print(f"✅ Created {brands_added} new brands")

        # 2. OPTIMIZED SHOP SYNC: Fetch ALL existing Google Place IDs from target once
        print("🔍 Checking for existing shops in target...")
        existing_target_ids = {
            id[0] for id in target_db.query(Shop.google_place_id).filter(Shop.google_place_id.isnot(None)).all()
        }
        
        added = 0
        skipped = 0
        for s in us_shops:
            if s.google_place_id and s.google_place_id in existing_target_ids:
                skipped += 1
                continue
            
            target_db.add(Shop(
                name=s.name, 
                brand_id=brand_id_map.get(s.brand_id),
                address=s.address, 
                city=s.city, 
                country=s.country,
                latitude=s.latitude, 
                longitude=s.longitude,
                google_place_id=s.google_place_id, 
                status=s.status,
                last_verified=s.last_verified, 
                created_at=s.created_at,
            ))
            added += 1
            
            # Commit in batches for very large imports
            if added % 100 == 0:
                target_db.flush()

        target_db.commit()
        print(f"✅ Sync complete: {added} added, {skipped} skipped.")
        
        # Reset sequences for PostgreSQL
        target_db.execute(text("SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id) FROM brands), 1), true)"))
        target_db.execute(text("SELECT setval('shops_id_seq', COALESCE((SELECT MAX(id) FROM shops), 1), true)"))
        target_db.commit()
        
        print(f"✅ Synced {added} new shops")
    finally:
        source_db.close()
        target_db.close()


async def main():
    parser = argparse.ArgumentParser(description="US Boba Import v2 - Better Brand Coverage")
    parser.add_argument("--city", type=str, help="Single city to import")
    parser.add_argument("--discover-only", action="store_true", help="Only run discovery mode")
    parser.add_argument("--no-discover", action="store_true", help="Skip discovery mode")
    parser.add_argument("--sync-to", type=str, help="Sync to production DB")
    args = parser.parse_args()
    
    if args.sync_to:
        sync_to_database(args.sync_to)
        return
    
    print("=" * 60)
    print("🧋 US BOBA IMPORT v2 - Three-Layer Strategy")
    print("=" * 60)
    print(f"📋 National brands: {len(NATIONAL_BRANDS)}")
    print(f"📋 Regional groups: {len(REGIONAL_BRANDS)}")
    print(f"🏙️  Cities: {', '.join(CITY_GRIDS.keys())}")
    print()
    
    service = GooglePlacesServiceV2()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return
    
    db = SessionLocal()
    
    try:
        existing = db.query(Shop.google_place_id).all()
        session_place_ids = set(id[0] for id in existing if id[0])
        print(f"📥 Loaded {len(session_place_ids)} existing place IDs\n")
        
        cities = [args.city] if args.city else list(CITY_GRIDS.keys())
        discover = not args.no_discover
        
        grand_total = 0
        for city in cities:
            if args.discover_only:
                count = await discovery_search(service, db, city, session_place_ids)
            else:
                count = await import_city(service, db, city, session_place_ids, discover=discover)
            grand_total += count
        
        print(f"\n{'='*60}")
        print(f"✅ COMPLETE! Imported {grand_total} shops")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
