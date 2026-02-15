import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.brand_matcher import match_brand_from_name


# Mock Brand class since import_us_v2 imports it from app.models
class MockBrand:
    def __init__(self, id, name, name_zh=None):
        self.id = id
        self.name = name
        self.name_zh = name_zh
        # Add other fields if necessary, but fuzzy_match matches on name/name_zh


def test_specific_match():
    # Brand 43
    boba_guys = MockBrand(43, "Boba Guys", "Boba Guys")
    brands = [boba_guys]

    # Shop 5033 name
    shop_name = "The Berry’s Boba Matcha"

    print(f"Testing Shop: '{shop_name}' vs Brand: '{boba_guys.name}'")

    # Match returns confidence only in the service version (it returns float)
    # The script previously expected (matched_brand, confidence) from find_best_brand_match/fuzzy_match_brand
    # But wait, fuzzy_match_brand usually returns (brand_obj, confidence).
    # match_brand_from_name returns float confidence.

    confidence = match_brand_from_name(shop_name, boba_guys.name, boba_guys.name_zh)
    matched_brand = boba_guys if confidence > 0.8 else None

    if matched_brand:
        print(f"✅ MATCH FOUND! Confidence: {confidence}")
        print(f"Matched Brand: {matched_brand.name}")
    else:
        print("❌ NO MATCH")

    # Let's debug WHY by manually running the logic steps
    print("\n--- Manual Debug ---")
    shop_lower = shop_name.lower()
    brand_lower = boba_guys.name.lower()
    GENERIC_WORDS = {
        "boba",
        "tea",
        "bubble",
        "milk",
        "the",
        "cafe",
        "house",
        "bar",
        "shop",
    }

    print(
        f"1. Exact match '{brand_lower}' in '{shop_lower}'? {brand_lower in shop_lower}"
    )

    brand_words = [w for w in brand_lower.split() if w not in GENERIC_WORDS]
    print(f"2. Brand words (non-generic): {brand_words}")

    if len(brand_words) >= 2:
        match_2 = all(word in shop_lower for word in brand_words[:2])
        print(f"3. Two+ words match? {match_2}")

    elif len(brand_words) == 1:
        print(f"3. Single word length: {len(brand_words[0])}")
        match_1 = brand_words[0] in shop_lower
        print(f"4. Single word match? {match_1}")


if __name__ == "__main__":
    test_specific_match()
