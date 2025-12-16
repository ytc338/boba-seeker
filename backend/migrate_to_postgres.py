#!/usr/bin/env python3
"""
Migrate data from SQLite to PostgreSQL.

Usage:
    # Set your Render PostgreSQL connection string
    export DATABASE_URL="postgresql://user:password@host:port/boba_seeker"
    
    # Run migration
    python migrate_to_postgres.py
    
    # Or specify SQLite path explicitly
    python migrate_to_postgres.py --sqlite ./data/boba_seeker.db
"""

import argparse
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def get_sqlite_engine(sqlite_path: str):
    """Create SQLite engine."""
    return create_engine(f"sqlite:///{sqlite_path}")


def get_postgres_engine(database_url: str):
    """Create PostgreSQL engine."""
    # Handle Render's postgres:// vs postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return create_engine(database_url)


def migrate_data(sqlite_path: str, postgres_url: str, batch_size: int = 1000):
    """Migrate all data from SQLite to PostgreSQL."""
    
    print(f"📦 Source: {sqlite_path}")
    print(f"🎯 Target: {postgres_url[:50]}...")
    print()
    
    # Create engines
    sqlite_engine = get_sqlite_engine(sqlite_path)
    pg_engine = get_postgres_engine(postgres_url)
    
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PgSession = sessionmaker(bind=pg_engine)
    
    sqlite_session = SqliteSession()
    pg_session = PgSession()
    
    try:
        # Create tables in PostgreSQL (import models to register them)
        from app.models import Brand, Shop
        from app.database import Base
        
        print("🔨 Creating tables in PostgreSQL...")
        Base.metadata.create_all(bind=pg_engine)
        
        # Migrate brands first (foreign key dependency)
        print("\n📋 Migrating brands...")
        brands = sqlite_session.execute(text("SELECT * FROM brands")).fetchall()
        brand_columns = sqlite_session.execute(text("PRAGMA table_info(brands)")).fetchall()
        brand_col_names = [col[1] for col in brand_columns]
        
        if brands:
            for brand_row in brands:
                brand_dict = dict(zip(brand_col_names, brand_row))
                
                # Check if brand already exists
                existing = pg_session.execute(
                    text("SELECT id FROM brands WHERE id = :id"),
                    {"id": brand_dict["id"]}
                ).fetchone()
                
                if not existing:
                    columns = ", ".join(brand_dict.keys())
                    placeholders = ", ".join([f":{k}" for k in brand_dict.keys()])
                    pg_session.execute(
                        text(f"INSERT INTO brands ({columns}) VALUES ({placeholders})"),
                        brand_dict
                    )
            
            pg_session.commit()
            print(f"   ✅ Migrated {len(brands)} brands")
        else:
            print("   ⚠️  No brands found")
        
        # Migrate shops in batches
        print("\n📋 Migrating shops...")
        total_shops = sqlite_session.execute(text("SELECT COUNT(*) FROM shops")).scalar()
        print(f"   Found {total_shops} shops to migrate")
        
        shop_columns = sqlite_session.execute(text("PRAGMA table_info(shops)")).fetchall()
        shop_col_names = [col[1] for col in shop_columns]
        
        migrated = 0
        skipped = 0
        offset = 0
        
        while offset < total_shops:
            shops = sqlite_session.execute(
                text(f"SELECT * FROM shops LIMIT {batch_size} OFFSET {offset}")
            ).fetchall()
            
            for shop_row in shops:
                shop_dict = dict(zip(shop_col_names, shop_row))
                
                try:
                    # Check if shop already exists (by google_place_id or id)
                    existing = None
                    if shop_dict.get("google_place_id"):
                        existing = pg_session.execute(
                            text("SELECT id FROM shops WHERE google_place_id = :gid"),
                            {"gid": shop_dict["google_place_id"]}
                        ).fetchone()
                    
                    if not existing:
                        existing = pg_session.execute(
                            text("SELECT id FROM shops WHERE id = :id"),
                            {"id": shop_dict["id"]}
                        ).fetchone()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Handle datetime fields
                    for dt_field in ["last_verified", "created_at", "updated_at"]:
                        if dt_field in shop_dict and shop_dict[dt_field]:
                            if isinstance(shop_dict[dt_field], str):
                                try:
                                    shop_dict[dt_field] = datetime.fromisoformat(
                                        shop_dict[dt_field].replace("Z", "+00:00")
                                    )
                                except:
                                    shop_dict[dt_field] = datetime.utcnow()
                    
                    columns = ", ".join(shop_dict.keys())
                    placeholders = ", ".join([f":{k}" for k in shop_dict.keys()])
                    
                    pg_session.execute(
                        text(f"INSERT INTO shops ({columns}) VALUES ({placeholders})"),
                        shop_dict
                    )
                    pg_session.commit()  # Commit each successful insert
                    migrated += 1
                    
                except Exception as e:
                    pg_session.rollback()  # Rollback failed insert
                    print(f"   ⚠️  Error migrating shop {shop_dict.get('name', 'unknown')}: {e}")
                    skipped += 1
            
            offset += batch_size
            print(f"   Progress: {min(offset, total_shops)}/{total_shops} (migrated: {migrated}, skipped: {skipped})")
        
        # Update PostgreSQL sequences to avoid ID conflicts
        print("\n🔧 Updating ID sequences...")
        pg_session.execute(text("""
            SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id) FROM brands), 1), true)
        """))
        pg_session.execute(text("""
            SELECT setval('shops_id_seq', COALESCE((SELECT MAX(id) FROM shops), 1), true)
        """))
        pg_session.commit()
        
        print(f"\n✅ Migration complete!")
        print(f"   Brands: {len(brands)}")
        print(f"   Shops migrated: {migrated}")
        print(f"   Shops skipped (duplicates): {skipped}")
        
    except Exception as e:
        pg_session.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        sqlite_session.close()
        pg_session.close()


def main():
    parser = argparse.ArgumentParser(description="Migrate SQLite data to PostgreSQL")
    parser.add_argument(
        "--sqlite",
        default="./boba_seeker.db",
        help="Path to SQLite database (default: ./boba_seeker.db)"
    )
    parser.add_argument(
        "--postgres",
        default=os.environ.get("DATABASE_URL"),
        help="PostgreSQL connection URL (default: DATABASE_URL env var)"
    )
    
    args = parser.parse_args()
    
    if not args.postgres:
        print("❌ Error: PostgreSQL URL required.")
        print("   Set DATABASE_URL environment variable or use --postgres flag")
        print()
        print("   Example:")
        print('   export DATABASE_URL="postgresql://user:pass@host:5432/boba_seeker"')
        print("   python migrate_to_postgres.py")
        sys.exit(1)
    
    if not os.path.exists(args.sqlite):
        print(f"❌ Error: SQLite database not found: {args.sqlite}")
        sys.exit(1)
    
    migrate_data(args.sqlite, args.postgres)


if __name__ == "__main__":
    main()
