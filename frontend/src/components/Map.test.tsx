/**
 * Tests for Map component.
 * Note: mapbox-gl is mocked in setup.ts since it requires WebGL.
 * When no VITE_MAPBOX_TOKEN is set, component shows an overlay.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import Map from './Map';
import type { Shop } from '../types';

// Sample test data
const mockShops: Shop[] = [
  {
    id: 1,
    name: 'Test Shop 1',
    address: '123 Test St',
    country: 'US',
    latitude: 37.7749,
    longitude: -122.4194,
  },
  {
    id: 2,
    name: 'Test Shop 2',
    address: '456 Market St',
    country: 'US',
    latitude: 37.7855,
    longitude: -122.4079,
  },
];

describe('Map', () => {
  describe('Rendering without Mapbox token', () => {
    // When no token is set, component shows overlay
    it('renders map wrapper container', () => {
      const { container } = render(<Map shops={[]} />);
      const wrapper = container.querySelector('.map-wrapper');
      expect(wrapper).toBeInTheDocument();
    });

    it('shows token required overlay when no token', () => {
      render(<Map shops={[]} />);
      expect(screen.getByText('🗺️ Map Preview')).toBeInTheDocument();
      expect(screen.getByText(/Add your Mapbox token/)).toBeInTheDocument();
    });

    it('renders without crashing with shops', () => {
      expect(() => {
        render(<Map shops={mockShops} />);
      }).not.toThrow();
    });

    it('renders without crashing with empty shops', () => {
      expect(() => {
        render(<Map shops={[]} />);
      }).not.toThrow();
    });

    it('renders the map div element', () => {
      const { container } = render(<Map shops={[]} />);
      const mapDiv = container.querySelector('.map');
      expect(mapDiv).toBeInTheDocument();
    });
  });

  describe('Props handling', () => {
    // These tests verify props are accepted without errors
    // (actual map behavior requires a real token and WebGL)
    
    it('accepts selectedShop prop', () => {
      const selectedShop = mockShops[0];
      expect(() => {
        render(<Map shops={mockShops} selectedShop={selectedShop} />);
      }).not.toThrow();
    });

    it('accepts onShopSelect callback', () => {
      const onShopSelect = vi.fn();
      expect(() => {
        render(<Map shops={mockShops} onShopSelect={onShopSelect} />);
      }).not.toThrow();
    });

    it('accepts onMapMove callback', () => {
      const onMapMove = vi.fn();
      expect(() => {
        render(<Map shops={mockShops} onMapMove={onMapMove} />);
      }).not.toThrow();
    });

    it('accepts bottomPadding prop', () => {
      expect(() => {
        render(<Map shops={[]} bottomPadding={200} />);
      }).not.toThrow();
    });

    it('accepts showSearchButton prop', () => {
      expect(() => {
        render(<Map shops={[]} showSearchButton={true} />);
      }).not.toThrow();
    });

    it('accepts onSearchClick callback', () => {
      const onSearchClick = vi.fn();
      expect(() => {
        render(<Map shops={[]} showSearchButton={true} onSearchClick={onSearchClick} />);
      }).not.toThrow();
    });

    it('accepts searchLoading prop', () => {
      expect(() => {
        render(<Map shops={[]} showSearchButton={true} searchLoading={true} />);
      }).not.toThrow();
    });
  });

  describe('Search button visibility', () => {
    // Note: Search button is only visible when mapboxgl.accessToken is set
    // Since our mock doesn't set the token, these verify behavior without token
    
    it('does not show search button without valid token', () => {
      render(<Map shops={[]} showSearchButton={true} />);
      expect(screen.queryByText('Search this area')).not.toBeInTheDocument();
    });

    it('does not show locate button without valid token', () => {
      render(<Map shops={[]} />);
      expect(screen.queryByText('◎')).not.toBeInTheDocument();
    });
  });
});

