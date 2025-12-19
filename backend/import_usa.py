"""
Import US boba shop data from Google Places API.
Focuses on major hubs: Seattle, Bay Area, LA, San Diego, NYC.

Usage:
    # Dry run
    python import_usa.py --dry-run

    # Test specific brand
    python import_usa.py --dry-run --brands "Boba Guys"

    # Full import to local
    python import_usa.py

    # Sync to production (NO API calls)
    python import_usa.py --sync-to "postgresql://..."
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

# US Boba Brands - Hybrid Strategy
BRANDS = [
    # Tier 1 - National/International Chains
    {"name": "Kung Fu Tea", "name_zh": "功夫茶", "description": "Largest bubble tea franchise in the US", "origin_country": "US"},
    {"name": "Gong Cha", "name_zh": "貢茶", "description": "International favorite, known for milk foam", "origin_country": "TW"},
    {"name": "Sharetea", "name_zh": "歇腳亭", "description": "Classic Taiwanese bubble tea chain", "origin_country": "TW"},
    {"name": "Sunright Tea Studio", "name_zh": "日青良月", "description": "Popular SoCal lifestyle tea brand", "origin_country": "US"},
    {"name": "Happy Lemon", "name_zh": "快樂檸檬", "description": "Inventors of rock salt cheese tea", "origin_country": "CN"},
    {"name": "The Alley", "name_zh": "鹿角巷", "description": "Deerioca tapioca pearls specialty", "origin_country": "TW"},
    {"name": "Tiger Sugar", "name_zh": "老虎堂", "description": "Original brown sugar boba milk", "origin_country": "TW"},
    {"name": "CoCo Fresh Tea & Juice", "name_zh": "CoCo都可", "description": "Massive global chain", "origin_country": "TW"},
    {"name": "Wushiland Boba", "name_zh": "50嵐", "description": "US branch of Taiwan's famous 50 Lan", "origin_country": "TW"},
    {"name": "Yi Fang Taiwan Fruit Tea", "name_zh": "一芳", "description": "Traditional fruit teas", "origin_country": "TW"},

    # Tier 2 - Regional Favorites
    # Seattle
    {"name": "Oasis Tea Zone", "name_zh": "Oasis", "description": "Seattle staple since 2001", "origin_country": "US"},
    {"name": "Don't Yell At Me", "name_zh": "不要對我尖叫", "description": "Trendy aesthetic tea shop", "origin_country": "TW"},
    {"name": "Atulea", "name_zh": "Atulea", "description": "Matcha and cheese tea specialist", "origin_country": "US"},
    
    # Bay Area
    {"name": "Boba Guys", "name_zh": "Boba Guys", "description": "Iconic SF brand, house-made ingredients", "origin_country": "US"},
    {"name": "Asha Tea House", "name_zh": "Asha", "description": "High quality whole leaf teas", "origin_country": "US"},
    {"name": "TP Tea", "name_zh": "茶湯會", "description": "Chun Shui Tang's beverage brand", "origin_country": "TW"},
    {"name": "Urban Ritual", "name_zh": "Urban Ritual", "description": "Creative craft boba drinks", "origin_country": "US"},
    {"name": "Feng Cha", "name_zh": "奉茶", "description": "Dessert and tea specialist", "origin_country": "CN"},
    
    # Los Angeles / SGV
    {"name": "ChiCha San Chen", "name_zh": "吃茶三千", "description": "Michelin-rated tea from Taiwan", "origin_country": "TW"},
    {"name": "Half & Half Tea Express", "name_zh": "伴伴堂", "description": "SGV classic, huge cups", "origin_country": "US"},
    {"name": "7 Leaves Cafe", "name_zh": "7 Leaves", "description": "Vietnamese-style coffee and tea", "origin_country": "US"},
    {"name": "Bopomofo Cafe", "name_zh": "Bopomofo", "description": "Phil Wang's cafe, Asian-American fusion", "origin_country": "US"},
    {"name": "Meet Fresh", "name_zh": "鮮芋仙", "description": "Taiwanese desserts and herbal tea", "origin_country": "TW"},
    
    # San Diego
    {"name": "Camellia Rd Tea Bar", "name_zh": "Camellia Rd", "description": "San Diego local high quality tea", "origin_country": "US"},
    {"name": "Omomo Tea Shoppe", "name_zh": "Omomo", "description": "Famous for matcha and cream toppings", "origin_country": "US"},
    {"name": "Daboba", "name_zh": "熊黑堂", "description": "Honey golden boba specialty", "origin_country": "MY"},
    
    # NYC
    {"name": "Moge Tee", "name_zh": "愿茶", "description": "Global cheese tea chain", "origin_country": "CN"},
    {"name": "ViVi Bubble Tea", "name_zh": "ViVi", "description": "NYC staple with cotton candy themes", "origin_country": "US"},
    {"name": "Machi Machi", "name_zh": "麥吉", "description": "Jay Chou's favorite milk tea", "origin_country": "TW"},
    {"name": "Ten Ren's Tea", "name_zh": "天仁茗茶", "description": "Traditional tea legend", "origin_country": "TW"},
    {"name": "Xing Fu Tang", "name_zh": "幸福堂", "description": "Stir-fried brown sugar boba", "origin_country": "TW"},
]

# US High-Density Boba Hubs
US_GRID = [
    # Seattle
    {"name": "Seattle (U-District)", "lat": 47.6628, "lng": -122.3139},
    {"name": "Bellevue", "lat": 47.6101, "lng": -122.2015},
    
    # Bay Area
    {"name": "San Francisco (Sunset)", "lat": 37.7587, "lng": -122.4757},
    {"name": "Berkeley", "lat": 37.8715, "lng": -122.2730},
    {"name": "San Jose (Downtown)", "lat": 37.3382, "lng": -121.8863},
    {"name": "Cupertino", "lat": 37.3230, "lng": -122.0322},
    
    # Los Angeles Area
    {"name": "San Gabriel Valley", "lat": 34.0967, "lng": -118.1058},
    {"name": "West LA (Sawtelle)", "lat": 34.0449, "lng": -118.4455},
    {"name": "Irvine", "lat": 33.6846, "lng": -117.8265},
    
    # San Diego
    {"name": "San Diego (Convoy)", "lat": 32.8329, "lng": -117.1554},
    
    # NYC
    {"name": "NYC (East Village)", "lat": 40.7295, "lng": -73.9874},
    {"name": "NYC (Chinatown)", "lat": 40.7152, "lng": -73.9974},
    {"name": "Queens (Flushing)", "lat": 40.7593, "lng": -73.8307},
]

# Brand Aliases
BRAND_ALIASES = {
    "Kung Fu Tea": ["Kung Fu Tea", "KFT", "功夫茶"],
    "Gong Cha": ["Gong Cha", "貢茶", "GongCha"],
    "Sharetea": ["Sharetea", "歇腳亭"],
    "Sunright Tea Studio": ["Sunright", "Sunright Tea", "日青良月"],
    "Happy Lemon": ["Happy Lemon", "快樂檸檬"],
    "The Alley": ["The Alley", "鹿角巷"],
    "Tiger Sugar": ["Tiger Sugar", "老虎堂"],
    "CoCo Fresh Tea & Juice": ["CoCo", "CoCo都可", "Coco Fresh"],
    "Wushiland Boba": ["Wushiland", "50嵐", "50 Lan"],
    "Yi Fang Taiwan Fruit Tea": ["Yi Fang", "一芳", "Yifang"],
    "Oasis Tea Zone": ["Oasis Tea", "Oasis"],
    "Don't Yell At Me": ["Don't Yell At Me", "不要對我尖叫"],
    "Atulea": ["Atulea"],
    "Boba Guys": ["Boba Guys"],
    "Asha Tea House": ["Asha Tea", "Asha"],
    "TP Tea": ["TP Tea", "茶湯會"],
    "Urban Ritual": ["Urban Ritual"],
    "Feng Cha": ["Feng Cha", "奉茶"],
    "ChiCha San Chen": ["ChiCha", "吃茶三千", "Chicha San Chen"],
    "Half & Half Tea Express": ["Half & Half", "伴伴堂"],
    "7 Leaves Cafe": ["7 Leaves", "Seven Leaves"],
    "Bopomofo Cafe": ["Bopomofo"],
    "Meet Fresh": ["Meet Fresh", "鮮芋仙"],
    "Camellia Rd Tea Bar": ["Camellia Rd"],
    "Omomo Tea Shoppe": ["Omomo"],
    "Daboba": ["Daboba", "熊黑堂"],
    "Moge Tee": ["Moge Tee", "愿茶", "Moge"],
    "ViVi Bubble Tea": ["ViVi", "Vivi Bubble Tea"],
    "Machi Machi": ["Machi Machi", "麥吉"],
    "Ten Ren's Tea": ["Ten Ren", "天仁茗茶", "Ten Ren's"],
    "Xing Fu Tang": ["Xing Fu Tang", "幸福堂"],
}


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


def matches_brand(shop_name: str, brand_name: str) -> bool:
    """Check if shop name matches the brand (including aliases)."""
    aliases = [brand_name] + BRAND_ALIASES.get(brand_name, [])
    return any(alias.lower() in shop_name.lower() for alias in aliases)


def extract_region(lat: float, lng: float) -> str:
    """Estimate region from coordinates."""
    if lat > 46: 
        return "Washington (Seattle)"
    if lng > -75: 
        return "New York (NYC)"
    if lat > 36: 
        return "California (Bay Area)"
    if lat < 33.5: 
        return "California (San Diego)"
    return "California (Los Angeles)"


def sync_to_database(target_url: str):
    """
    Sync US shops from local database to target database.
    NO API calls - just copies existing data.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql://", 1)
    
    print("=" * 60)
    print("🔄 US Data Sync (No API calls)")
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
        
        # Get all US shops (excluding SG, TW)
        us_shops = source_db.query(Shop).filter(
            Shop.country == "US",
            Shop.city.in_([
                "Washington (Seattle)", "New York (NYC)", 
                "California (Bay Area)", "California (San Diego)", 
                "California (Los Angeles)"
            ])
        ).all()
        
        print(f"📊 Found {len(us_shops)} US shops to sync")
        
        # Sync brands
        us_brand_ids = set(shop.brand_id for shop in us_shops if shop.brand_id)
        us_brands = source_db.query(Brand).filter(Brand.id.in_(us_brand_ids)).all()
        print(f"🏷️  Found {len(us_brands)} brands to sync")
        
        brand_id_map = {}
        brands_added = 0
        
        for brand in us_brands:
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
        
        target_db.execute(text("SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id) FROM brands), 1), true)"))
        target_db.execute(text("SELECT setval('shops_id_seq', COALESCE((SELECT MAX(id) FROM shops), 1), true)"))
        target_db.commit()
        
        print(f"\n✅ Sync complete! +{shops_added} new shops")
        
    except Exception as e:
        target_db.rollback()
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
        print(f"    📍 {point['name']}")
        
        try:
            shops_data = await service.nearby_search_all_pages(
                lat=point["lat"],
                lng=point["lng"],
                keyword=brand.name,
                radius_meters=15000,
                country="US",
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
            
            if place_id in session_place_ids:
                skipped_dup += 1
                continue
            
            if shop_exists(db, place_id):
                session_place_ids.add(place_id)
                skipped_dup += 1
                continue
            
            shop_name = shop_data.get("name", "")
            if not matches_brand(shop_name, brand.name):
                skipped_name += 1
                continue
            
            session_place_ids.add(place_id)
            
            if dry_run:
                print(f"      [DRY] {shop_name}")
                imported += 1
                point_imported += 1
                continue
            
            shop = Shop(
                name=shop_name,
                brand_id=brand.id,
                address=shop_data.get("address", ""),
                city=extract_region(shop_data.get("latitude", 0), shop_data.get("longitude", 0)),
                country="US",
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
        
        await asyncio.sleep(0.3)
    
    return imported


async def main():
    parser = argparse.ArgumentParser(description="Import US boba shops from Google Places API")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to database")
    parser.add_argument("--brands", type=str, help="Comma-separated brand names")
    parser.add_argument("--sync-to", type=str, dest="sync_to", help="Sync to target DB")
    args = parser.parse_args()
    
    if args.sync_to:
        sync_to_database(args.sync_to)
        return
    
    brand_filter = [b.strip() for b in args.brands.split(",")] if args.brands else None
    
    # Show which database we're using
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./boba_seeker.db")
    if "postgresql" in db_url:
        db_type = "🐘 PostgreSQL (Production)"
    else:
        db_type = "📁 SQLite (Local)"
    
    print("=" * 60)
    print("🧋 US Boba Shop Importer")
    print("=" * 60)
    print(f"💾 Database: {db_type}")
    print(f"📍 Grid points: {len(US_GRID)}")
    print(f"🏷️  Brands: {len(BRANDS)}")
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE")
    
    service = GooglePlacesService()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return
    
    db = SessionLocal()
    
    try:
        existing_shops = db.query(Shop).count()
        existing_us_shops = db.query(Shop).filter(Shop.country == "US").count()
        print(f"\n📊 Existing shops: {existing_shops} total, {existing_us_shops} in US")
        
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
                grid_points=US_GRID,
                session_place_ids=session_place_ids,
                dry_run=args.dry_run
            )
            total_imported += count
            
            if not args.dry_run:
                db.commit()
                print(f"    💾 Committed {brand.name}")
        
        print("\n" + "=" * 60)
        print(f"✅ Import complete! +{total_imported} new shops")
        print("=" * 60)
        
        if not args.dry_run:
            new_total = db.query(Shop).count()
            new_us_total = db.query(Shop).filter(Shop.country == "US").count()
            print(f"\n📊 Database now contains:")
            print(f"   • {new_total} total shops")
            print(f"   • {new_us_total} US shops (+{new_us_total - existing_us_shops})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
