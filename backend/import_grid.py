# ruff: noqa: E402
"""
Grid-based import for complete Taiwan coverage.

Uses Nearby Search API with a grid of points covering all of Taiwan.
More efficient than text search for systematic coverage.

Usage:
    # Dry run
    python import_grid.py --dry-run

    # Import specific brand
    python import_grid.py --brands "50嵐"

    # Full import (fills gaps, keeps existing data)
    python import_grid.py
"""

import argparse
import asyncio
import sys
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv

load_dotenv("../.env")

sys.path.insert(0, ".")

from app.database import Base, SessionLocal, engine
from app.models import Brand, Shop
from app.services.brand_matcher import match_brand_from_name
from app.services.google_places import GooglePlacesService


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
    return (
        db.query(Shop).filter(Shop.google_place_id == google_place_id).first()
        is not None
    )


Base.metadata.create_all(bind=engine)

# Priority brands
BRANDS = [
    {
        "name": "清心福全",
        "name_zh": "清心福全",
        "description": "Largest chain by store count (900+)",
        "origin_country": "TW",
    },
    {
        "name": "50嵐",
        "name_zh": "50嵐",
        "description": "Iconic Taiwan brand, #2 by stores",
        "origin_country": "TW",
    },
    {
        "name": "CoCo都可",
        "name_zh": "CoCo都可",
        "description": "International chain",
        "origin_country": "TW",
    },
    {
        "name": "麻古茶坊",
        "name_zh": "麻古茶坊",
        "description": "Fruit tea specialty",
        "origin_country": "TW",
    },
    {
        "name": "迷客夏",
        "name_zh": "迷客夏",
        "description": "Fresh milk tea specialist",
        "origin_country": "TW",
    },
    {
        "name": "大苑子",
        "name_zh": "大苑子",
        "description": "Fresh fruit juice and tea",
        "origin_country": "TW",
    },
    {
        "name": "茶的魔手",
        "name_zh": "茶的魔手",
        "description": "South Taiwan champion",
        "origin_country": "TW",
    },
    {
        "name": "得正",
        "name_zh": "得正",
        "description": "Oolong tea specialist",
        "origin_country": "TW",
    },
    {
        "name": "可不可熟成紅茶",
        "name_zh": "可不可熟成紅茶",
        "description": "Premium aged black tea",
        "origin_country": "TW",
    },
    {
        "name": "茶湯會",
        "name_zh": "茶湯會",
        "description": "Part of 六角集團",
        "origin_country": "TW",
    },
    {
        "name": "一沐日",
        "name_zh": "一沐日",
        "description": "Rising Gen-Z favorite",
        "origin_country": "TW",
    },
    {
        "name": "龜記",
        "name_zh": "龜記",
        "description": "Trendy specialty drinks",
        "origin_country": "TW",
    },
    {
        "name": "八曜和茶",
        "name_zh": "八曜和茶",
        "description": "High social buzz",
        "origin_country": "TW",
    },
    {
        "name": "五桐號",
        "name_zh": "五桐號",
        "description": "Almond jelly specialty",
        "origin_country": "TW",
    },
    {
        "name": "UG樂己",
        "name_zh": "UG樂己",
        "description": "Popular chain brand",
        "origin_country": "TW",
    },
]

# Grid points covering all of Taiwan
# Each point covers ~25km radius, overlapping for complete coverage
# Taiwan: ~22°N to 25.3°N latitude, ~120°E to 122°E longitude
TAIWAN_GRID = [
    # North (Taipei, New Taipei, Keelung, Yilan)
    {"name": "Taipei City", "lat": 25.0330, "lng": 121.5654},
    {"name": "Taipei North", "lat": 25.1200, "lng": 121.5200},
    {"name": "New Taipei West", "lat": 25.0100, "lng": 121.4300},
    {"name": "New Taipei East", "lat": 25.0000, "lng": 121.7500},
    {"name": "Keelung", "lat": 25.1276, "lng": 121.7392},
    {"name": "Yilan", "lat": 24.7570, "lng": 121.7533},
    # Northwest (Taoyuan, Hsinchu, Miaoli)
    {"name": "Taoyuan City", "lat": 24.9936, "lng": 121.3010},
    {"name": "Taoyuan Airport", "lat": 25.0777, "lng": 121.2329},
    {"name": "Zhongli", "lat": 24.9537, "lng": 121.2249},
    {"name": "Hsinchu City", "lat": 24.8066, "lng": 120.9686},
    {"name": "Hsinchu County", "lat": 24.8387, "lng": 121.0178},
    {"name": "Miaoli", "lat": 24.5602, "lng": 120.8214},
    # Central (Taichung, Changhua, Nantou)
    {"name": "Taichung City", "lat": 24.1477, "lng": 120.6736},
    {"name": "Taichung North", "lat": 24.2500, "lng": 120.7000},
    {"name": "Taichung South", "lat": 24.0500, "lng": 120.6500},
    {"name": "Changhua City", "lat": 24.0734, "lng": 120.5134},
    {"name": "Changhua Coast", "lat": 24.0500, "lng": 120.4000},
    {"name": "Nantou", "lat": 23.9158, "lng": 120.6873},
    {"name": "Puli", "lat": 23.9659, "lng": 120.9692},
    # Southwest (Yunlin, Chiayi, Tainan)
    {"name": "Yunlin", "lat": 23.7092, "lng": 120.4313},
    {"name": "Chiayi City", "lat": 23.4801, "lng": 120.4491},
    {"name": "Chiayi County", "lat": 23.4518, "lng": 120.2555},
    {"name": "Tainan North", "lat": 23.1500, "lng": 120.2000},
    {"name": "Tainan City", "lat": 22.9998, "lng": 120.2270},
    {"name": "Tainan South", "lat": 22.9000, "lng": 120.2000},
    # South (Kaohsiung, Pingtung)
    {"name": "Kaohsiung City", "lat": 22.6273, "lng": 120.3014},
    {"name": "Kaohsiung North", "lat": 22.7500, "lng": 120.3500},
    {"name": "Kaohsiung South", "lat": 22.5000, "lng": 120.4000},
    {"name": "Fengshan", "lat": 22.6271, "lng": 120.3568},
    {"name": "Pingtung City", "lat": 22.6762, "lng": 120.4929},
    {"name": "Pingtung South", "lat": 22.4500, "lng": 120.5500},
    # East (Hualien, Taitung)
    {"name": "Hualien City", "lat": 23.9871, "lng": 121.6015},
    {"name": "Hualien South", "lat": 23.7500, "lng": 121.4500},
    {"name": "Taitung City", "lat": 22.7583, "lng": 121.1444},
    {"name": "Taitung North", "lat": 23.1000, "lng": 121.2000},
    # Islands (Penghu only - Kinmen/Matsu are far)
    {"name": "Penghu", "lat": 23.5711, "lng": 119.5793},
]


