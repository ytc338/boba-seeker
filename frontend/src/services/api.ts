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
  brand_id?: number;
}): Promise<ShopListResponse> {
  const response = await api.get('/api/shops', { params });
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

export async function getBrands(): Promise<Brand[]> {
  const response = await api.get('/api/brands');
  return response.data;
}

export default api;
