from typing import Optional

from pydantic import BaseModel


class BrandBase(BaseModel):
    name: str
    name_zh: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    origin_country: Optional[str] = None
    website: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    id: int

    class Config:
        from_attributes = True


class ShopBase(BaseModel):
    name: str
    brand_id: Optional[int] = None
    address: str
    city: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    phone: Optional[str] = None
    hours: Optional[str] = None
    photo_url: Optional[str] = None
    google_place_id: Optional[str] = None


class ShopCreate(ShopBase):
    pass


class ShopResponse(ShopBase):
    id: int
    brand: Optional[BrandResponse] = None

    class Config:
        from_attributes = True


class ShopListResponse(BaseModel):
    shops: list[ShopResponse]
    total: int
    page: int
    page_size: int


class FeedbackBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    message: str
    type: Optional[str] = "contact"


class FeedbackCreate(FeedbackBase):
    pass
