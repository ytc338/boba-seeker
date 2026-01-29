#!/usr/bin/env python3
"""
Sync Dev Shop IDs to match Prod Shop IDs for the same google_place_id.
Handles potential primary key conflicts by using a temporary ID space.
"""

import sys
import os
import argparse
from typing import Dict, List, Set, Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values

# Add parent directory to path
# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import Shop

def get_db_url(env_file_name: str) -> str:
    """Extract DATABASE_URL from an env file without loading it into os.environ."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def get_shop_map(session) -> Dict[str, int]:
    """Returns {google_place_id: id}."""
    shops = session.query(Shop.id, Shop.google_place_id).filter(Shop.google_place_id.isnot(None)).all()
    return {shop.google_place_id: shop.id for shop in shops}

def main():
    parser = argparse.ArgumentParser(description="Sync Dev Shop IDs to match Prod")
    parser.add_argument("--dry-run", action="store_true", help="Calculate mismatches but do not commit changes")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()

    # 1. Connect
    dev_url = get_db_url(".env")
    prod_url = get_db_url(".env.prod")

    if not dev_url or not prod_url:
        print("❌ Error: Missing DATABASE_URL")
        sys.exit(1)

    print(f"Dev:  {dev_url.split('@')[-1]}")
    print(f"Prod: {prod_url.split('@')[-1]}")

    dev_engine = create_engine(dev_url)
    prod_engine = create_engine(prod_url)
    
    DevSession = sessionmaker(bind=dev_engine)
    ProdSession = sessionmaker(bind=prod_engine)
    
    dev_session = DevSession()
    prod_session = ProdSession()

    try:
        # 2. Get Data
        print("Matching shops by google_place_id...")
        dev_map = get_shop_map(dev_session)
        prod_map = get_shop_map(prod_session)

        # 3. Identify mismatching updates
        # List of (google_place_id, current_dev_id, target_prod_id)
        updates: List[Tuple[str, int, int]] = []
        
        # Identify IDs in Dev that are "staying" (to check conflicts)
        # We only really care about where we are GOING.
        
        common_gpids = set(dev_map.keys()) & set(prod_map.keys())
        
        for gpid in common_gpids:
            dev_id = dev_map[gpid]
            prod_id = prod_map[gpid]
            
            if dev_id != prod_id:
                updates.append((gpid, dev_id, prod_id))
        
        if not updates:
            print("✅ No ID mismatches found. Dev and Prod are in sync.")
            return

        print(f"⚠️ Found {len(updates)} shops needing ID update.")
        
        # 4. Confirmation
        if args.dry_run:
            print("\n[Dry Run] Would execute the following:")
            for gpid, old, new in updates[:10]:
                print(f"   - Shop {gpid}: {old} -> {new}")
            if len(updates) > 10: print(f"   ... and {len(updates)-10} more.")
            return

        if not args.force:
            confirm = input("\n⚠️ This will modify IDs in the DEV database. Are you sure? [y/N] ")
            if confirm.lower() != 'y':
                print("Aborted.")
                sys.exit(0)

        # 5. Execute Updates Correctly
        # We cannot just do UPDATE shops SET id=new WHERE id=old because 'new' might be occupied by another shop 
        # that hasn't moved yet.
        # Strategy:
        # 1. Shift ALL affected shops to a temporary Safe Zone (e.g. negative IDs).
        # 2. Shift from Safe Zone to Target IDs.
        
        print("\n🚀 Starting update transaction...")
        
        # 5.1. Move to Temporary Negative IDs
        # Mappings: old_id -> temp_id -> new_id
        temp_map = {} # old_id -> temp_id
        final_map = {} # temp_id -> new_id
        
        # We need a safely unused range. Negative IDs are usually safe in integer PKs if not used.
        # Let's verify no negative IDs exist.
        min_id = dev_session.execute(text("SELECT MIN(id) FROM shops")).scalar() or 0
        start_temp = -1
        if min_id < 0:
             # potentially unsafe if they use negatives, start lower
             start_temp = min_id - 100000

        current_temp = start_temp
        
        # Collect all dev_ids involved in this dance
        # Note: We must move matched shops.
        # Check: Is the *target* ID occupied by a shop that *isn't* in our update list?
        # If so, we have a problem (collision with a shop that isn't moving).
        # In this specific context (syncing completely), presumably we want to sync these.
        # But if there is a Shop C in Dev with ID=100 (and different google_place_id, or no match),
        # and we want to move Shop A to ID=100, we will fail unless we move Shop C too.
        
        # Check for collisions with non-moving shops
        target_ids = {u[2] for u in updates}
        occupied_ids = set(dev_session.query(Shop.id).all()) # List of tuples, really separate needed
        occupied_ids = {r[0] for r in dev_session.query(Shop.id).all()}
        
        moving_source_ids = {u[1] for u in updates}
        
        # Collision = (Target ID is in Occupied) AND (Target ID is NOT in Moving Source IDs)
        # If Target ID is in Moving Source IDs, it will move out of the way (step 1), so it's safe.
        # If Target ID is NOT matching any gpid we are syncing, it stays put -> Collision.
        
        collisions = target_ids.intersection(occupied_ids) - moving_source_ids
        
        if collisions:
            print(f"❌ CRITICAL ERROR: {len(collisions)} target IDs are occupied by shops that are NOT part of the sync map.")
            print(f"   Example collisions: {list(collisions)[:5]}")
            print("   This script only swaps IDs for known Google Place ID matches.")
            print("   If you proceed, these existing shops will block the update.")
            print("   Aborting to prevent integrity errors.")
            sys.exit(1)

        # Apply Step 1: Move to Temp
        print("   Step 1: Moving to temporary IDs...")
        for i, (gpid, old_id, new_id) in enumerate(updates):
            temp_id = current_temp - i
            temp_map[old_id] = temp_id
            final_map[temp_id] = new_id
            
            # Update specific row
            # We use text SQL for speed/directness or ORM.
            # ORM might be tricky with PK updates in session.
            # Let's use direct SQL for bulk logic.
            dev_session.execute(
                text("UPDATE shops SET id = :temp_id WHERE id = :old_id"),
                {"temp_id": temp_id, "old_id": old_id}
            )
            
        dev_session.flush()
        
        # Apply Step 2: Move to Final
        print("   Step 2: Moving to final IDs...")
        for temp_id, new_id in final_map.items():
            dev_session.execute(
                text("UPDATE shops SET id = :new_id WHERE id = :temp_id"),
                {"new_id": new_id, "temp_id": temp_id}
            )
            
        # 6. Update Sequence
        print("   Step 3: Updating sequence...")
        dev_session.execute(text("SELECT setval('shops_id_seq', (SELECT MAX(id) FROM shops))"))
        
        dev_session.commit()
        print(f"✅ Successfully updated {len(updates)} shop IDs.")
        
    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        dev_session.rollback()
        
    finally:
        dev_session.close()
        prod_session.close()

if __name__ == "__main__":
    main()
