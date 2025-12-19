import { useState, useMemo } from 'react';
import type { Brand } from '../types';
import './FilterPanel.css';

// Available regions with their country codes and emoji flags
const REGIONS = [
  { code: '', label: 'All', emoji: '🌍' },
  { code: 'TW', label: 'Taiwan', emoji: '🇹🇼' },
  { code: 'SG', label: 'Singapore', emoji: '🇸🇬' },
  { code: 'US', label: 'USA', emoji: '🇺🇸' },
];

interface FilterPanelProps {
  brands: Brand[];
  selectedBrands: number[];
  selectedRegion: string;
  onBrandToggle: (brandId: number) => void;
  onRegionChange: (region: string) => void;
  onClearFilters: () => void;
}

// Get displayed brand name based on region
// Shows original name in parentheses if brand is from overseas
function getBrandDisplayName(brand: Brand, region: string): string {
  const hasEnglish = !!brand.name;
  const hasChinese = !!brand.name_zh;
  const hasBothNames = hasEnglish && hasChinese && brand.name !== brand.name_zh;
  
  // TW uses Chinese as primary, other regions use English
  if (region === 'TW') {
    const primary = brand.name_zh || brand.name;
    // If brand has English name different from Chinese, show it in parentheses
    if (hasBothNames && brand.name_zh) {
      return `${brand.name_zh} (${brand.name})`;
    }
    return primary;
  }
  
  // SG, US, and "All" use English name as primary
  const primary = brand.name || brand.name_zh || '';
  // If brand has Chinese name different from English, show it in parentheses
  if (hasBothNames && brand.name) {
    return `${brand.name} (${brand.name_zh})`;
  }
  return primary;
}

export default function FilterPanel({
  brands,
  selectedBrands,
  selectedRegion,
  onBrandToggle,
  onRegionChange,
  onClearFilters,
}: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const filterCount = selectedBrands.length;

  // Filter and sort brands
  const displayedBrands = useMemo(() => {
    // First, add display name to each brand
    const brandsWithDisplayName = brands.map(brand => ({
      ...brand,
      displayName: getBrandDisplayName(brand, selectedRegion),
    }));

    // Filter by search query (search display name, English name, and Chinese name)
    const filtered = searchQuery.trim()
      ? brandsWithDisplayName.filter(brand => {
          const query = searchQuery.toLowerCase();
          const nameMatch = brand.name?.toLowerCase().includes(query);
          const nameZhMatch = brand.name_zh?.toLowerCase().includes(query);
          const displayMatch = brand.displayName.toLowerCase().includes(query);
          return nameMatch || nameZhMatch || displayMatch;
        })
      : brandsWithDisplayName;

    // Sort alphabetically by display name
    return filtered.sort((a, b) => 
      a.displayName.localeCompare(b.displayName, selectedRegion === 'TW' ? 'zh' : 'en')
    );
  }, [brands, searchQuery, selectedRegion]);

  return (
    <>
      {/* Floating Action Button */}
      <button
        className={`filter-fab ${isOpen ? 'active' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle filters"
      >
        ☰
        {filterCount > 0 && <span className="filter-badge">{filterCount}</span>}
      </button>

      {/* Filter Panel */}
      <div className={`filter-panel ${isOpen ? 'open' : ''}`}>
        {/* Region Selector */}
        <div className="filter-section">
          <div className="filter-title">Region</div>
          <div className="region-buttons">
            {REGIONS.map((region) => (
              <button
                key={region.code}
                className={`region-btn ${selectedRegion === region.code ? 'active' : ''}`}
                onClick={() => onRegionChange(region.code)}
              >
                {region.emoji} {region.label}
              </button>
            ))}
          </div>
        </div>

        {/* Brand Filter */}
        <div className="filter-section">
          <div className="filter-title">Filter by Brand</div>
          
          {/* Search Input */}
          <div className="brand-search">
            <input
              type="text"
              placeholder="Search brands..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="brand-search-input"
            />
            {searchQuery && (
              <button 
                className="search-clear" 
                onClick={() => setSearchQuery('')}
                aria-label="Clear search"
              >
                ×
              </button>
            )}
          </div>

          {/* Brand List */}
          <div className="brand-grid">
            {displayedBrands.length === 0 ? (
              <div className="no-brands">
                {brands.length === 0 ? 'No brands in this region' : 'No matching brands'}
              </div>
            ) : (
              displayedBrands.map((brand) => {
                const isChecked = selectedBrands.includes(brand.id);
                return (
                  <label
                    key={brand.id}
                    className={`brand-checkbox ${isChecked ? 'checked' : ''}`}
                    onClick={() => onBrandToggle(brand.id)}
                  >
                    <span className="checkmark">{isChecked ? '✓' : ''}</span>
                    <span className="brand-name">{brand.displayName}</span>
                  </label>
                );
              })
            )}
          </div>
        </div>

        {/* Clear Filters */}
        {filterCount > 0 && (
          <button className="clear-filters" onClick={onClearFilters}>
            Clear Filters ({filterCount})
          </button>
        )}
      </div>
    </>
  );
}
