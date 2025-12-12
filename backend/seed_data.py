"""
Seed the database with sample boba shop data for development.

Run this script after starting the backend to populate sample data:
    python seed_data.py
"""

from app.database import SessionLocal, engine, Base
from app.models import Brand, Shop

# Create tables
Base.metadata.create_all(bind=engine)

# Sample brands
BRANDS = [
    {
        "name": "50嵐",
        "name_zh": "50嵐",
        "origin_country": "TW",
        "description": "One of Taiwan's most popular bubble tea chains, known for consistent quality.",
        "website": "https://www.50lan.com.tw/"
    },
    {
        "name": "CoCo",
        "name_zh": "CoCo都可",
        "origin_country": "TW",
        "description": "International bubble tea chain with locations worldwide.",
        "website": "https://www.coco-tea.com/"
    },
    {
        "name": "珍煮丹",
        "name_zh": "珍煮丹",
        "origin_country": "TW",
        "description": "Known for their brown sugar pearl milk, a must-try in Taiwan.",
        "website": "https://www.jld-drink.com/"
    },
    {
        "name": "迷客夏",
        "name_zh": "迷客夏",
        "origin_country": "TW",
        "description": "Popular for their fresh milk tea and green tea options.",
        "website": "https://www.milkshoptea.com/"
    },
    {
        "name": "Kung Fu Tea",
        "name_zh": "功夫茶",
        "origin_country": "US",
        "description": "Largest bubble tea franchise in the United States.",
        "website": "https://www.kungfutea.com/"
    },
    {
        "name": "Tiger Sugar",
        "name_zh": "老虎堂",
        "origin_country": "TW",
        "description": "Famous for tiger stripe brown sugar boba milk.",
        "website": "https://www.tigersugarusa.com/"
    }
]

# Sample shops in Taiwan (Taipei area)
TAIWAN_SHOPS = [
    {
        "name": "50嵐 台北信義店",
        "brand_name": "50嵐",
        "address": "台北市信義區信義路五段7號",
        "city": "Taipei",
        "country": "TW",
        "latitude": 25.0330,
        "longitude": 121.5654,
        "rating": 4.3,
        "rating_count": 245
    },
    {
        "name": "50嵐 台北忠孝店",
        "brand_name": "50嵐",
        "address": "台北市大安區忠孝東路四段216號",
        "city": "Taipei",
        "country": "TW",
        "latitude": 25.0418,
        "longitude": 121.5513,
        "rating": 4.4,
        "rating_count": 312
    },
    {
        "name": "CoCo都可 台北站前店",
        "brand_name": "CoCo",
        "address": "台北市中正區忠孝西路一段36號",
        "city": "Taipei",
        "country": "TW",
        "latitude": 25.0461,
        "longitude": 121.5170,
        "rating": 4.2,
        "rating_count": 189
    },
    {
        "name": "珍煮丹 西門店",
        "brand_name": "珍煮丹",
        "address": "台北市萬華區漢中街51號",
        "city": "Taipei",
        "country": "TW",
        "latitude": 25.0424,
        "longitude": 121.5081,
        "rating": 4.5,
        "rating_count": 567
    },
    {
        "name": "迷客夏 台北永康店",
        "brand_name": "迷客夏",
        "address": "台北市大安區永康街31巷9號",
        "city": "Taipei",
        "country": "TW",
        "latitude": 25.0306,
        "longitude": 121.5297,
        "rating": 4.4,
        "rating_count": 234
    },
    {
        "name": "Tiger Sugar 台北101店",
        "brand_name": "Tiger Sugar",
        "address": "台北市信義區市府路45號",
        "city": "Taipei",
        "country": "TW",
        "latitude": 25.0339,
        "longitude": 121.5645,
        "rating": 4.6,
        "rating_count": 892
    }
]

# Sample shops in US
US_SHOPS = [
    {
        "name": "Kung Fu Tea - Flushing",
        "brand_name": "Kung Fu Tea",
        "address": "133-42 39th Ave, Flushing, NY 11354",
        "city": "New York",
        "country": "US",
        "latitude": 40.7614,
        "longitude": -73.8307,
        "rating": 4.3,
        "rating_count": 456
    },
    {
        "name": "Kung Fu Tea - Los Angeles Chinatown",
        "brand_name": "Kung Fu Tea",
        "address": "727 N Broadway, Los Angeles, CA 90012",
        "city": "Los Angeles",
        "country": "US",
        "latitude": 34.0622,
        "longitude": -118.2395,
        "rating": 4.2,
        "rating_count": 321
    },
    {
        "name": "Tiger Sugar - San Gabriel",
        "brand_name": "Tiger Sugar",
        "address": "227 W Valley Blvd, San Gabriel, CA 91776",
        "city": "Los Angeles",
        "country": "US",
        "latitude": 34.0963,
        "longitude": -118.1058,
        "rating": 4.5,
        "rating_count": 678
    },
    {
        "name": "CoCo Fresh Tea & Juice - San Francisco",
        "brand_name": "CoCo",
        "address": "772 Clement St, San Francisco, CA 94118",
        "city": "San Francisco",
        "country": "US",
        "latitude": 37.7829,
        "longitude": -122.4663,
        "rating": 4.1,
        "rating_count": 234
    }
]


def seed_database():
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing_brands = db.query(Brand).count()
        if existing_brands > 0:
            print("Database already seeded. Skipping...")
            return
        
        # Create brands
        brand_map = {}
        for brand_data in BRANDS:
            brand = Brand(**brand_data)
            db.add(brand)
            db.flush()
            brand_map[brand_data["name"]] = brand.id
        
        # Create Taiwan shops
        for shop_data in TAIWAN_SHOPS:
            brand_name = shop_data.pop("brand_name")
            shop_data["brand_id"] = brand_map.get(brand_name)
            shop = Shop(**shop_data)
            db.add(shop)
        
        # Create US shops
        for shop_data in US_SHOPS:
            brand_name = shop_data.pop("brand_name")
            shop_data["brand_id"] = brand_map.get(brand_name)
            shop = Shop(**shop_data)
            db.add(shop)
        
        db.commit()
        print(f"✅ Seeded {len(BRANDS)} brands and {len(TAIWAN_SHOPS) + len(US_SHOPS)} shops")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
