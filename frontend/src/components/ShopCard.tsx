import type { Shop } from '../types';
import './ShopCard.css';

interface ShopCardProps {
  shop: Shop;
  isSelected?: boolean;
  onClick?: () => void;
}

export default function ShopCard({ shop, isSelected, onClick }: ShopCardProps) {
  return (
    <div
      className={`shop-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      <div className="shop-card-header">
        <h3 className="shop-name">{shop.name}</h3>
        {shop.rating && (
          <div className="shop-rating">
            <span className="star">★</span>
            <span>{shop.rating.toFixed(1)}</span>
            {shop.rating_count && (
              <span className="rating-count">({shop.rating_count})</span>
            )}
          </div>
        )}
      </div>
      
      <p className="shop-address">{shop.address}</p>
      
      <div className="shop-meta">
        {shop.brand && (
          <span className="shop-brand">{shop.brand.name}</span>
        )}
        <span className="shop-country">
          {shop.country === 'TW' ? '🇹🇼 Taiwan' : '🇺🇸 USA'}
        </span>
      </div>
    </div>
  );
}
