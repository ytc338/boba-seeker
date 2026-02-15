"""
Brand Matched Service
Centralizes brand matching logic and aliases for various import scripts.
"""

from rapidfuzz import fuzz, utils

# ============================================================
# BRAND CONFIGURAITON & ALIASES
# ============================================================

# Generic words that should not trigger a match on their own
GENERIC_WORDS = {
    "boba",
    "tea",
    "bubble",
    "milk",
    "the",
    "cafe",
    "coffee",
    "house",
    "bar",
    "shop",
    "teahouse",
    "drink",
    "dessert",
    "station",
}

# Known Brand Aliases
# Used to map variations to the canonical brand name
BRAND_ALIASES = {
    "Kung Fu Tea": ["KFT", "Kungfu Tea", "功夫茶"],
    "Gong Cha": ["GongCha", "貢茶", "Gong Cha"],
    "Tiger Sugar": ["Tiger Sugar", "老虎堂"],
    "Sharetea": ["Share Tea", "歇腳亭", "Sharetea"],
    "CoCo Fresh Tea & Juice": ["CoCo", "Coco Tea", "CoCo都可", "Coco Fresh"],
    "CoCo都可": ["CoCo", "都可", "coco", "CoCo都可"],  # Taiwan specific key
    "Yi Fang Taiwan Fruit Tea": ["Yifang", "Yi Fang", "一芳"],
    "Yi Fang": ["Yi Fang", "一芳", "Yifang", "Yi Fang Taiwan Fruit Tea"],  # SG key
    "The Alley": ["鹿角巷", "The Alley"],
    "TP Tea": ["TP TEA", "Tpumps", "茶湯會"],
    "Ten Ren": ["Ten Ren's Tea", "Ten Ren Tea", "天仁茗茶", "天仁"],
    "Xing Fu Tang": ["XFT", "幸福堂", "XingFuTang"],
    "HEYTEA": ["Hey Tea", "喜茶", "HEYTEA"],
    "Chicha San Chen": ["ChiCha", "ChiCha San Chen", "吃茶三千"],
    "7 Leaves Cafe": ["7 Leaves", "Seven Leaves"],
    "Sunright Tea Studio": ["Sunright", "Sunright Tea", "日青良月"],
    "Feng Cha Teahouse": ["Feng Cha", "奉茶"],
    "Moge Tee": ["Moge", "愿茶"],
    "Meet Fresh": ["鮮芋仙"],
    "Wushiland Boba": ["OO Tea", "50 Lan", "50嵐", "Wushiland"],
    "50嵐": ["50嵐", "50 Lan", "五十嵐"],  # Taiwan key
    "OMOMO Tea Shoppe": ["OMOMO", "Omomo"],
    "Molly Tea": ["Molly"],
    "3CAT Tea": ["3 Cat", "3CAT"],
    "DaYung's Tea": ["Da Yung", "DaYungs", "大苑子"],
    "Camellia Tea Bar": ["Camellia Rd", "Camellia"],
    "Asha Tea House": ["Asha", "Asha Tea"],
    "Teaspoon": ["Tea Spoon"],
    "Ume Tea": ["Ume"],
    "Wanpo Tea Shop": ["Wanpo", "萬波"],
    "Vivi Bubble Tea": ["Vivi"],
    "Machi Machi": ["麥吉"],
    "Song Tea": ["宋茶"],
    "Tea Top": ["TeaTop", "Tea-Top"],
    "Happy Lemon": ["Happy Lemon", "快樂檸檬"],
    "Boba Guys": ["Boba Guys"],
    # Taiwan Specific
    "龜記": ["龜記", "Guiji", "GUIJI", "龜記茗品"],
    "清心福全": ["清心", "清心福全"],
    "一沐日": ["一沐日", "YIMU"],
    "UG樂己": ["UG", "樂己", "UG樂己"],
    "迷客夏": ["迷客夏", "Milksha", "MILKSHA"],
    "五桐號": ["五桐號", "WooTea", "Woo Tea"],
    "可不可熟成紅茶": [
        "可不可熟成紅茶"
    ],  # Add if needed, was in Brands list but no alias in text? Ah, implied
    # Singapore Specific
    "LiHO Tea": ["LiHO", "里喝", "Li Ho"],
    "KOI Thé": ["KOI", "KOI The", "KOI茶"],
    "Each A Cup": ["Each A Cup", "Each-A-Cup", "各一杯"],
    "Nayuki": ["Nayuki", "奈雪", "奈雪的茶", "Naixue"],
    "Chagee": ["Chagee", "霸王茶姬", "CHAGEE"],
    "R&B Tea": ["R&B", "R&B Tea", "R&B巡茶", "RB Tea"],
    "Hollin": ["Hollin", "賀凜", "HOLLIN"],
    "iTEA": ["iTEA", "iTea", "itea"],
    "Milksha": ["Milksha", "迷客夏", "MILKSHA"],
    "PlayMade": ["PlayMade", "Play Made", "Playmade"],
    "KEBUKE": ["KEBUKE", "可不可", "Kebuke", "可不可熟成紅茶"],
    "Bober Tea": ["Bober", "Bober Tea", "BOBER"],
    "The Whale Tea": ["Whale Tea", "The Whale Tea", "大鯨魚"],
}


def get_aliases_for_brand(brand_name: str) -> list[str]:
    """Get all aliases for a brand name."""
    return BRAND_ALIASES.get(brand_name, [])


def calculate_match_score(name1: str, name2: str) -> float:
    """
    Calculate fuzzy match score between two names using token set ratio.
    Returns 0-100 score.
    """
    if not name1 or not name2:
        return 0.0
    return fuzz.token_set_ratio(name1, name2)


def normalize_name(name: str) -> str:
    """
    Normalize a name using the standard processor (lowercase, trim, etc).
    """
    return utils.default_process(name)


def match_brand_from_name(
    shop_name: str, brand_name: str, brand_name_zh: str = None, aliases: list = None
) -> float:
    """
    Match a shop name to a brand.
    Returns confidence score (0.0 to 1.0).
    1.0 = Exact/Strong match
    0.95 = Multi-word partial match
    0.9 = Single strong word match
    0.0 = No match
    """
    if not shop_name or not brand_name:
        return 0.0

    shop_lower = shop_name.lower()
    brand_lower = brand_name.lower()

    # 1. Exact canonical match
    if brand_lower in shop_lower:
        return 1.0

    # 2. Chinese name match
    if brand_name_zh and brand_name_zh in shop_name:
        return 1.0

    # 3. Alias match
    # Use provided aliases or lookup
    check_aliases = (
        aliases if aliases is not None else get_aliases_for_brand(brand_name)
    )
    for alias in check_aliases:
        if alias.lower() in shop_lower:
            return 1.0

    # 4. Fuzzy Matching using RapidFuzz
    # We use the centralized scoring function
    score = calculate_match_score(brand_name, shop_name)

    if score >= 85:
        # Normalize to 0.0-1.0 scale
        return score / 100.0

    return 0.0


def find_best_brand_match(
    shop_name: str, brands_data: list[dict]
) -> tuple[dict, float]:
    """
    Find the best matching brand from a list of brand data/dicts.
    Each item in brands_data should have 'name', and optionally 'name_zh', 'aliases'.

    Returns (brand_data, confidence).
    """
    best_match = None
    best_conf = 0.0

    for brand in brands_data:
        conf = match_brand_from_name(
            shop_name, brand["name"], brand.get("name_zh"), brand.get("aliases")
        )

        if conf > best_conf:
            best_conf = conf
            best_match = brand
            # If we found a perfect match, return immediately
            if conf >= 1.0:
                return best_match, best_conf

    return best_match, best_conf
