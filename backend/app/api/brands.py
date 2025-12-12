from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Brand
from ..schemas import BrandResponse, BrandCreate

router = APIRouter()


@router.get("", response_model=list[BrandResponse])
def list_brands(db: Session = Depends(get_db)):
    """List all brands"""
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
