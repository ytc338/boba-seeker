import { useState } from 'react';
import type { Brand } from '../types';
import './FilterPanel.css';

type CountryFilter = 'all' | 'TW' | 'US';

interface FilterPanelProps {
  brands: Brand[];
  selectedBrands: number[];
  onBrandToggle: (brandId: number) => void;
  countryFilter: CountryFilter;
  onCountryChange: (country: CountryFilter) => void;
  onClearFilters: () => void;
}

export default function FilterPanel({
  brands,
  selectedBrands,
  onBrandToggle,
  countryFilter,
  onCountryChange,
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
        {/* Region Filter */}
        <div className="filter-section">
          <div className="filter-title">Region</div>
          <div className="region-buttons">
            <button
              className={`region-btn ${countryFilter === 'all' ? 'active' : ''}`}
              onClick={() => onCountryChange('all')}
            >
              🌍 All
            </button>
            <button
              className={`region-btn ${countryFilter === 'TW' ? 'active' : ''}`}
              onClick={() => onCountryChange('TW')}
            >
              🇹🇼 Taiwan
            </button>
            <button
              className={`region-btn ${countryFilter === 'US' ? 'active' : ''}`}
              onClick={() => onCountryChange('US')}
            >
              🇺🇸 USA
            </button>
          </div>
        </div>

        {/* Brand Filter */}
        <div className="filter-section">
          <div className="filter-title">Brands ({brands.length})</div>
          <div className="brand-grid">
            {brands.map((brand) => {
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
            })}
          </div>
        </div>

        {/* Clear Filters */}
        {filterCount > 0 && (
          <button className="clear-filters" onClick={onClearFilters}>
            Clear All Filters ({filterCount})
          </button>
        )}
      </div>
    </>
  );
}
