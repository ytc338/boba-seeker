export interface Brand {
  id: number;
  name: string;
  name_zh?: string;
  logo_url?: string;
  description?: string;
  origin_country?: string;
  website?: string;
}

export interface Shop {
  id: number;
  name: string;
  brand_id?: number;
  address: string;
  city?: string;
  country: string;
  latitude: number;
  longitude: number;
  rating?: number;
  rating_count?: number;
  phone?: string;
  hours?: string;
  photo_url?: string;
  google_place_id?: string;
  brand?: Brand;
}

export interface ShopListResponse {
  shops: Shop[];
  total: number;
  page: number;
  page_size: number;
}

export interface FeedbackCreate {
  name?: string;
  email?: string;
  message: string;
  type: string;
}
