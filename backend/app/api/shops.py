from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Shop
from ..schemas import ShopCreate, ShopListResponse, ShopResponse

router = APIRouter()


@router.get("", response_model=ShopListResponse)
def list_shops(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    country: Optional[str] = None,
    city: Optional[str] = None,
    brand_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """List all shops with pagination and filters"""
    query = db.query(Shop)

    if country:
        query = query.filter(Shop.country == country)
    if city:
        query = query.filter(Shop.city == city)
    if brand_id:
        query = query.filter(Shop.brand_id == brand_id)

    total = query.count()
    shops = query.offset((page - 1) * page_size).limit(page_size).all()

    return ShopListResponse(shops=shops, total=total, page=page, page_size=page_size)


@router.get("/search", response_model=list[ShopResponse])
def search_shops(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Search shops by name or address"""
    shops = (
        db.query(Shop)
        .filter((Shop.name.ilike(f"%{q}%")) | (Shop.address.ilike(f"%{q}%")))
        .limit(limit)
        .all()
    )
    return shops


@router.get("/nearby", response_model=list[ShopResponse])
def nearby_shops(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5, ge=0.1, le=50),
    limit: int = Query(500, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Find shops near a location (simple distance calculation)"""
    import math

    # Simple bounding box filter (not perfect sphere distance)
    # 1 degree latitude ≈ 111km
    lat_delta = radius_km / 111
    # 1 degree longitude varies by latitude: 111km * cos(lat)
    cos_lat = math.cos(math.radians(lat)) if lat != 0 else 1
    lng_delta = radius_km / (111 * cos_lat)

    shops = (
        db.query(Shop)
        .filter(
            Shop.latitude.between(lat - lat_delta, lat + lat_delta),
            Shop.longitude.between(lng - lng_delta, lng + lng_delta),
        )
        .limit(limit)
        .all()
    )

    return shops


@router.get("/{shop_id}", response_model=ShopResponse)
def get_shop(shop_id: int, db: Session = Depends(get_db)):
    """Get a single shop by ID"""
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.post("", response_model=ShopResponse, status_code=201)
def create_shop(shop: ShopCreate, db: Session = Depends(get_db)):
    """Create a new shop"""
    db_shop = Shop(**shop.model_dump())
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    return db_shop
