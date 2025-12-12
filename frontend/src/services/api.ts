import axios from 'axios';
import type { Shop, ShopListResponse, Brand } from '../types';

// In production (Docker), nginx proxies /api to backend
// In development, we need the full URL
const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_URL,
});

export async function getShops(params?: {
  page?: number;
  page_size?: number;
  country?: string;
  city?: string;
  brand_ids?: number[];
}): Promise<ShopListResponse> {
  // Build query params, handling brand_ids array specially
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.append('page', String(params.page));
  if (params?.page_size) queryParams.append('page_size', String(params.page_size));
  if (params?.country) queryParams.append('country', params.country);
  if (params?.city) queryParams.append('city', params.city);
  if (params?.brand_ids) {
    params.brand_ids.forEach(id => queryParams.append('brand_ids', String(id)));
  }
  
  const response = await api.get(`/api/shops?${queryParams.toString()}`);
  return response.data;
}

export async function getShop(id: number): Promise<Shop> {
  const response = await api.get(`/api/shops/${id}`);
  return response.data;
}

export async function searchShops(query: string, limit = 10): Promise<Shop[]> {
  const response = await api.get('/api/shops/search', {
    params: { q: query, limit },
  });
  return response.data;
}

export async function getNearbyShops(
  lat: number,
  lng: number,
  radiusKm = 5
): Promise<Shop[]> {
  const response = await api.get('/api/shops/nearby', {
    params: { lat, lng, radius_km: radiusKm },
  });
  return response.data;
}

export interface MapBounds {
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
}

export async function getShopsInBounds(
  bounds: MapBounds,
  brandIds?: number[]
): Promise<Shop[]> {
  const params = new URLSearchParams({
    min_lat: String(bounds.minLat),
    max_lat: String(bounds.maxLat),
    min_lng: String(bounds.minLng),
    max_lng: String(bounds.maxLng),
  });
  if (brandIds) {
    brandIds.forEach(id => params.append('brand_ids', String(id)));
  }
  const response = await api.get(`/api/shops/bounds?${params.toString()}`);
  return response.data;
}

export async function getBrands(): Promise<Brand[]> {
  const response = await api.get('/api/brands');
  return response.data;
}

export default api;
