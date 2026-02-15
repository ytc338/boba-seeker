import os
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from app.services.brand_matcher import calculate_match_score, normalize_name

# Load env
# Use CWD for .env
load_dotenv(os.path.join(os.getcwd(), ".env"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import from centralized service


def find_potential_brands():
    database_url = os.getenv("DATABASE_URL")
    print(f"DEBUG: DATABASE_URL IS: {database_url}")
    if not database_url:
        print("DATABASE_URL not found")
        return

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("--- Fetching Unbranded Shops ---")
        query = text("SELECT name FROM shops WHERE brand_id IS NULL")
        result = conn.execute(query).fetchall()
        shop_names = [row.name for row in result]

    print(f"Analyzing {len(shop_names)} unbranded shop names...")

    # Clustering Logic
    # clusters = [ {'name': 'Representative Name', 'members': ['var1', 'var2']} ]
    clusters = []

    # We want to ignore very generic matches, but rapidfuzz handles a lot.
    # We might want to pre-clean names (remove city names if possible),
    # but let's start simple.

    for name in shop_names:
        # Simple normalization for the loop
        name_clean = normalize_name(name)
        if not name_clean:
            continue

        matched = False
        for cluster in clusters:
            # Check against representative
            # token_set_ratio is good for subset matches:
            # "Gong Cha" vs "Gong Cha SJ" -> 100
            score = calculate_match_score(cluster["name"], name)

            if score >= 85:  # Threshold
                cluster["members"].append(name)
                matched = True
                break

        if not matched:
            clusters.append({"name": name, "members": [name]})

    # Sort by size
    clusters.sort(key=lambda x: len(x["members"]), reverse=True)

    print("\n--- Potential Brand Clusters (Size >= 3) ---")
    for c in clusters:
        if len(c["members"]) >= 3:
            print(f"\nCluster: {c['name']} (Count: {len(c['members'])})")
            # Show top 5 interactions to avoid spam
            unique_variations = list(set(c["members"]))
            for v in unique_variations[:5]:
                print(f"  - {v}")
            if len(unique_variations) > 5:
                print(f"  ... + {len(unique_variations) - 5} more")


if __name__ == "__main__":
    find_potential_brands()
