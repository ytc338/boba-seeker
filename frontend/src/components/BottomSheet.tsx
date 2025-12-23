import { useState, useRef, useCallback, useEffect } from 'react';
import type { Shop } from '../types';
import ShopCard from './ShopCard';
import './BottomSheet.css';

type SheetState = 'collapsed' | 'peek' | 'expanded';

// Height values in vh for each state
const SHEET_HEIGHTS = {
  collapsed: 72, // pixels for collapsed (header only)
  peek: 25,      // vh for peek
  expanded: 55,  // vh for expanded
};

interface BottomSheetProps {
  shops: Shop[];
  selectedShop: Shop | null;
  onShopSelect: (shop: Shop) => void;
  loading: boolean;
  error: string | null;
  onHeightChange?: (height: number) => void;
}

export default function BottomSheet({
  shops,
  selectedShop,
  onShopSelect,
  loading,
  error,
  onHeightChange,
}: BottomSheetProps) {
  const [sheetState, setSheetState] = useState<SheetState>('peek');
  const sheetRef = useRef<HTMLDivElement>(null);
  const dragStartY = useRef<number>(0);
  const dragStartHeight = useRef<number>(0);
  const isDragging = useRef<boolean>(false);

  // Calculate and report current height
  useEffect(() => {
    if (!onHeightChange) return;
    
    const calculateHeight = () => {
      if (sheetState === 'collapsed') {
        onHeightChange(SHEET_HEIGHTS.collapsed);
      } else {
        const vh = window.innerHeight / 100;
        const heightVh = sheetState === 'peek' ? SHEET_HEIGHTS.peek : SHEET_HEIGHTS.expanded;
        onHeightChange(heightVh * vh);
      }
    };

    calculateHeight();
    window.addEventListener('resize', calculateHeight);
    return () => window.removeEventListener('resize', calculateHeight);
  }, [sheetState, onHeightChange]);

  // Get next state when tapping header
  const cycleState = useCallback(() => {
    setSheetState((prev) => {
      if (prev === 'collapsed') return 'peek';
      if (prev === 'peek') return 'expanded';
      return 'peek';
    });
  }, []);

  // Handle drag start
  const handleDragStart = useCallback((clientY: number) => {
    if (!sheetRef.current) return;
    isDragging.current = true;
    dragStartY.current = clientY;
    dragStartHeight.current = sheetRef.current.offsetHeight;
    sheetRef.current.style.transition = 'none';
  }, []);

  // Handle drag move
  const handleDragMove = useCallback((clientY: number) => {
    if (!isDragging.current || !sheetRef.current) return;
    
    const deltaY = dragStartY.current - clientY;
    const newHeight = Math.max(72, Math.min(window.innerHeight * 0.7, dragStartHeight.current + deltaY));
    sheetRef.current.style.maxHeight = `${newHeight}px`;
  }, []);

  // Handle drag end - snap to nearest state
  const handleDragEnd = useCallback(() => {
    if (!isDragging.current || !sheetRef.current) return;
    isDragging.current = false;
    
    const currentHeight = sheetRef.current.offsetHeight;
    const vh = window.innerHeight / 100;
    
    // Calculate thresholds
    const collapsedHeight = SHEET_HEIGHTS.collapsed;
    const peekHeight = SHEET_HEIGHTS.peek * vh;
    const expandedHeight = SHEET_HEIGHTS.expanded * vh;
    
    // Find nearest state
    const distances = {
      collapsed: Math.abs(currentHeight - collapsedHeight),
      peek: Math.abs(currentHeight - peekHeight),
      expanded: Math.abs(currentHeight - expandedHeight),
    };
    
    const nearestState = (Object.keys(distances) as SheetState[]).reduce((a, b) => 
      distances[a] < distances[b] ? a : b
    );
    
    // Reset inline style and let CSS handle the transition
    sheetRef.current.style.maxHeight = '';
    sheetRef.current.style.transition = '';
    setSheetState(nearestState);
  }, []);

  // Touch event handlers
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    handleDragStart(e.touches[0].clientY);
  }, [handleDragStart]);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    handleDragMove(e.touches[0].clientY);
  }, [handleDragMove]);

  const handleTouchEnd = useCallback(() => {
    handleDragEnd();
  }, [handleDragEnd]);

  // Mouse event handlers (for desktop testing)
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    handleDragStart(e.clientY);
    
    const handleMouseMove = (e: MouseEvent) => handleDragMove(e.clientY);
    const handleMouseUp = () => {
      handleDragEnd();
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [handleDragStart, handleDragMove, handleDragEnd]);

  // Auto-collapse when no shops
  const effectiveState = shops.length === 0 && !loading ? 'collapsed' : sheetState;

  return (
    <div
      ref={sheetRef}
      className={`bottom-sheet ${effectiveState}`}
    >
      <div 
        className="sheet-handle"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handleMouseDown}
        onClick={cycleState}
      >
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
