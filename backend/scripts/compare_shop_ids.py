#!/usr/bin/env python3
"""
Compare Shop IDs between Dev and Prod databases.
Finds shops where ID differs for the same google_place_id.
"""

import os
import sys

from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to allow importing app.models
# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Shop


def get_db_url(env_file_name: str) -> str:
    """Extract DATABASE_URL from an env file without loading it into os.environ."""
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
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


def get_shop_data(session, label: str):
    print(f"Fetching shops from {label}...")
    # Fetch id and google_place_id where google_place_id is not null
    shops = (
        session.query(Shop.id, Shop.google_place_id)
        .filter(Shop.google_place_id.isnot(None))
        .all()
    )

    # Store as dictionary: google_place_id -> id
    shop_map = {shop.google_place_id: shop.id for shop in shops}
    print(f"   Found {len(shop_map)} shops with google_place_id in {label}.")
    return shop_map


def main():
    # 1. Get URLs
    dev_url = get_db_url(".env")
    prod_url = get_db_url(".env.prod")

    if not dev_url:
        print("❌ Error: Missing DATABASE_URL in .env")
        return
    if not prod_url:
        print("❌ Error: Missing DATABASE_URL in .env.prod")
        return

    # 2. Connect
    dev_engine = create_engine(dev_url)
    prod_engine = create_engine(prod_url)

    DevSession = sessionmaker(bind=dev_engine)
    ProdSession = sessionmaker(bind=prod_engine)

    dev_session = DevSession()
    prod_session = ProdSession()

    try:
        # 3. Fetch Data
        dev_map = get_shop_data(dev_session, "Dev")
        prod_map = get_shop_data(prod_session, "Prod")

        # 4. Compare
        print("\n🔍 Comparing IDs...")
        mismatches = []

        # Iterate through common google_place_ids
        common_ids = set(dev_map.keys()) & set(prod_map.keys())
        dev_set = set()
        prod_set = set()
        for gp_id in common_ids:
            dev_id = dev_map[gp_id]
            prod_id = prod_map[gp_id]

            if dev_id != prod_id:
                mismatches.append(
                    {"google_place_id": gp_id, "dev_id": dev_id, "prod_id": prod_id}
                )
                dev_set.add(dev_id)
                prod_set.add(prod_id)

        # 5. Report
        if not mismatches:
            print(
                "\n✅ All shops with the same google_place_id have matching "
                "internal IDs."
            )
        else:
            if len(mismatches) == len(dev_set & prod_set):
                print("\n⚠️ Found mismatches, but all dev IDs are present in prod.")
            else:
                print("\n❌ Found mismatches with differing IDs between Dev and Prod:")
            # mismatches.sort(key=lambda x: x['dev_id'])
            # print(f"\n⚠️ Found {len(mismatches)} mismatches:")
            # print(f"{'Google Place ID':<30} | {'Dev ID':<8} | {'Prod ID':<8}")
            # print("-" * 52)
            # diff = mismatches[0]['dev_id'] - mismatches[0]['prod_id']
            # for m in mismatches:
            #     if (m['dev_id'] - m['prod_id']) != diff:
            #         diff = m['dev_id'] - m['prod_id']
            #         print(f"{m['google_place_id']:<30} | {m['dev_id']:<8} | "
            #               f"{m['prod_id']:<8}")

        # Also report orphans/exclusives if interesting?
        # User only asked: "I want to see the shop that the id doesn't match in to db."

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
    finally:
        dev_session.close()
        prod_session.close()


if __name__ == "__main__":
    main()
