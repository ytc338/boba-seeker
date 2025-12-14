import { useState, useEffect, useMemo } from 'react';
import type { Shop, Brand } from '../types';
import { getShops, getBrands } from '../services/api';
import Map from '../components/Map';
import FilterPanel from '../components/FilterPanel';
import BottomSheet from '../components/BottomSheet';
import './HomePage.css';

type CountryFilter = 'all' | 'TW' | 'US';

export default function HomePage() {
  // Data state
  const [allShops, setAllShops] = useState<Shop[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [selectedShop, setSelectedShop] = useState<Shop | null>(null);
  
  // Filter state
  const [countryFilter, setCountryFilter] = useState<CountryFilter>('TW');
  const [selectedBrands, setSelectedBrands] = useState<number[]>([]);
  
  // Loading state
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  // Fetch shops when REGION changes (backend filter)
  useEffect(() => {
    async function fetchShops() {
      try {
        setLoading(true);
        setError(null);
        
        const params: { country?: string; page_size: number } = {
          page_size: 5000, // Load all shops in region
        };
        if (countryFilter !== 'all') {
          params.country = countryFilter;
        }
        
        const response = await getShops(params);
        setAllShops(response.shops);
        setSelectedShop(null); // Clear selection on region change
      } catch (err) {
        console.error('Failed to fetch shops:', err);
        setError('Failed to load shops. Make sure the backend is running.');
      } finally {
        setLoading(false);
      }
    }

    fetchShops();
  }, [countryFilter]);

  // Client-side filtering by brand (instant!)
  const filteredShops = useMemo(() => {
    if (selectedBrands.length === 0) {
      return allShops; // No brand filter = show all
    }
    return allShops.filter(
      (shop) => shop.brand_id && selectedBrands.includes(shop.brand_id)
    );
  }, [allShops, selectedBrands]);

  // Toggle brand selection
  const handleBrandToggle = (brandId: number) => {
    setSelectedBrands((prev) =>
      prev.includes(brandId)
        ? prev.filter((id) => id !== brandId)
        : [...prev, brandId]
    );
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
        />
      </div>

      {/* Filter Panel (FAB + slide-down) - positioned below map controls */}
      <FilterPanel
        brands={brands}
        selectedBrands={selectedBrands}
        onBrandToggle={handleBrandToggle}
        countryFilter={countryFilter}
        onCountryChange={setCountryFilter}
        onClearFilters={handleClearFilters}
      />

      {/* Bottom Sheet (shop list) */}
      <BottomSheet
        shops={filteredShops}
        selectedShop={selectedShop}
        onShopSelect={setSelectedShop}
        loading={loading}
        error={error}
      />
    </div>
  );
}
