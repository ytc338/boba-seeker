/**
 * Tests for ShopCard component.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ShopCard from './ShopCard';
import type { Shop, Brand } from '../types';

// Sample test data
const mockBrand: Brand = {
  id: 1,
  name: 'Gong Cha',
  name_zh: '貢茶',
  origin_country: 'TW',
};

const mockShop: Shop = {
  id: 1,
  name: 'Gong Cha SF Downtown',
  brand_id: 1,
  address: '123 Market St, San Francisco, CA 94102',
  city: 'San Francisco',
  country: 'US',
  latitude: 37.7749,
  longitude: -122.4194,
  rating: 4.5,
  rating_count: 250,
  brand: mockBrand,
};

const mockShopMinimal: Shop = {
  id: 2,
  name: 'Independent Boba Shop',
  address: '456 Main St, Oakland, CA',
  country: 'US',
  latitude: 37.8044,
  longitude: -122.2712,
};

describe('ShopCard', () => {
  describe('Rendering', () => {
    it('renders shop name', () => {
      render(<ShopCard shop={mockShop} />);
      expect(screen.getByText('Gong Cha SF Downtown')).toBeInTheDocument();
    });

    it('renders shop address', () => {
      render(<ShopCard shop={mockShop} />);
      expect(screen.getByText('123 Market St, San Francisco, CA 94102')).toBeInTheDocument();
    });

    it('renders brand name when available', () => {
      render(<ShopCard shop={mockShop} />);
      expect(screen.getByText('Gong Cha')).toBeInTheDocument();
    });

    it('handles missing brand gracefully', () => {
      render(<ShopCard shop={mockShopMinimal} />);
      expect(screen.getByText('Independent Boba Shop')).toBeInTheDocument();
      expect(screen.queryByText('Gong Cha')).not.toBeInTheDocument();
    });

    it('renders rating when available', () => {
      render(<ShopCard shop={mockShop} />);
      expect(screen.getByText('4.5')).toBeInTheDocument();
      expect(screen.getByText('(250)')).toBeInTheDocument();
    });

    it('handles missing rating gracefully', () => {
      render(<ShopCard shop={mockShopMinimal} />);
      expect(screen.queryByText('★')).not.toBeInTheDocument();
    });

    it('displays US country flag', () => {
      render(<ShopCard shop={mockShop} />);
      expect(screen.getByText('🇺🇸 USA')).toBeInTheDocument();
    });

    it('displays Taiwan country flag for TW shops', () => {
      const twShop = { ...mockShop, country: 'TW' };
      render(<ShopCard shop={twShop} />);
      expect(screen.getByText('🇹🇼 Taiwan')).toBeInTheDocument();
    });
  });

  describe('Selection state', () => {
    it('does not have selected class by default', () => {
      const { container } = render(<ShopCard shop={mockShop} />);
      expect(container.firstChild).not.toHaveClass('selected');
    });

    it('has selected class when isSelected is true', () => {
      const { container } = render(<ShopCard shop={mockShop} isSelected={true} />);
      expect(container.firstChild).toHaveClass('selected');
    });
  });

  describe('Click handling', () => {
    it('calls onClick when clicked', () => {
      const handleClick = vi.fn();
      render(<ShopCard shop={mockShop} onClick={handleClick} />);
      
      fireEvent.click(screen.getByText('Gong Cha SF Downtown'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('does not error when onClick is not provided', () => {
      render(<ShopCard shop={mockShop} />);
      expect(() => {
        fireEvent.click(screen.getByText('Gong Cha SF Downtown'));
      }).not.toThrow();
    });
  });
});
