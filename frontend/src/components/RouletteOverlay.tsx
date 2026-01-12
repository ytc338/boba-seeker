import './RouletteOverlay.css';

interface RouletteOverlayProps {
  currentShopName?: string;
  isSpinning: boolean;
}

export default function RouletteOverlay({ currentShopName, isSpinning }: RouletteOverlayProps) {
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
