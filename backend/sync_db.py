#!/usr/bin/env python3
"""
Smart Sync from Source DB (.env) to Target DB (.env.prod).

Features:
1.  **Brand Sync**: Matches by `name`. Maps Source IDs to Target IDs correctly, handling mismatched sequences.
2.  **Shop Sync**: Matches by `google_place_id`. Uses the ID map to rewrite `brand_id` references before upserting.
3.  **Conflict Resolution**: Uses `google_place_id` for Shops and `name` for Brands as the "Real" keys.
4.  **Preserves Target IDs**: Does not overwrite the Primary Key (`id`) of existing rows in Target.

Usage:
    python backend/sync_db.py [--dry-run]
"""

import sys
import os
import argparse
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import dotenv_values
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Import models to ensure they are registered
from app.models import Brand, Shop, Base


def get_db_url(env_file_name: str) -> str:
    """Extract DATABASE_URL from an env file without loading it into os.environ."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, env_file_name)

    if not os.path.exists(env_path):
        print(f"⚠️ Warning: Env file not found at {env_path}")
        return None

    config = dotenv_values(env_path)
    url = config.get("DATABASE_URL")

    if not url:
        return None

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url


def sync_brands(source_session, target_session, dry_run=False) -> Dict[int, int]:
    """
    Sync Brands by NAME.
    Returns a map of {Source_Brand_ID: Target_Brand_ID}.
    """
    print("\n📦 Syncing Table: Brands (Match by Name)")

    source_brands = source_session.query(Brand).all()
    if not source_brands:
        print("   No brands in source.")
        return {}

    # columns to sync (exclude id)
    columns = [c.name for c in Brand.__table__.columns if c.name != "id"]

    # Batch upsert
    data_to_insert = []
    for b in source_brands:
        row = {col: getattr(b, col) for col in columns}
        data_to_insert.append(row)

    if dry_run:
        print(f"   [Dry Run] Would upsert {len(data_to_insert)} brands.")
        # Return dummy map for dry run
        return {b.id: b.id for b in source_brands}

    # Perform Upsert
    stmt = pg_insert(Brand).values(data_to_insert)

    # Update all columns except name (key) and id (pk)
    update_dict = {col: stmt.excluded[col] for col in columns if col != "name"}

    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=["name"],  # Match on Name
        set_=update_dict,
    )

    target_session.execute(upsert_stmt)
    target_session.commit()
    print(f"   ✅ Synced {len(data_to_insert)} brands.")

    # Re-build ID map
    print("   🔄 Building ID Map (Source -> Target)...")
    target_brands = target_session.query(Brand).all()

    # Map: Name -> TargetID
    target_map = {b.name: b.id for b in target_brands}

    # Map: SourceID -> TargetID
    id_map = {}
    for b in source_brands:
        if b.name in target_map:
            id_map[b.id] = target_map[b.name]

    return id_map


def sync_shops(
    source_session, target_session, brand_id_map: Dict[int, int], dry_run=False
):
    """
    Sync Shops by GOOGLE_PLACE_ID.
    Rewrite brand_id using the provided map.
    """
    print("\n📦 Syncing Table: Shops (Match by Google Place ID)")

    # Only sync shops that have a google_place_id (our logic relies on it)
    query = source_session.query(Shop).filter(Shop.google_place_id.isnot(None))
    total_rows = query.count()
    print(f"   Source has {total_rows} matchable shops.")

    if total_rows == 0:
        return

    # columns to sync (exclude id)
    columns = [c.name for c in Shop.__table__.columns if c.name != "id"]

    batch_size = 1000
    processed = 0

    for offset in range(0, total_rows, batch_size):
        batch = query.offset(offset).limit(batch_size).all()
        data_to_insert = []

        for obj in batch:
            row = {col: getattr(obj, col) for col in columns}

            # Key Step: TRANSLATE BRAND ID
            if row.get("brand_id"):
                if row["brand_id"] in brand_id_map:
                    row["brand_id"] = brand_id_map[row["brand_id"]]
                else:
                    # Brand exists in Source but somehow missing in Target/Map?
                    # Should set to None or Skip?
                    # If sync_brands ran, it should be there.
                    # Fallback to None to avoid FK constraint error
                    row["brand_id"] = None

            data_to_insert.append(row)

        if not data_to_insert:
            break

        if dry_run:
            print(f"   [Dry Run] Would upsert batch of {len(data_to_insert)} shops.")
            processed += len(data_to_insert)
            continue

        # Perform Upsert
        stmt = pg_insert(Shop).values(data_to_insert)

        # Update all columns except google_place_id (key) and id (pk)
        update_dict = {
            col: stmt.excluded[col] for col in columns if col != "google_place_id"
        }

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=["google_place_id"], set_=update_dict
        )

        target_session.execute(upsert_stmt)
        target_session.commit()

        processed += len(data_to_insert)
        print(f"   Progress: {processed}/{total_rows}")


def update_sequences(target_session):
    """Update PostgreSQL sequences to match the highest ID."""
    print("\n🔧 Updating sequences...")
    tables = ["brands", "shops"]

    for table in tables:
        try:
            target_session.execute(
                text(
                    f"SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 1), true)"
                )
            )
            print(f"   Updated sequence for {table}")
        except Exception as e:
            print(f"   ⚠️ Could not update sequence for {table}: {e}")
            target_session.rollback()

    target_session.commit()


def main():
    parser = argparse.ArgumentParser(description="Smart Sync from Source to Target DB")
    parser.add_argument("--dry-run", action="store_true", help="Simulate sync")
    parser.add_argument("--force", action="store_true", help="Bypass confirmation")

    args = parser.parse_args()

    # 1. Load Configs
    source_url = get_db_url(".env")
    target_url = get_db_url(".env.prod")

    if not source_url or not target_url:
        print("❌ Error: Missing DATABASE_URL in .env or .env.prod")
        sys.exit(1)

    print(f"Source: {source_url.split('://')[1]}://... (Development)")
    print(f"Target: {target_url.split('://')[1]}://... (Production)")

    if args.dry_run:
        print("\n🚧 DRY RUN MODE")
    elif not args.force:
        confirm = input("\nAre you sure you want to sync to Target? [y/N] ")
        if confirm.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    # 2. Connect
    source_engine = create_engine(source_url)
    target_engine = create_engine(target_url)

    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)

    source_session = SourceSession()
    target_session = TargetSession()

    try:
        # 3. Sync Brands & Get Map
        id_map = sync_brands(source_session, target_session, dry_run=args.dry_run)

        # 4. Sync Shops
        sync_shops(source_session, target_session, id_map, dry_run=args.dry_run)

        # 5. Sequences
        if not args.dry_run:
            update_sequences(target_session)

        print("\n✅ Sync complete!")

    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        target_session.rollback()
        raise
    finally:
        source_session.close()
        target_session.close()


if __name__ == "__main__":
    main()
