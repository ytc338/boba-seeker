import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env and add path
# Load env and add path
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FIXED verification logic
from app.services.brand_matcher import match_brand_from_name

def fix_bad_mappings(dry_run=True):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return
    
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        print("--- Loading Data ---")
        # Get all active brands
        brands_query = text("SELECT id, name, name_zh, origin_country FROM brands")
        brands = conn.execute(brands_query).fetchall()
        
        # Convert to dict lookup
        brand_map = {} 
        for b in brands:
            brand_map[b.id] = {
                "name": b.name,
                "name_zh": b.name_zh,
                # Aliases will be looked up by brand_matcher if we don't provide them
                # or we can leave it empty if we want strict DB only logic? 
                # No, we want to respect aliases during validation.
            }

        # Get all Shops WITH a brand_id
        shops_query = text("SELECT id, name, brand_id FROM shops WHERE brand_id IS NOT NULL")
        shops = conn.execute(shops_query).fetchall()
        print(f"Scanning {len(shops)} matched shops against NEW strict logic...")
        
        # Buffer for invalid shops: key = brand_name, value = list of shops
        # Using a dict of lists to group them
        invalid_groups = {}
        
        for shop in shops:
            current_brand = brand_map.get(shop.brand_id)
            if not current_brand:
                continue 
            
            # Re-run match logic
            conf = match_brand_from_name(
                shop.name, 
                current_brand["name"], 
                current_brand["name_zh"]
            )
            
            # If confidence is low, it's a BAD mapping
            if conf < 0.9:
                brand_name = current_brand["name"]
                if brand_name not in invalid_groups:
                    invalid_groups[brand_name] = []
                invalid_groups[brand_name].append(shop)
        
        total_invalid = sum(len(l) for l in invalid_groups.values())
        print(f"\nFound {total_invalid} invalid mappings across {len(invalid_groups)} brands.")
        
        if total_invalid == 0:
            print("✅ Data is clean!")
            return

        if dry_run:
            print("\n[DRY RUN PREVIEW]")
            for brand_name, bad_shops in invalid_groups.items():
                print(f"  • {brand_name}: {len(bad_shops)} invalid matches")
            print("\nRun with 'python backend/fix_bad_mappings.py' (without dry run arg if using script manually) to clean up.")
            return

        # Interactive Cleanup
        total_fixed = 0
        
        for brand_name, bad_shops in invalid_groups.items():
            print(f"\n{'='*50}")
            print(f"BRAND: {brand_name}")
            print(f"⚠️  {len(bad_shops)} invalid matches found.")
            print(f"{'='*50}")
            
            # Show samples
            print("Samples of shops to be UNLINKED:")
            for s in bad_shops[:10]:
                print(f"  • {s.name}")
            if len(bad_shops) > 10:
                print(f"  ... and {len(bad_shops)-10} more")
            
            print(f"\nOptions:")
            print(f"  [y] Unlink ALL {len(bad_shops)} shops for {brand_name}")
            print(f"  [n] Skip this brand")
            print(f"  [i] Inspect one by one (Individual mode)")
            
            while True:
                choice = input("Choice: ").strip().lower()
                
                if choice == 'y':
                    # Batch delete
                    ids = tuple(s.id for s in bad_shops)
                    conn.execute(
                        text("UPDATE shops SET brand_id = NULL, updated_at = :now WHERE id IN :ids"), 
                        {"now": datetime.now(timezone.utc), "ids": ids}
                    )
                    total_fixed += len(ids)
                    print(f"  ✅ Unlinked {len(ids)} shops.")
                    break
                    
                elif choice == 'n':
                    print("  ⏭️  Skipped.")
                    break
                    
                elif choice == 'i':
                    print("\n  ENTERING INDIVIDUAL REVIEW:")
                    count = 0
                    for s in bad_shops:
                        sub = input(f"    Unlink '{s.name}'? [y/n]: ").lower()
                        if sub == 'y':
                            conn.execute(
                                text("UPDATE shops SET brand_id = NULL, updated_at = :now WHERE id = :id"), 
                                {"now": datetime.now(timezone.utc), "id": s.id}
                            )
                            count += 1
                    total_fixed += count
                    print(f"  ✅ Finished review. Unlinked {count} shops.")
                    break
                
        conn.commit()
        print(f"\n{'-'*50}")
        print(f"🎉 CLEANUP COMPLETE! Total unlinked: {total_fixed}")
        print(f"{'-'*50}")

if __name__ == "__main__":
    # Always interactive unless flag passed? Let's just default to interactive given the use case.
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show preview only")
    args = parser.parse_args()
    
    fix_bad_mappings(dry_run=args.dry_run)
