"""
Import real Taiwan boba shop data from Google Places API.

Usage:
    # Dry run (no database writes)
    python import_places.py --dry-run

    # Test with single brand
    python import_places.py --brands "50嵐" --cities "Taipei"

    # Full import
    python import_places.py

    # Clear existing data before import
    python import_places.py --clear
"""

import asyncio
import argparse
import sys
from typing import Optional

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv("../.env")  # Load from project root

# Add parent directory for imports
sys.path.insert(0, ".")

from app.database import SessionLocal, engine, Base
from app.models import Brand, Shop
from app.services.google_places import GooglePlacesService

# Create tables
Base.metadata.create_all(bind=engine)

# Priority brands from research
BRANDS = [
    {"name": "清心福全", "name_zh": "清心福全", "description": "Largest chain by store count (900+)", "origin_country": "TW"},
    {"name": "50嵐", "name_zh": "50嵐", "description": "Iconic Taiwan brand, #2 by stores", "origin_country": "TW", "website": "https://www.50lan.com.tw/"},
    {"name": "CoCo都可", "name_zh": "CoCo都可", "description": "International chain with 5000+ global locations", "origin_country": "TW", "website": "https://www.coco-tea.com/"},
    {"name": "麻古茶坊", "name_zh": "麻古茶坊", "description": "Fruit tea specialty, #3 market share", "origin_country": "TW"},
    {"name": "迷客夏", "name_zh": "迷客夏", "description": "Fresh milk tea specialist", "origin_country": "TW", "website": "https://www.milkshoptea.com/"},
    {"name": "大苑子", "name_zh": "大苑子", "description": "Fresh fruit juice and tea", "origin_country": "TW"},
    {"name": "茶的魔手", "name_zh": "茶的魔手", "description": "South Taiwan champion, 500+ stores", "origin_country": "TW"},
    {"name": "得正", "name_zh": "得正", "description": "Oolong tea specialist, #4 by sales", "origin_country": "TW"},
    {"name": "可不可熟成紅茶", "name_zh": "可不可熟成紅茶", "description": "Premium aged black tea", "origin_country": "TW"},
    {"name": "茶湯會", "name_zh": "茶湯會", "description": "Part of 六角集團", "origin_country": "TW"},
    {"name": "一沐日", "name_zh": "一沐日", "description": "Rising Gen-Z favorite, mochi toppings", "origin_country": "TW"},
    {"name": "龜記", "name_zh": "龜記", "description": "Trendy specialty drinks", "origin_country": "TW"},
    {"name": "八曜和茶", "name_zh": "八曜和茶", "description": "High social buzz ranking", "origin_country": "TW"},
    {"name": "五桐號", "name_zh": "五桐號", "description": "Almond jelly specialty", "origin_country": "TW"},
    {"name": "UG樂己", "name_zh": "UG樂己", "description": "Popular chain brand", "origin_country": "TW"},
]

# Major Taiwan cities with coordinates for location bias
# Using Chinese names for better search results
CITIES = {
    "Taipei": {"location": "25.0330,121.5654", "region": "tw", "zh": "台北"},
    "New Taipei": {"location": "25.0120,121.4650", "region": "tw", "zh": "新北"},
    "Taoyuan": {"location": "24.9936,121.3010", "region": "tw", "zh": "桃園"},
    "Taichung": {"location": "24.1477,120.6736", "region": "tw", "zh": "台中"},
    "Tainan": {"location": "22.9998,120.2270", "region": "tw", "zh": "台南"},
    "Kaohsiung": {"location": "22.6273,120.3014", "region": "tw", "zh": "高雄"},
    "Hsinchu": {"location": "24.8066,120.9686", "region": "tw", "zh": "新竹"},
    "Changhua": {"location": "24.0734,120.5134", "region": "tw", "zh": "彰化"},
}

# Brand name variations for flexible matching
BRAND_ALIASES = {
    "龜記": ["龜記", "Guiji", "GUIJI", "龜記茗品"],
    "CoCo都可": ["CoCo", "都可", "coco"],
    "50嵐": ["50嵐", "50 Lan", "五十嵐"],
    "清心福全": ["清心", "清心福全"],
    "一沐日": ["一沐日", "YIMU"],
    "UG樂己": ["UG", "樂己", "UG樂己"],
}


def get_or_create_brand(db, brand_data: dict) -> Brand:
    """Get existing brand or create new one."""
    brand = db.query(Brand).filter(Brand.name == brand_data["name"]).first()
    if not brand:
        brand = Brand(**brand_data)
        db.add(brand)
        db.flush()
        print(f"  ✅ Created brand: {brand_data['name']}")
    return brand


def shop_exists(db, google_place_id: str) -> bool:
    """Check if shop already exists by Google Place ID."""
    return db.query(Shop).filter(Shop.google_place_id == google_place_id).first() is not None


