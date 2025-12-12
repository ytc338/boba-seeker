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

export interface MapBounds {
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
}

interface MapProps {
  shops: Shop[];
  selectedShop?: Shop | null;
  onShopSelect?: (shop: Shop) => void;
  onBoundsChange?: (bounds: MapBounds) => void;
  showSearchButton?: boolean;
  onSearchClick?: () => void;
  searchLoading?: boolean;
}

export default function Map({
  shops,
  selectedShop,
  onShopSelect,
  onBoundsChange,
  showSearchButton = false,
  onSearchClick,
  searchLoading = false,
}: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const userMarker = useRef<mapboxgl.Marker | null>(null);
  const popup = useRef<mapboxgl.Popup | null>(null);
  const [locating, setLocating] = useState(false);
  const [mapReady, setMapReady] = useState(false);
  const shopsRef = useRef<Shop[]>([]);
  const userHasInteracted = useRef(false);
  
  // Store callbacks in refs so useEffect doesn't depend on them
  const onBoundsChangeRef = useRef(onBoundsChange);
  const onShopSelectRef = useRef(onShopSelect);
  
  // Keep refs updated
  useEffect(() => {
    onBoundsChangeRef.current = onBoundsChange;
  }, [onBoundsChange]);
  
  useEffect(() => {
    onShopSelectRef.current = onShopSelect;
  }, [onShopSelect]);

  // Keep shops ref updated for click handler
  useEffect(() => {
    shopsRef.current = shops;
  }, [shops]);

  // Get current map bounds
  const getBounds = useCallback((): MapBounds | null => {
    if (!map.current) return null;
    const bounds = map.current.getBounds();
    if (!bounds) return null;
    return {
      minLat: bounds.getSouth(),
      maxLat: bounds.getNorth(),
      minLng: bounds.getWest(),
      maxLng: bounds.getEast(),
    };
  }, []);

  // Initialize map with geolocation
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    if (!mapboxgl.accessToken) {
      console.warn('Mapbox token not set. Add VITE_MAPBOX_TOKEN to .env');
      return;
    }

    // Initialize map immediately at default center
    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current!,
        style: 'mapbox://styles/mapbox/light-v11',
        center: DEFAULT_CENTER,
        zoom: DEFAULT_ZOOM,
      });

      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

      map.current.on('load', () => {
        if (!map.current) return;

        // Load boba SVG icon
        const img = new Image();
        img.onload = () => {
          if (!map.current) return;

          // Add image to map
          if (!map.current.hasImage('boba-marker')) {
            map.current.addImage('boba-marker', img);
          }

          // Add GeoJSON source for shops
          map.current.addSource('shops', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: [] },
          });

          // Add symbol layer for boba markers
          map.current.addLayer({
            id: 'shop-markers',
            type: 'symbol',
            source: 'shops',
            layout: {
              'icon-image': 'boba-marker',
              'icon-size': 0.8,
              'icon-anchor': 'bottom',
              'icon-allow-overlap': true,
            },
          });

          // Highlight layer for selected marker (slightly larger)
          map.current.addLayer({
            id: 'shop-markers-selected',
            type: 'symbol',
            source: 'shops',
            layout: {
              'icon-image': 'boba-marker',
              'icon-size': 1.0,
              'icon-anchor': 'bottom',
              'icon-allow-overlap': true,
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

          // Initial bounds
          const bounds = getBounds();
          if (bounds && onBoundsChangeRef.current) {
            onBoundsChangeRef.current(bounds);
          }
        };
        img.src = '/boba-marker.svg';
      });

      map.current.on('moveend', () => {
        const bounds = getBounds();
        if (bounds && onBoundsChangeRef.current) {
          onBoundsChangeRef.current(bounds);
        }
      });

      // Try to get user location and fly there (non-blocking)
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            
            // Only fly if user hasn't interacted yet and we still have a map
            if (map.current && !userHasInteracted.current) {
              map.current.flyTo({
                center: [longitude, latitude],
                zoom: DEFAULT_ZOOM,
                duration: 1500,
              });

              // Add user marker
              const el = document.createElement('div');
              el.className = 'user-marker';
              el.innerHTML = '📍';

              userMarker.current = new mapboxgl.Marker({
                element: el,
                anchor: 'bottom',
              })
                .setLngLat([longitude, latitude])
                .addTo(map.current);
            }
          },
          () => {
            // User denied or error - stay at default center
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
  }, [getBounds]); // Only depend on getBounds (stable)

  // Update shop markers (GeoJSON data)
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
        },
      })),
    };

    source.setData(geojson);
  }, [shops, mapReady]);

  // Update selected marker highlight and show popup
  useEffect(() => {
    if (!map.current || !mapReady) return;

    // Update filter for selected layer
    map.current.setFilter('shop-markers-selected', [
      '==',
      ['get', 'id'],
      selectedShop?.id ?? -1,
    ]);

    // Remove old popup
    if (popup.current) {
      popup.current.remove();
      popup.current = null;
    }

    // Add popup for selected shop
    if (selectedShop) {
      popup.current = new mapboxgl.Popup({ offset: 25, closeButton: true })
        .setLngLat([selectedShop.longitude, selectedShop.latitude])
        .setHTML(
          `<div class="marker-popup">
            <h4>${selectedShop.name}</h4>
            <p>${selectedShop.address}</p>
            ${selectedShop.rating ? `<p>★ ${selectedShop.rating.toFixed(1)}</p>` : ''}
          </div>`
        )
        .addTo(map.current);

      map.current.flyTo({
        center: [selectedShop.longitude, selectedShop.latitude],
        zoom: 15,
        duration: 1000,
      });
    }
  }, [selectedShop, mapReady]);

  // Locate user
  const locateUser = () => {
    if (!navigator.geolocation || !map.current) return;

    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;

        if (userMarker.current) {
          userMarker.current.remove();
        }

        const el = document.createElement('div');
        el.className = 'user-marker';
        el.innerHTML = '📍';

        userMarker.current = new mapboxgl.Marker({
          element: el,
          anchor: 'bottom',
        })
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
  };

  return (
    <div className="map-container">
      {!mapboxgl.accessToken && (
        <div className="map-overlay">
          <div className="map-overlay-content">
            <h3>🗺️ Map Preview</h3>
            <p>Add your Mapbox token to .env to see the map:</p>
            <code>VITE_MAPBOX_TOKEN=your_token_here</code>
          </div>
        </div>
      )}
      <div ref={mapContainer} className="map" />

      {/* Search This Area Button */}
      {mapboxgl.accessToken && mapReady && showSearchButton && (
        <button
          className="search-area-button"
          onClick={(e) => {
            e.stopPropagation();
            e.preventDefault();
            userHasInteracted.current = true;
            onSearchClick?.();
          }}
          disabled={searchLoading}
        >
          {searchLoading ? '🔄 Searching...' : '🔍 Search This Area'}
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
          {locating ? '⏳' : '📍'}
        </button>
      )}
    </div>
  );
}
