import { useState } from 'react';
import type { Shop } from '../types';
import DrinkRec from './DrinkRec';
import './ShopDetail.css';

interface ShopDetailProps {
  shop: Shop;
  onBack: () => void;
  backLabel?: string;
  isFavorite?: boolean;
  onToggleFavorite?: (shopId: number) => void;
}

function getGoogleMapsUrl(shop: Shop): string {
  if (shop.google_place_id) {
    return `https://www.google.com/maps/search/?api=1&query=Google&query_place_id=${shop.google_place_id}`;
  }
  const query = encodeURIComponent(`${shop.name} ${shop.address}`);
  return `https://www.google.com/maps/search/?api=1&query=${query}`;
}

function getDirectionsUrl(shop: Shop): string {
  if (shop.google_place_id) {
    return `https://www.google.com/maps/dir/?api=1&destination=Google&destination_place_id=${shop.google_place_id}`;
  }
  const dest = encodeURIComponent(`${shop.name} ${shop.address}`);
  return `https://www.google.com/maps/dir/?api=1&destination=${dest}`;
}

function getCountryLabel(country: string): string {
  switch (country) {
    case 'TW': return '🇹🇼 Taiwan';
    case 'SG': return '🇸🇬 Singapore';
    case 'US': return '🇺🇸 USA';
    default: return country;
  }
}

function parseHours(hours: string | undefined): string[] | null {
  if (!hours) return null;
  try {
    const parsed = JSON.parse(hours);
    if (Array.isArray(parsed)) return parsed;
    return null;
  } catch {
    return [hours];
  }
}

export default function ShopDetail({ shop, onBack, backLabel = 'Back to list', isFavorite, onToggleFavorite }: ShopDetailProps) {
  const hoursLines = parseHours(shop.hours);
  const [copied, setCopied] = useState(false);

  const handleShare = async () => {
    const url = `${window.location.origin}/shop/${shop.id}`;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback: select a temporary input
      const input = document.createElement('input');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="shop-detail">
      <div className="shop-detail-top-bar">
        <button className="shop-detail-back" onClick={onBack}>
          ← {backLabel}
        </button>
        <div className="shop-detail-top-actions">
          {onToggleFavorite && (
            <button
              className={`shop-detail-fav ${isFavorite ? 'is-fav' : ''}`}
              onClick={() => onToggleFavorite(shop.id)}
              title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              {isFavorite ? '♥' : '♡'}
            </button>
          )}
          <button className="shop-detail-share" onClick={handleShare}>
            {copied ? 'Copied!' : 'Share'}
          </button>
        </div>
      </div>

      {shop.photo_url && (
        <div className="shop-detail-photo">
          <img src={shop.photo_url} alt={shop.name} />
        </div>
      )}

      <div className="shop-detail-header">
        <h2 className="shop-detail-name">{shop.name}</h2>
        {shop.rating && (
          <div className="shop-detail-rating">
            <span className="star">★</span>
            <span>{shop.rating.toFixed(1)}</span>
            {shop.rating_count && (
              <span className="rating-count">({shop.rating_count} reviews)</span>
            )}
          </div>
        )}
      </div>

      <div className="shop-detail-meta">
        {shop.brand && (
          <span className="shop-detail-brand">{shop.brand.name}</span>
        )}
        <span className="shop-detail-country">{getCountryLabel(shop.country)}</span>
      </div>

      <div className="shop-detail-actions">
        <a
          href={getDirectionsUrl(shop)}
          target="_blank"
          rel="noopener noreferrer"
          className="shop-detail-directions"
        >
          Directions
        </a>
        <a
          href={getGoogleMapsUrl(shop)}
          target="_blank"
          rel="noopener noreferrer"
          className="shop-detail-gmaps"
        >
          View on Google Maps
        </a>
      </div>

      <div className="shop-detail-info">
        <div className="shop-detail-address">
          <span className="info-label">Address</span>
          <span>{shop.address}</span>
        </div>

        {shop.phone && (
          <div className="shop-detail-phone">
            <span className="info-label">Phone</span>
            <a href={`tel:${shop.phone}`}>{shop.phone}</a>
          </div>
        )}

        {hoursLines && (
          <div className="shop-detail-hours">
            <span className="info-label">Hours</span>
            <div className="hours-list">
              {hoursLines.map((line, i) => (
                <div key={i} className="hours-line">{line}</div>
              ))}
            </div>
          </div>
        )}
      </div>

      <DrinkRec brandName={shop.brand?.name} />
    </div>
  );
}
