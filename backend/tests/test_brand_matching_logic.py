import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock objects
class MockBrand:
    def __init__(self, name, name_zh=None):
        self.name = name
        self.name_zh = name_zh
        self.aliases = []

# Import logic from service
from app.services.brand_matcher import match_brand_from_name, BRAND_ALIASES

def test_matching_logic():
    
    test_cases = [
        ("Boba Guys", True),
        ("The Boba Guys", True),
        ("Boby Guys", True), # Fuzzy match tolerance
        ("Baby Guys", False), # Too different? Depends on fuzzy logic
        ("Boba Guys - Union Square", True),
        ("Boby Guys Tea", False),
        ("Guys Boba", True),
        ("Generic Guys", False)
    ]
    
    print("\n--- Testing app.services.brand_matcher.match_brand_from_name ---")
    for name, expected in test_cases:
        # Service takes (shop_name, brand_name, brand_name_zh, aliases)
        # We simulate checking against "Boba Guys"
        confidence = match_brand_from_name(name, "Boba Guys", "Boba Guys")
        
        # We consider a match if confidence > 0.8
        is_match = confidence > 0.8
        
        if expected:
             assert is_match, f"Expected match for {name}, got conf {confidence}"

    print("\n--- Testing Aliases via Service ---")
    print(f"Aliases for Boba Guys: {BRAND_ALIASES.get('Boba Guys')}")

