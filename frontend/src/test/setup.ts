/**
 * Vitest test setup file.
 * Configures jest-dom matchers and mocks for external dependencies.
 */

import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';

// Mock mapbox-gl since it requires WebGL
vi.mock('mapbox-gl', () => ({
  default: {
    Map: vi.fn(() => ({
      on: vi.fn(),
      off: vi.fn(),
      remove: vi.fn(),
      addControl: vi.fn(),
      removeControl: vi.fn(),
      getCenter: vi.fn(() => ({ lng: 121.5, lat: 25.03 })),
      getZoom: vi.fn(() => 13),
      getBounds: vi.fn(() => ({
        getNorth: vi.fn(() => 25.1),
        getSouth: vi.fn(() => 24.9),
        getEast: vi.fn(() => 121.6),
        getWest: vi.fn(() => 121.4),
      })),
      setCenter: vi.fn(),
      setZoom: vi.fn(),
      flyTo: vi.fn(),
      resize: vi.fn(),
      getCanvas: vi.fn(() => ({
        style: {},
      })),
      getContainer: vi.fn(() => document.createElement('div')),
      loaded: vi.fn(() => true),
    })),
    Marker: vi.fn(() => ({
      setLngLat: vi.fn().mockReturnThis(),
      setPopup: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
      remove: vi.fn(),
      getElement: vi.fn(() => document.createElement('div')),
    })),
    Popup: vi.fn(() => ({
      setLngLat: vi.fn().mockReturnThis(),
      setHTML: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
      remove: vi.fn(),
    })),
    NavigationControl: vi.fn(),
    GeolocateControl: vi.fn(),
    accessToken: '',
  },
  Map: vi.fn(),
  Marker: vi.fn(),
  Popup: vi.fn(),
  NavigationControl: vi.fn(),
  GeolocateControl: vi.fn(),
}));

// Mock window.matchMedia for responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
  root: null,
  rootMargin: '',
  thresholds: [],
}));
