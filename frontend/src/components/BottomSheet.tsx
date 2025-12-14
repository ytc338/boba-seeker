import { useState } from 'react';
import type { Shop } from '../types';
import ShopCard from './ShopCard';
import './BottomSheet.css';

interface BottomSheetProps {
  shops: Shop[];
  selectedShop: Shop | null;
  onShopSelect: (shop: Shop) => void;
  loading: boolean;
  error: string | null;
}

export default function BottomSheet({
  shops,
  selectedShop,
  onShopSelect,
  loading,
  error,
}: BottomSheetProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div
      className={`bottom-sheet ${isExpanded ? 'expanded' : ''} ${shops.length === 0 && !loading ? 'collapsed' : ''}`}
    >
      <div className="sheet-handle" onClick={toggleExpand}>
        <div className="handle-bar" />
        <div className="sheet-header">
          <span className="sheet-title">Boba Shops</span>
          <span className="shop-count">
            {loading ? 'Loading...' : `${shops.length} found`}
          </span>
        </div>
      </div>

      <div className="sheet-shop-list">
        {error && <div className="error">{error}</div>}

        {!loading && !error && shops.length === 0 && (
          <div className="empty">No shops found</div>
        )}

        {shops.map((shop) => (
          <ShopCard
            key={shop.id}
            shop={shop}
            isSelected={selectedShop?.id === shop.id}
            onClick={() => onShopSelect(shop)}
          />
        ))}
      </div>
    </div>
  );
}
