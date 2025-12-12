import { useState, useEffect, useCallback } from 'react';
import type { Shop, Brand } from '../types';
import { getShopsInBounds, getBrands, type MapBounds } from '../services/api';
import Map from '../components/Map';
import ShopCard from '../components/ShopCard';
import DrinkRec from '../components/DrinkRec';
import './HomePage.css';

export default function HomePage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedShop, setSelectedShop] = useState<Shop | null>(null);
  const [brandFilters, setBrandFilters] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  
  // Map bounds and search state
  const [mapBounds, setMapBounds] = useState<MapBounds | null>(null);
  const [showSearchButton, setShowSearchButton] = useState(false);

  // Toggle brand in filter
  const toggleBrandFilter = (brandId: number) => {
    setBrandFilters(prev => {
      const next = new Set(prev);
      if (next.has(brandId)) {
        next.delete(brandId);
      } else {
        next.add(brandId);
      }
      return next;
    });
    // Show search button when filters change (if we've searched before)
    if (hasSearched) {
      setShowSearchButton(true);
    }
  };

  // Fetch brands on mount
  useEffect(() => {
    async function fetchBrands() {
      try {
        const data = await getBrands();
        setBrands(data);
      } catch (err) {
        console.error('Failed to fetch brands:', err);
      }
    }
    fetchBrands();
  }, []);

  // Handle bounds change from map
  const handleBoundsChange = useCallback((bounds: MapBounds) => {
    setMapBounds(bounds);
    // Show search button when map moves (after initial search)
    if (hasSearched) {
      setShowSearchButton(true);
    }
  }, [hasSearched]);

  // Search shops in current area
  const handleSearchArea = async () => {
    if (!mapBounds) return;
    
    try {
      setLoading(true);
      setError(null);
      const brandIds = brandFilters.size > 0 ? Array.from(brandFilters) : undefined;
      const results = await getShopsInBounds(mapBounds, brandIds);
      setShops(results);
      setShowSearchButton(false);
      setHasSearched(true);
    } catch (err) {
      console.error('Failed to fetch shops:', err);
      setError('Failed to load shops. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-page">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Boba Shops</h2>
          
          {/* Brand Filter */}
          <div className="filter-section">
            <div className="filter-label-row">
              <label className="filter-label">Brands</label>
              {brandFilters.size > 0 && (
                <button 
                  className="clear-filters-btn" 
                  onClick={() => {
                    setBrandFilters(new Set());
                    if (hasSearched) setShowSearchButton(true);
                  }}
                >
                  Clear all
                </button>
              )}
            </div>
            <div className="brand-checkboxes">
              {brands.map((brand) => (
                <label key={brand.id} className="brand-checkbox">
                  <input
                    type="checkbox"
                    checked={brandFilters.has(brand.id)}
                    onChange={() => toggleBrandFilter(brand.id)}
                  />
                  <span className="checkbox-label">{brand.name_zh || brand.name}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Drink Recommendations */}
          <DrinkRec brandNames={
            selectedShop?.brand?.name 
              ? [selectedShop.brand.name]
              : brandFilters.size > 0 
                ? brands.filter(b => brandFilters.has(b.id)).map(b => b.name)
                : undefined
          } />
        </div>

        <div className="shop-list">
          {loading && <div className="loading">Searching for shops...</div>}

          {error && <div className="error">{error}</div>}

          {!loading && !error && !hasSearched && (
            <div className="empty-prompt">
              <span className="empty-icon">🗺️</span>
              <p>Pan the map to your desired area</p>
              <p className="empty-hint">Then click "Search This Area" to find shops</p>
            </div>
          )}

          {!loading && !error && hasSearched && shops.length === 0 && (
            <div className="empty">No shops found in this area</div>
          )}

          {shops.map((shop) => (
            <ShopCard
              key={shop.id}
              shop={shop}
              isSelected={selectedShop?.id === shop.id}
              onClick={() => setSelectedShop(shop)}
            />
          ))}
        </div>
      </aside>

      <main className="map-section">
        <Map
          shops={shops}
          selectedShop={selectedShop}
          onShopSelect={setSelectedShop}
          onBoundsChange={handleBoundsChange}
          showSearchButton={mapBounds !== null && (showSearchButton || !hasSearched)}
          onSearchClick={handleSearchArea}
          searchLoading={loading}
        />
      </main>
    </div>
  );
}
