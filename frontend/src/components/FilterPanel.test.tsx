/**
 * Tests for FilterPanel component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import FilterPanel from './FilterPanel';
import type { Brand } from '../types';

// Sample test data
const mockBrands: Brand[] = [
  { id: 1, name: 'Gong Cha', name_zh: '貢茶', origin_country: 'TW' },
  { id: 2, name: 'Tiger Sugar', name_zh: '老虎堂', origin_country: 'TW' },
  { id: 3, name: 'Boba Guys', origin_country: 'US' },
  { id: 4, name: 'TP Tea', name_zh: '茶湯會', origin_country: 'TW' },
];

const defaultProps = {
  brands: mockBrands,
  selectedBrands: [],
  selectedRegion: '',
  onBrandToggle: vi.fn(),
  onRegionChange: vi.fn(),
  onClearFilters: vi.fn(),
};

describe('FilterPanel', () => {
  describe('Opening and closing', () => {
    it('is closed by default', () => {
      render(<FilterPanel {...defaultProps} />);
      // Filter panel should not have 'open' class
      const panel = document.querySelector('.filter-panel');
      expect(panel).not.toHaveClass('open');
    });

    it('opens when FAB is clicked', () => {
      render(<FilterPanel {...defaultProps} />);
      const fab = screen.getByRole('button', { name: /toggle filters/i });
      fireEvent.click(fab);
      
      const panel = document.querySelector('.filter-panel');
      expect(panel).toHaveClass('open');
    });

    it('closes when FAB is clicked again', () => {
      render(<FilterPanel {...defaultProps} />);
      const fab = screen.getByRole('button', { name: /toggle filters/i });
      
      fireEvent.click(fab); // Open
      fireEvent.click(fab); // Close
      
      const panel = document.querySelector('.filter-panel');
      expect(panel).not.toHaveClass('open');
    });
  });

  describe('Region selector', () => {
    it('renders all region options', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      expect(screen.getByText(/🌍 All/)).toBeInTheDocument();
      expect(screen.getByText(/🇹🇼 Taiwan/)).toBeInTheDocument();
      expect(screen.getByText(/🇸🇬 Singapore/)).toBeInTheDocument();
      expect(screen.getByText(/🇺🇸 USA/)).toBeInTheDocument();
    });

    it('calls onRegionChange when region is selected', () => {
      const onRegionChange = vi.fn();
      render(<FilterPanel {...defaultProps} onRegionChange={onRegionChange} />);
      
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));
      fireEvent.click(screen.getByText(/🇹🇼 Taiwan/));
      
      expect(onRegionChange).toHaveBeenCalledWith('TW');
    });

    it('highlights selected region', () => {
      render(<FilterPanel {...defaultProps} selectedRegion="TW" />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const taiwanBtn = screen.getByText(/🇹🇼 Taiwan/).closest('button');
      expect(taiwanBtn).toHaveClass('active');
    });
  });

  describe('Brand list', () => {
    it('renders brand names', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      expect(screen.getByText(/Gong Cha/)).toBeInTheDocument();
      expect(screen.getByText(/Tiger Sugar/)).toBeInTheDocument();
      expect(screen.getByText(/Boba Guys/)).toBeInTheDocument();
    });

    it('calls onBrandToggle when brand is clicked', () => {
      const onBrandToggle = vi.fn();
      render(<FilterPanel {...defaultProps} onBrandToggle={onBrandToggle} />);
      
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));
      fireEvent.click(screen.getByText(/Boba Guys/));
      
      expect(onBrandToggle).toHaveBeenCalledWith(3);
    });

    it('shows checkmark for selected brands', () => {
      render(<FilterPanel {...defaultProps} selectedBrands={[1, 2]} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const checkmarks = document.querySelectorAll('.checkmark');
      const checkedCount = Array.from(checkmarks).filter(el => el.textContent === '✓').length;
      expect(checkedCount).toBe(2);
    });

    it('handles empty brands list', () => {
      render(<FilterPanel {...defaultProps} brands={[]} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      expect(screen.getByText('No brands in this region')).toBeInTheDocument();
    });
  });

  describe('Brand search', () => {
    it('filters brands by search query', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const searchInput = screen.getByPlaceholderText('Search brands...');
      fireEvent.change(searchInput, { target: { value: 'gong' } });

      expect(screen.getByText(/Gong Cha/)).toBeInTheDocument();
      expect(screen.queryByText(/Tiger Sugar/)).not.toBeInTheDocument();
    });

    it('search is case insensitive', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const searchInput = screen.getByPlaceholderText('Search brands...');
      fireEvent.change(searchInput, { target: { value: 'GONG' } });

      expect(screen.getByText(/Gong Cha/)).toBeInTheDocument();
    });

    it('searches Chinese names', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const searchInput = screen.getByPlaceholderText('Search brands...');
      fireEvent.change(searchInput, { target: { value: '貢' } });

      expect(screen.getByText(/Gong Cha/)).toBeInTheDocument();
    });

    it('shows no matching brands message', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const searchInput = screen.getByPlaceholderText('Search brands...');
      fireEvent.change(searchInput, { target: { value: 'xyz123' } });

      expect(screen.getByText('No matching brands')).toBeInTheDocument();
    });

    it('clears search when clear button is clicked', () => {
      render(<FilterPanel {...defaultProps} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      const searchInput = screen.getByPlaceholderText('Search brands...');
      fireEvent.change(searchInput, { target: { value: 'gong' } });
      
      const clearBtn = screen.getByRole('button', { name: /clear search/i });
      fireEvent.click(clearBtn);

      expect(searchInput).toHaveValue('');
    });
  });

  describe('Clear filters', () => {
    it('shows clear button when brands are selected', () => {
      render(<FilterPanel {...defaultProps} selectedBrands={[1, 2]} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      expect(screen.getByText('Clear Filters (2)')).toBeInTheDocument();
    });

    it('hides clear button when no brands selected', () => {
      render(<FilterPanel {...defaultProps} selectedBrands={[]} />);
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));

      expect(screen.queryByText(/Clear Filters/)).not.toBeInTheDocument();
    });

    it('calls onClearFilters when clear button is clicked', () => {
      const onClearFilters = vi.fn();
      render(<FilterPanel {...defaultProps} selectedBrands={[1]} onClearFilters={onClearFilters} />);
      
      fireEvent.click(screen.getByRole('button', { name: /toggle filters/i }));
      fireEvent.click(screen.getByText(/Clear Filters/));
      
      expect(onClearFilters).toHaveBeenCalled();
    });
  });

  describe('Filter count badge', () => {
    it('shows badge with count when brands selected', () => {
      render(<FilterPanel {...defaultProps} selectedBrands={[1, 2, 3]} />);
      
      const badge = document.querySelector('.filter-badge');
      expect(badge).toHaveTextContent('3');
    });

    it('hides badge when no brands selected', () => {
      render(<FilterPanel {...defaultProps} selectedBrands={[]} />);
      
      const badge = document.querySelector('.filter-badge');
      expect(badge).not.toBeInTheDocument();
    });
  });
});
