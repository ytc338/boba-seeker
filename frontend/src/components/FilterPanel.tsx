import { useState } from 'react';
import type { Brand } from '../types';
import './FilterPanel.css';

interface FilterPanelProps {
  brands: Brand[];
  selectedBrands: number[];
  onBrandToggle: (brandId: number) => void;
  onClearFilters: () => void;
}

export default function FilterPanel({
  brands,
  selectedBrands,
  onBrandToggle,
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
        {/* Brand Filter */}
        <div className="filter-section">
          <div className="filter-title">Filter by Brand</div>
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
            Clear Filters ({filterCount})
          </button>
        )}
      </div>
    </>
  );
}
