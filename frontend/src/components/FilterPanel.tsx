import { useState } from 'react';
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

export default function FilterPanel({
  brands,
  selectedBrands,
  selectedRegion,
  onBrandToggle,
  onRegionChange,
  onClearFilters,
}: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const filterCount = selectedBrands.length;

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
          <div className="brand-grid">
            {brands.length === 0 ? (
              <div className="no-brands">No brands in this region</div>
            ) : (
              brands.map((brand) => {
                const isChecked = selectedBrands.includes(brand.id);
                return (
                  <label
                    key={brand.id}
                    className={`brand-checkbox ${isChecked ? 'checked' : ''}`}
                    onClick={() => onBrandToggle(brand.id)}
                  >
                    <span className="checkmark">{isChecked ? '✓' : ''}</span>
                    <span className="brand-name">{brand.name_zh || brand.name}</span>
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
