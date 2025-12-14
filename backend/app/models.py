from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .database import Base


class ShopStatus(enum.Enum):
    """Status of a shop"""
    ACTIVE = "active"
    CLOSED = "closed"
    UNVERIFIED = "unverified"


class Brand(Base):
    """Boba tea brand/chain"""
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    name_zh = Column(String(100))  # Chinese name
    logo_url = Column(String(500))
    description = Column(Text)
    origin_country = Column(String(50))
    website = Column(String(500))

    shops = relationship("Shop", back_populates="brand")


class Shop(Base):
    """Individual boba tea shop location"""
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
    
    # Location
    address = Column(String(500), nullable=False)
    city = Column(String(100))
    country = Column(String(50), nullable=False)  # 'TW' or 'US'
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Details
    rating = Column(Float)  # Google rating
    rating_count = Column(Integer)
    phone = Column(String(50))
    hours = Column(Text)  # JSON string of opening hours
    photo_url = Column(String(500))
    google_place_id = Column(String(100), unique=True, index=True)
    
    # Maintenance fields
    status = Column(String(20), default="active")  # active, closed, unverified
    last_verified = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = relationship("Brand", back_populates="shops")

