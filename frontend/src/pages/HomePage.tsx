import { useState, useEffect, useMemo, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import type { Shop, Brand } from '../types';
import { getNearbyShops, getBrands, searchShops } from '../services/api';
import Map from '../components/Map';
import FilterPanel from '../components/FilterPanel';
import BottomSheet from '../components/BottomSheet';
import RouletteOverlay from '../components/RouletteOverlay';
import './HomePage.css';

// Default center: New York
const DEFAULT_CENTER = { lat: 40.74, lng: -74.98 };

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

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Shop[] | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // Roulette state
  const location = useLocation();
  const navigate = useNavigate();
  const [rouletteState, setRouletteState] = useState<'idle' | 'spinning'>('idle');
  const [highlightedShopId, setHighlightedShopId] = useState<number | null>(null);

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

  // On mount: try GPS, fallback to default
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
    const base = searchResults ?? shops;
    if (selectedBrands.length === 0) {
      return base;
    }
    return base.filter(
      (shop) => shop.brand_id && selectedBrands.includes(shop.brand_id)
    );
  }, [shops, searchResults, selectedBrands]);

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

  // Search by name
  const handleSearchSubmit = useCallback(async () => {
    const query = searchQuery.trim();
    if (!query) return;

    try {
      setSearchLoading(true);
      const results = await searchShops(query, 50);
      setSearchResults(results);
      setSelectedShop(null);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setSearchLoading(false);
    }
  }, [searchQuery]);

  const handleSearchClear = useCallback(() => {
    setSearchQuery('');
    setSearchResults(null);
  }, []);

  // Roulette Logic
  const startRoulette = useCallback(() => {
    // Only pick from shops currently visible on the map
    let visibleShops = filteredShops;
    if (mapBounds) {
      visibleShops = filteredShops.filter(shop =>
        shop.latitude >= mapBounds.minLat &&
        shop.latitude <= mapBounds.maxLat &&
        shop.longitude >= mapBounds.minLng &&
        shop.longitude <= mapBounds.maxLng
      );
    }

    if (visibleShops.length === 0) {
      alert('No boba shops visible in this area! Try zooming out or panning to a different spot.');
      return;
    }

    setRouletteState('spinning');
    setSelectedShop(null); // Clear selection

    // Animation settings
    const duration = 2000; // 2 seconds spin
    const intervalTime = 100; // Switch every 100ms
    const startTime = Date.now();

    const intervalId = setInterval(() => {
      // Pick random shop from visible set to highlight
      const randomIndex = Math.floor(Math.random() * visibleShops.length);
      setHighlightedShopId(visibleShops[randomIndex].id);

      // Check if time is up
      if (Date.now() - startTime >= duration) {
        clearInterval(intervalId);

        // Pick winner from visible set
        const winnerIndex = Math.floor(Math.random() * visibleShops.length);
        const winner = visibleShops[winnerIndex];

        setHighlightedShopId(null);
        setRouletteState('idle');
        setSelectedShop(winner); // This triggers map flyTo in Map component
      }
    }, intervalTime);

    return () => clearInterval(intervalId);
  }, [filteredShops, mapBounds]);

  // Listen for URL param ?action=explore
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.get('action') === 'explore') {
      // Remove param without reload
      navigate(location.pathname, { replace: true });

      if (!loading) {
         startRoulette();
      } else {
         const checkLoaded = setInterval(() => {
             if (!loading && shops.length > 0) {
                 clearInterval(checkLoaded);
                 startRoulette();
             }
         }, 500);
         setTimeout(() => clearInterval(checkLoaded), 5000);
      }
    }
  }, [location, navigate, startRoulette, loading, shops.length]);

  return (
    <div className="home-page map-first">
      {/* Roulette Overlay */}
      <RouletteOverlay
        isSpinning={rouletteState === 'spinning'}
        currentShopName={
          highlightedShopId
            ? filteredShops.find(s => s.id === highlightedShopId)?.name
            : undefined
        }
      />

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
          highlightedShopId={highlightedShopId}
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
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onSearchSubmit={handleSearchSubmit}
        searchLoading={searchLoading}
        onSearchClear={handleSearchClear}
        isSearchActive={searchResults !== null}
      />
    </div>
  );
}
