#!/usr/bin/env python3
"""
One-way sync from Source DB (.env) to Target DB (.env.prod).

Efficiency:
    This script uses PostgreSQL's `INSERT ... ON CONFLICT DO UPDATE` (Upsert).
    This is efficient because:
    1. It minimizes network round-trips by sending data in batches rather than row-by-row.
    2. It avoids the need to pre-query the database to check for existence (SELECT then INSERT/UPDATE).
    3. The database engine handles the conflict resolution internally using indexes (B-Trees), which is much faster than application-level logic.
    4. By only updating when data actually changes (optional optimization) or blindly updating, it ensures consistency with a single atomic operation per batch.

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
    # Assume script is in backend/sync_db.py, so project root is ../
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, env_file_name)
    
    if not os.path.exists(env_path):
        print(f"⚠️ Warning: Env file not found at {env_path}")
        return None
        
    config = dotenv_values(env_path)
    url = config.get("DATABASE_URL")
    
    if not url:
        return None
    
    # Fix Render's postgres:// if needed
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
        
    return url

def sync_table(source_session, target_session, model, batch_size=1000, dry_run=False):
    """Sync a single table from source to target using Upsert."""
    table_name = model.__tablename__
    print(f"\n📦 Syncing table: {table_name}")
    
    # Get columns
    columns = [c.name for c in model.__table__.columns]
    
    # Identify Primary Key for conflict resolution
    pk_columns = [c.name for c in model.__table__.primary_key.columns]
    
    # Count source rows
    total_rows = source_session.query(model).count()
    print(f"   Source has {total_rows} rows.")
    
    if total_rows == 0:
        return

    processed = 0
    query = source_session.query(model)
    
    # Fetch in batches
    for offset in range(0, total_rows, batch_size):
        batch = query.offset(offset).limit(batch_size).all()
        data_to_insert = []
        
        for obj in batch:
            # Convert object to dict
            row_data = {col: getattr(obj, col) for col in columns}
            data_to_insert.append(row_data)
        
        if not data_to_insert:
            break
            
        if dry_run:
            print(f"   [Dry Run] Would upsert batch of {len(data_to_insert)} records.")
            processed += len(data_to_insert)
            continue
            
        # Construct Upsert Statement
        stmt = pg_insert(model).values(data_to_insert)
        
        # Create update dict: update all columns except PKs
        update_dict = {col: stmt.excluded[col] for col in columns if col not in pk_columns}
        
        # Add timestamp if it exists and isn't being explicitly updated differently (optional)
        # But here we want to sync exactly what is in source, so we stick to the source values.
        
        # Perform Upsert
        # ON CONFLICT (pk) DO UPDATE SET ...
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=pk_columns,
            set_=update_dict
        )
        
        target_session.execute(upsert_stmt)
        target_session.commit()
        
        processed += len(data_to_insert)
        print(f"   Progress: {processed}/{total_rows}")

def update_sequences(target_session):
    """Update PostgreSQL sequences to match the highest ID."""
    print("\n🔧 Updating sequences...")
    # List of tables to update sequences for
    tables = ['brands', 'shops']
    
    for table in tables:
        try:
            target_session.execute(text(f"SELECT setval('{table}_id_seq', COALESCE((SELECT MAX(id) FROM {table}), 1), true)"))
            print(f"   Updated sequence for {table}")
        except Exception as e:
            print(f"   ⚠️ Could not update sequence for {table}: {e}")
            target_session.rollback()
    
    target_session.commit()

def main():
    parser = argparse.ArgumentParser(description="Sync DB from .env (Source) to .env.prod (Target)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate sync without making changes")
    parser.add_argument("--force", action="store_true", help="Bypass confirmation prompt")
    
    args = parser.parse_args()
    
    # 1. Load Configs
    source_url = get_db_url(".env")
    target_url = get_db_url(".env.prod")
    
    if not source_url:
        print("❌ Error: Could not find DATABASE_URL in .env")
        sys.exit(1)
    if not target_url:
        print("❌ Error: Could not find DATABASE_URL in .env.prod")
        sys.exit(1)
        
    print(f"Source: {source_url.split('://')[1]}://... (from .env)")
    print(f"Target: {target_url.split('://')[1]}://... (from .env.prod)")
    
    if args.dry_run:
        print("\n🚧 DRY RUN MODE: No changes will be committed.")
    elif not args.force:
        confirm = input("\nAre you sure you want to overwrite/sync to Target? [y/N] ")
        if confirm.lower() != 'y':
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
        # 3. Sync Tables
        # Order matters due to Foreign Keys: Brand first, then Shop
        sync_table(source_session, target_session, Brand, dry_run=args.dry_run)
        sync_table(source_session, target_session, Shop, dry_run=args.dry_run)
        
        # 4. Update Sequences (Only if real run)
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
