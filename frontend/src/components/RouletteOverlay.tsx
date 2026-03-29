import type { Shop } from '../types';
import './RouletteOverlay.css';

interface RouletteOverlayProps {
  currentShopName?: string;
  isSpinning: boolean;
  winner?: Shop | null;
  onShare?: (shop: Shop) => void;
  onDismiss?: () => void;
  onClose?: () => void;
}

export default function RouletteOverlay({
  currentShopName,
  isSpinning,
  winner,
  onShare,
  onDismiss,
  onClose,
}: RouletteOverlayProps) {
  // Show result card after spin completes
  if (!isSpinning && winner) {
    return (
      <div className="roulette-overlay roulette-result">
        <button className="roulette-close" onClick={onClose ?? onDismiss}>×</button>
        <span className="roulette-result-icon">🎉</span>
        <span className="roulette-result-name">{winner.name}</span>
        {winner.brand?.name && (
          <span className="roulette-result-brand">{winner.brand.name}</span>
        )}
        <div className="roulette-actions">
          <button className="roulette-share-btn" onClick={() => onShare?.(winner)}>
            Share Pick
          </button>
          <button className="roulette-view-btn" onClick={onDismiss}>
            View Shop
          </button>
        </div>
      </div>
    );
  }

  if (!isSpinning) return null;

  return (
    <div className="roulette-overlay">
      <span className="roulette-icon">🎲</span>
      <span className="roulette-label">Picking...</span>
      <span className="roulette-shop-name changing">
        {currentShopName || '...'}
      </span>
    </div>
  );
}