def extract_city_from_address(address: str) -> Optional[str]:
    """Try to extract city name from address."""
    for city in CITIES.keys():
        if city in address:
            return city
    # Check Chinese city names
    city_zh_map = {
        "台北": "Taipei", "臺北": "Taipei",
        "新北": "New Taipei",
        "桃園": "Taoyuan",
        "台中": "Taichung", "臺中": "Taichung",
        "台南": "Tainan", "臺南": "Tainan",
        "高雄": "Kaohsiung",
        "新竹": "Hsinchu",
        "彰化": "Changhua",
    }
    for zh, en in city_zh_map.items():
        if zh in address:
            return en
    return None


async def import_brand_shops(
    service: GooglePlacesService,
    db,
    brand: Brand,
    cities: list[str],
    dry_run: bool = False
) -> int:
    """Import shops for a single brand across specified cities."""
    imported = 0
    skipped = 0
    
    for city in cities:
        city_info = CITIES.get(city)
        if not city_info:
            continue
        
        # Search for this brand in this city (use Chinese city name)
        city_zh = city_info.get("zh", city)
        query = f"{brand.name} {city_zh}"
        print(f"    🔍 Searching: {query}")
        
        try:
            shops_data, _ = await service.text_search(
                query=query,
                region=city_info["region"],
                location=city_info["location"]
            )
        except Exception as e:
            print(f"    ❌ Error searching {query}: {e}")
            continue
        
        for shop_data in shops_data:
            # Skip if no place ID
            if not shop_data.get("google_place_id"):
                continue
            
            # Skip duplicates
            if shop_exists(db, shop_data["google_place_id"]):
                skipped += 1
                continue
            
            # Skip if name doesn't contain brand name or alias (false positive filter)
            shop_name = shop_data.get("name", "")
            brand_matches = [brand.name] + BRAND_ALIASES.get(brand.name, [])
            if not any(alias in shop_name for alias in brand_matches):
                continue
            
            if dry_run:
                print(f"      [DRY RUN] Would import: {shop_data['name']}")
                imported += 1
                continue
            
            # Create shop
            shop = Shop(
                name=shop_data["name"],
                brand_id=brand.id,
                address=shop_data.get("address", ""),
                city=extract_city_from_address(shop_data.get("address", "")) or city,
                country=shop_data.get("country", "TW"),
                latitude=shop_data.get("latitude"),
                longitude=shop_data.get("longitude"),
                rating=shop_data.get("rating"),
                rating_count=shop_data.get("rating_count"),
                google_place_id=shop_data.get("google_place_id"),
                photo_url=shop_data.get("photo_url"),
            )
            db.add(shop)
            imported += 1
            print(f"      ✅ Imported: {shop_data['name']}")
        
        # Small delay between city searches
        await asyncio.sleep(0.5)
    
    if skipped > 0:
        print(f"    ⏭️  Skipped {skipped} duplicate(s)")
    
    return imported


async def main():
    parser = argparse.ArgumentParser(description="Import Taiwan boba shops from Google Places API")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to database")
    parser.add_argument("--clear", action="store_true", help="Clear existing shop data before import")
    parser.add_argument("--brands", type=str, help="Comma-separated brand names to import (default: all)")
    parser.add_argument("--cities", type=str, help="Comma-separated cities to search (default: all)")
    args = parser.parse_args()
    
    # Parse filters
    brand_filter = [b.strip() for b in args.brands.split(",")] if args.brands else None
    city_filter = [c.strip() for c in args.cities.split(",")] if args.cities else list(CITIES.keys())
    
    print("=" * 60)
    print("🧋 Taiwan Boba Shop Importer")
    print("=" * 60)
    
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
    
    # Initialize
    service = GooglePlacesService()
    if not service.api_key:
        print("❌ Error: GOOGLE_PLACES_API_KEY not set in environment")
        return
    
    db = SessionLocal()
    
    try:
        # Clear existing data if requested
        if args.clear and not args.dry_run:
            print("\n🗑️  Clearing existing data...")
            db.query(Shop).delete()
            db.query(Brand).delete()
            db.commit()
            print("   ✅ Cleared shops and brands")
        
        # Filter brands to import
        brands_to_import = BRANDS
        if brand_filter:
            brands_to_import = [b for b in BRANDS if b["name"] in brand_filter]
        
        print(f"\n📦 Importing {len(brands_to_import)} brand(s) across {len(city_filter)} city/cities")
        print(f"   Brands: {', '.join(b['name'] for b in brands_to_import)}")
        print(f"   Cities: {', '.join(city_filter)}")
        
        total_imported = 0
        
        for brand_data in brands_to_import:
            print(f"\n🏷️  {brand_data['name']}")
            
            # Get or create brand
            if not args.dry_run:
                brand = get_or_create_brand(db, brand_data)
            else:
                brand = type('Brand', (), {'id': 0, 'name': brand_data['name']})()
            
            # Import shops for this brand
            count = await import_brand_shops(
                service=service,
                db=db,
                brand=brand,
                cities=city_filter,
                dry_run=args.dry_run
            )
            total_imported += count
        
        if not args.dry_run:
            db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Import complete! {total_imported} shop(s) imported")
        print("=" * 60)
        
        # Show stats
        if not args.dry_run:
            brand_count = db.query(Brand).count()
            shop_count = db.query(Shop).count()
            print(f"\n📊 Database now contains:")
            print(f"   • {brand_count} brands")
            print(f"   • {shop_count} shops")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
