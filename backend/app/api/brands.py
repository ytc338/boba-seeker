from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Brand, Shop
from ..schemas import BrandCreate, BrandResponse

router = APIRouter()


@router.get("", response_model=list[BrandResponse])
def list_brands(
    country: Optional[str] = Query(
        None, description="Filter brands by country with shop presence"
    ),
    db: Session = Depends(get_db),
):
    """List brands, optionally filtered by country with shop presence"""
    if country:
        # Only return brands that have at least one shop in this country
        return (
            db.query(Brand).join(Shop).filter(Shop.country == country).distinct().all()
        )
    return db.query(Brand).all()


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Get a single brand by ID"""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("", response_model=BrandResponse, status_code=201)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    """Create a new brand"""
    db_brand = Brand(**brand.model_dump())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand
