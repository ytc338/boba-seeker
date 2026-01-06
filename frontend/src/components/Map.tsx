import { useRef, useEffect, useCallback, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import type { Shop } from '../types';
import './Map.css';

// Set token from environment
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || '';

// Default location: Taipei, Taiwan
const DEFAULT_CENTER: [number, number] = [121.5, 25.03];
const DEFAULT_ZOOM = 13;

interface MapBounds {
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
}

interface MapProps {
  shops: Shop[];
  selectedShop?: Shop | null;
  onShopSelect?: (shop: Shop) => void;
  onMapMove?: (bounds: MapBounds) => void;
  showSearchButton?: boolean;
  onSearchClick?: () => void;
  searchLoading?: boolean;
  bottomPadding?: number;
}

export default function Map({
  shops,
  selectedShop,
  onShopSelect,
  onMapMove,
  showSearchButton = false,
  onSearchClick,
  searchLoading = false,
  bottomPadding = 0,
}: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const userMarker = useRef<mapboxgl.Marker | null>(null);
  const popup = useRef<mapboxgl.Popup | null>(null);
  const [locating, setLocating] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const shopsRef = useRef<Shop[]>([]);
  const hasMovedRef = useRef(false);
  
  const onShopSelectRef = useRef(onShopSelect);
  const onMapMoveRef = useRef(onMapMove);
  
  useEffect(() => {
    onShopSelectRef.current = onShopSelect;
  }, [onShopSelect]);

  useEffect(() => {
    onMapMoveRef.current = onMapMove;
  }, [onMapMove]);

  useEffect(() => {
    shopsRef.current = shops;
  }, [shops]);

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    if (!mapboxgl.accessToken) {
      console.warn('Mapbox token not set. Add VITE_MAPBOX_TOKEN to .env');
      return;
    }

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current!,
        style: 'mapbox://styles/mapbox/light-v11',
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
      });

      // Note: NavigationControl (+/-) removed for cleaner UI

      map.current.on('load', () => {
        if (!map.current) return;

        // Add GeoJSON source for shops
        map.current.addSource('shops', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] },
        });

        // Simple circle markers
        map.current.addLayer({
          id: 'shop-markers',
          type: 'circle',
          source: 'shops',
          paint: {
            'circle-radius': 8,
            'circle-color': '#e91e63',
            'circle-stroke-width': 2,
            'circle-stroke-color': '#ffffff',
          },
        });

        // Highlight layer for selected marker
        map.current.addLayer({
          id: 'shop-markers-selected',
          type: 'circle',
          source: 'shops',
          paint: {
            'circle-radius': 12,
            'circle-color': '#c2185b',
            'circle-stroke-width': 3,
            'circle-stroke-color': '#ffffff',
          },
          filter: ['==', ['get', 'id'], -1],
        });

        // Click handler
        map.current.on('click', 'shop-markers', (e) => {
          if (!e.features?.[0]) return;
          const shopId = e.features[0].properties?.id;
          const shop = shopsRef.current.find((s) => s.id === shopId);
          if (shop && onShopSelectRef.current) {
            onShopSelectRef.current(shop);
          }
        });

        // Cursor on hover
        map.current.on('mouseenter', 'shop-markers', () => {
          if (map.current) map.current.getCanvas().style.cursor = 'pointer';
        });
        map.current.on('mouseleave', 'shop-markers', () => {
          if (map.current) map.current.getCanvas().style.cursor = '';
        });

        setMapReady(true);
      });

      // Track map movement for "Search This Area"
      map.current.on('moveend', () => {
        if (!map.current || !hasMovedRef.current) return;
        
        const bounds = map.current.getBounds();
        if (bounds && onMapMoveRef.current) {
          onMapMoveRef.current({
            minLat: bounds.getSouth(),
            maxLat: bounds.getNorth(),
            minLng: bounds.getWest(),
            maxLng: bounds.getEast(),
          });
        }
      });

      // Mark that user has moved the map (ignore initial load)
      map.current.on('dragstart', () => {
        hasMovedRef.current = true;
      });
      map.current.on('zoomstart', () => {
        hasMovedRef.current = true;
      });

      // Try to get user location on init
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            if (map.current) {
              map.current.flyTo({
                center: [position.coords.longitude, position.coords.latitude],
                zoom: DEFAULT_ZOOM,
                duration: 1500,
              });
            }
          },
          () => {
            console.log('Geolocation not available, using default center');
          },
          { enableHighAccuracy: true, timeout: 5000 }
        );
      }
    } catch (err) {
      console.error('Failed to initialize map:', err);
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Update shop markers
  useEffect(() => {
    if (!map.current || !mapReady) return;

    const source = map.current.getSource('shops') as mapboxgl.GeoJSONSource;
    if (!source) return;

    const geojson: GeoJSON.FeatureCollection = {
      type: 'FeatureCollection',
      features: shops.map((shop) => ({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [shop.longitude, shop.latitude],
        },
        properties: {
          id: shop.id,
          name: shop.name,
          address: shop.address,
          rating: shop.rating,
          brand_id: shop.brand_id || 0,
        },
      })),
    };

    source.setData(geojson);
  }, [shops, mapReady]);

  // Google Maps URL helper
  const getGoogleMapsUrl = useCallback((shop: Shop): string => {
    if (shop.google_place_id) {
      return `https://www.google.com/maps/search/?api=1&query=Google&query_place_id=${shop.google_place_id}`;
    }
    const query = encodeURIComponent(`${shop.name} ${shop.address}`);
    return `https://www.google.com/maps/search/?api=1&query=${query}`;
  }, []);

  // Update selected marker and show popup
  useEffect(() => {
    if (!map.current || !mapReady) return;

    map.current.setFilter('shop-markers-selected', [
      '==',
      ['get', 'id'],
      selectedShop?.id ?? -1,
    ]);

    if (popup.current) {
      popup.current.remove();
      popup.current = null;
    }

    if (selectedShop) {
      const mapsUrl = getGoogleMapsUrl(selectedShop);
      
      popup.current = new mapboxgl.Popup({ offset: 15, closeButton: true })
        .setLngLat([selectedShop.longitude, selectedShop.latitude])
        .setHTML(
          `<div class="marker-popup">
            <h4>${selectedShop.name}</h4>
            <p>${selectedShop.address}</p>
            ${selectedShop.rating ? `<p>★ ${selectedShop.rating.toFixed(1)}</p>` : ''}
            <a href="${mapsUrl}" target="_blank" rel="noopener noreferrer" class="marker-popup-link">
              View on Google Maps ↗
            </a>
          </div>`
        )
        .addTo(map.current);

      map.current.flyTo({
        center: [selectedShop.longitude, selectedShop.latitude],
        zoom: 15,
        duration: 1000,
        padding: { bottom: bottomPadding, top: 0, left: 0, right: 0 },
      });
    }
  }, [selectedShop, mapReady, getGoogleMapsUrl, bottomPadding]);

  // Locate user function
  const locateUser = useCallback(() => {
    if (!navigator.geolocation || !map.current) return;

    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;

        if (userMarker.current) {
          userMarker.current.remove();
        }

        const el = document.createElement('div');
        el.className = 'user-location-dot';

        userMarker.current = new mapboxgl.Marker({ element: el })
          .setLngLat([longitude, latitude])
          .addTo(map.current!);

        map.current!.flyTo({
          center: [longitude, latitude],
          zoom: DEFAULT_ZOOM,
          duration: 1500,
        });

        setLocating(false);
      },
      (error) => {
        console.error('Geolocation error:', error);
        setLocating(false);
        alert('Could not get your location.');
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, []);

  return (
    <div className="map-wrapper">
      {!mapboxgl.accessToken && (
        <div className="map-overlay">
          <div className="map-overlay-content">
            <h3>🗺️ Map Preview</h3>
            <p>Add your Mapbox token to .env:</p>
            <code>VITE_MAPBOX_TOKEN=your_token_here</code>
          </div>
        </div>
      )}
      <div ref={mapContainer} className="map" />

      {/* Search This Area Button */}
      {mapboxgl.accessToken && showSearchButton && (
        <button
          className="search-area-button"
          onClick={onSearchClick}
          disabled={searchLoading}
        >
          {searchLoading ? 'Searching...' : 'Search This Area'}
        </button>
      )}

      {/* Locate Me Button */}
      {mapboxgl.accessToken && (
        <button
          className="locate-button"
          onClick={locateUser}
          disabled={locating}
          title="Find my location"
        >
          {locating ? '...' : '◎'}
        </button>
      )}
    </div>
  );
}
