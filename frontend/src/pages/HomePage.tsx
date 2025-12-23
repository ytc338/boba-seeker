import { useState, useEffect, useMemo, useCallback } from 'react';
import type { Shop, Brand } from '../types';
import { getNearbyShops, getBrands } from '../services/api';
import Map from '../components/Map';
import FilterPanel from '../components/FilterPanel';
import BottomSheet from '../components/BottomSheet';
import './HomePage.css';

// Default center: Taipei
const DEFAULT_CENTER = { lat: 25.03, lng: 121.5 };

// Helper to detect region from coordinates
function detectRegion(lat: number, lng: number): string {
  // Taiwan bounding box (approximate)
  if (lat >= 21.5 && lat <= 26.5 && lng >= 119.5 && lng <= 122.5) {
    return 'TW';
  }
  // Singapore bounding box (approximate)
  if (lat >= 1.1 && lat <= 1.5 && lng >= 103.6 && lng <= 104.1) {
    return 'SG';
  }
  // USA bounding box (very rough - continental US)
  if (lat >= 24 && lat <= 50 && lng >= -125 && lng <= -66) {
    return 'US';
  }
  // Default to showing all
  return '';
}

export default function HomePage() {
  // Data state
  const [shops, setShops] = useState<Shop[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedShop, setSelectedShop] = useState<Shop | null>(null);
  
  // Filter state
  const [selectedBrands, setSelectedBrands] = useState<number[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>(''); // '' = All
  
  // Loading state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Map bounds for "Search This Area"
  const [mapBounds, setMapBounds] = useState<{
    minLat: number; maxLat: number; minLng: number; maxLng: number;
  } | null>(null);
  const [showSearchButton, setShowSearchButton] = useState(false);
  
  // Bottom sheet height for map padding
  const [sheetHeight, setSheetHeight] = useState(0);

  // Fetch brands when region changes
  useEffect(() => {
    getBrands(selectedRegion || undefined)
      .then(setBrands)
      .catch((err) => console.error('Failed to fetch brands:', err));
    
    // Clear brand selection when region changes
    setSelectedBrands([]);
  }, [selectedRegion]);

  // Load nearby shops based on center point
  const loadNearbyShops = useCallback(async (lat: number, lng: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await getNearbyShops(lat, lng, 10); // 10km radius
      setShops(data);
      
      // Auto-detect and set region based on coordinates
      const detectedRegion = detectRegion(lat, lng);
      setSelectedRegion(detectedRegion);
    } catch (err) {
      console.error('Failed to fetch nearby shops:', err);
      setError('Failed to load shops.');
    } finally {
      setLoading(false);
    }
  }, []);

  // On mount: try GPS, fallback to Taipei
  useEffect(() => {
    if (!navigator.geolocation) {
      loadNearbyShops(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        loadNearbyShops(position.coords.latitude, position.coords.longitude);
      },
      () => {
        // Denied or error - fallback to Taipei
        loadNearbyShops(DEFAULT_CENTER.lat, DEFAULT_CENTER.lng);
      },
      { enableHighAccuracy: true, timeout: 5000 }
    );
  }, [loadNearbyShops]);

  // Handle map movement - show search button
  const handleMapMove = useCallback((bounds: {
    minLat: number; maxLat: number; minLng: number; maxLng: number;
  }) => {
    setMapBounds(bounds);
    setShowSearchButton(true);
  }, []);

  // Search this area
  const handleSearchArea = useCallback(async () => {
    if (!mapBounds) return;
    
    // Calculate center of visible bounds
    const centerLat = (mapBounds.minLat + mapBounds.maxLat) / 2;
    const centerLng = (mapBounds.minLng + mapBounds.maxLng) / 2;
    
    // Calculate approximate radius from bounds
    const latDiff = (mapBounds.maxLat - mapBounds.minLat) / 2;
    const radiusKm = latDiff * 111; // 1 degree ≈ 111km
    
    try {
      setLoading(true);
      setError(null);
      setShowSearchButton(false);
      const data = await getNearbyShops(centerLat, centerLng, Math.max(radiusKm, 5));
      setShops(data);
      
      // Update region based on new map center
      const detectedRegion = detectRegion(centerLat, centerLng);
      setSelectedRegion(detectedRegion);
    } catch (err) {
      console.error('Failed to search area:', err);
      setError('Failed to search this area.');
    } finally {
      setLoading(false);
    }
  }, [mapBounds]);

  // Client-side filtering by brand
  const filteredShops = useMemo(() => {
    if (selectedBrands.length === 0) {
      return shops;
    }
    return shops.filter(
      (shop) => shop.brand_id && selectedBrands.includes(shop.brand_id)
    );
  }, [shops, selectedBrands]);

  // Toggle brand selection
  const handleBrandToggle = (brandId: number) => {
    setSelectedBrands((prev) =>
      prev.includes(brandId)
        ? prev.filter((id) => id !== brandId)
        : [...prev, brandId]
    );
  };

  // Handle region change
  const handleRegionChange = (region: string) => {
    setSelectedRegion(region);
  };

  // Clear all filters
  const handleClearFilters = () => {
    setSelectedBrands([]);
  };

  return (
    <div className="home-page map-first">
      {/* Full-screen Map */}
      <div className="map-container">
        <Map
          shops={filteredShops}
          selectedShop={selectedShop}
          onShopSelect={setSelectedShop}
          onMapMove={handleMapMove}
          showSearchButton={showSearchButton}
          onSearchClick={handleSearchArea}
          searchLoading={loading}
          bottomPadding={sheetHeight}
        />
      </div>

      {/* Filter Panel */}
      <FilterPanel
        brands={brands}
        selectedBrands={selectedBrands}
        selectedRegion={selectedRegion}
        onBrandToggle={handleBrandToggle}
        onRegionChange={handleRegionChange}
        onClearFilters={handleClearFilters}
      />

      {/* Bottom Sheet */}
      <BottomSheet
        shops={filteredShops}
        selectedShop={selectedShop}
        onShopSelect={setSelectedShop}
        loading={loading}
        error={error}
        onHeightChange={setSheetHeight}
      />
    </div>
  );
}