def extract_city(lat: float, lng: float) -> str:
    """Estimate city from coordinates."""
    # Simplified city detection based on lat/lng ranges
    if lat > 24.9 and lng > 121.4:
        return "Taipei"
    elif lat > 24.9 and lng < 121.4:
        return "Taoyuan"
    elif 24.0 < lat < 24.5:
        return "Taichung"
    elif 22.9 < lat < 23.3:
        return "Tainan"
    elif lat < 22.9:
        return "Kaohsiung"
    elif lng > 121.5:
        return "Hualien"
    else:
        return "Taiwan"


async def import_brand_grid(
    service: GooglePlacesService,
    db,
    brand: Brand,
    grid_points: list[dict],
    session_place_ids: set,  # Track IDs added this session
    dry_run: bool = False,
) -> int:
    """Import shops for a brand using grid-based nearby search."""
    imported = 0
    skipped_dup = 0
    skipped_name = 0

    for point in grid_points:
        print(f"    📍 {point['name']} ({point['lat']:.2f}, {point['lng']:.2f})")

        try:
            shops_data = await service.nearby_search_all_pages(
                lat=point["lat"],
                lng=point["lng"],
                keyword=brand.name,
                radius_meters=25000,  # 25km radius
                country="TW",
                max_results=60,
            )
        except Exception as e:
            print(f"      ❌ Error: {e}")
            continue

        point_imported = 0
        for shop_data in shops_data:
            place_id = shop_data.get("google_place_id")
            if not place_id:
                continue

            # Skip if already added this session (handles overlapping grids)
            if place_id in session_place_ids:
                skipped_dup += 1
                continue

            # Skip if already in database
            if shop_exists(db, place_id):
                session_place_ids.add(place_id)  # Remember for future checks
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

            # Create shop with maintenance fields
            shop = Shop(
                name=shop_name,
                brand_id=brand.id,
                address=shop_data.get("address", ""),
                city=extract_city(
                    shop_data.get("latitude", 0), shop_data.get("longitude", 0)
                ),
                country="TW",
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

    print(
        f"    📊 Total: +{imported} new, {skipped_dup} duplicates, "
        f"{skipped_name} non-matching"
    )
    return imported


async def main():
    parser = argparse.ArgumentParser(description="Grid-based Taiwan boba shop import")
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't write to database"
    )
    parser.add_argument("--brands", type=str, help="Comma-separated brand names")
    args = parser.parse_args()

    brand_filter = [b.strip() for b in args.brands.split(",")] if args.brands else None

    print("=" * 60)
    print("🧋 Grid-Based Taiwan Boba Shop Importer")
    print("=" * 60)
    print(f"📍 Grid points: {len(TAIWAN_GRID)}")
    print(f"🏷️  Brands: {len(BRANDS)}")

    if args.dry_run:
        print("⚠️  DRY RUN MODE")

    service = GooglePlacesService()
    if not service.api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set")
        return

    db = SessionLocal()

    try:
        # Get existing counts and pre-load place IDs
        existing_shops = db.query(Shop).count()
        print(f"\n📊 Existing shops in database: {existing_shops}")

        # Pre-load existing place IDs to avoid duplicates
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
                brand = type("Brand", (), {"id": 0, "name": brand_data["name"]})()

            count = await import_brand_grid(
                service=service,
                db=db,
                brand=brand,
                grid_points=TAIWAN_GRID,
                session_place_ids=session_place_ids,
                dry_run=args.dry_run,
            )
            total_imported += count

            # Commit after each brand to preserve progress
            if not args.dry_run:
                db.commit()
                print(f"    💾 Committed {brand.name}")

        print("\n" + "=" * 60)
        print(f"✅ Import complete! +{total_imported} new shops")
        print("=" * 60)

        if not args.dry_run:
            new_total = db.query(Shop).count()
            print(
                f"\n📊 Database now contains: {new_total} shops "
                f"(+{new_total - existing_shops})"
            )

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
