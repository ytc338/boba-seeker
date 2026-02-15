import os
import sys
import uuid
import argparse
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from rapidfuzz import fuzz, utils

# Load env
# Load env
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
load_dotenv(env_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def create_brand_and_link(conn, brand_name, shop_ids):
    """Creates a brand and links shops to it."""
    # 1. Create Brand
    brand_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    print(f"Creating Brand: {brand_name} ({brand_id})")
    conn.execute(
        text(
            "INSERT INTO brands (id, name, created_at, updated_at) VALUES (:id, :name, :now, :now)"
        ),
        {"id": brand_id, "name": brand_name, "now": now},
    )

    # 2. Link Shops
    if not shop_ids:
        print("No shops to link.")
        return

    print(f"Linking {len(shop_ids)} shops...")
    conn.execute(
        text(
            "UPDATE shops SET brand_id = :brand_id, updated_at = :now WHERE id IN :ids"
        ),
        {"brand_id": brand_id, "now": now, "ids": tuple(shop_ids)},
    )
    print("✅ Done.")


def interactive_brand_creator(min_size=3):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found")
        return

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(database_url)

    with engine.connect() as conn:
        print("--- Fetching Unbranded Shops ---")
        query = text("SELECT id, name, address FROM shops WHERE brand_id IS NULL")
        result = conn.execute(query).fetchall()
        # Store as dict for easy access
        shops = [
            {"id": row.id, "name": row.name, "address": row.address} for row in result
        ]

    print(f"Analyzing {len(shops)} unbranded shops...")

    # --- Clustering Logic (Same as before but keeping IDs) ---
    clusters = []

    for shop in shops:
        name_clean = utils.default_process(shop["name"])
        if not name_clean:
            continue

        matched = False
        for cluster in clusters:
            score = fuzz.token_set_ratio(cluster["name"], shop["name"])
            if score >= 85:
                cluster["members"].append(shop)
                matched = True
                break

        if not matched:
            clusters.append(
                {
                    "name": shop["name"],  # Use first found as representative
                    "members": [shop],
                }
            )

    # Sort by size
    clusters.sort(key=lambda x: len(x["members"]), reverse=True)

    # --- Interactive Review ---
    print(f"\nFound {len(clusters)} potential clusters.")

    with engine.begin() as conn:  # Transaction block
        for i, cluster in enumerate(clusters):
            if len(cluster["members"]) < min_size:
                continue

            print(f"\n{'=' * 60}")
            print(f"Cluster {i + 1} / {len(clusters)}")
            print(f"Suggested Brand Name: {cluster['name']}")
            print(f"Count: {len(cluster['members'])}")
            print(f"{'-' * 60}")

            for idx, member in enumerate(cluster["members"]):
                print(f"  [{idx + 1}] {member['name']} ({member['address']})")

            print(f"{'-' * 60}")
            print("Options:")
            print("  [y] Yes, create brand link ALL")
            print("  [e] Edit name then create")
            print("  [s] Select specific shops to link")
            print("  [n] No / Skip")
            print("  [q] Quit")

            choice = input("Choice: ").strip().lower()

            if choice == "q":
                break
            elif choice == "n":
                continue
            elif choice == "y":
                shop_ids = [m["id"] for m in cluster["members"]]
                create_brand_and_link(conn, cluster["name"], shop_ids)
            elif choice == "e":
                new_name = input(
                    f"Enter new brand name (default: {cluster['name']}): "
                ).strip()
                final_name = new_name if new_name else cluster["name"]
                shop_ids = [m["id"] for m in cluster["members"]]
                create_brand_and_link(conn, final_name, shop_ids)
            elif choice == "s":
                print(
                    "Enter numbers of shops to INCLUDE (comma separated, e.g. 1,3,5):"
                )
                selection = input("> ").strip()
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(",")]
                    selected_shops = [
                        cluster["members"][idx]
                        for idx in indices
                        if 0 <= idx < len(cluster["members"])
                    ]

                    if not selected_shops:
                        print("No valid shops selected. Skipping.")
                        continue

                    # Ask for name again just in case
                    new_name = input(
                        f"Enter brand name for these {len(selected_shops)} shops (default: {cluster['name']}): "
                    ).strip()
                    final_name = new_name if new_name else cluster["name"]

                    shop_ids = [s["id"] for s in selected_shops]
                    create_brand_and_link(conn, final_name, shop_ids)
                except ValueError:
                    print("Invalid input. Skipping.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--min-size", type=int, default=3, help="Minimum cluster size to show"
    )
    args = parser.parse_args()

    interactive_brand_creator(min_size=args.min_size)
