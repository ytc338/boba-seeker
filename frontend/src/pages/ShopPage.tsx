import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import type { Shop } from '../types';
import { getShop } from '../services/api';
import { useFavorites } from '../hooks/useFavorites';
import ShopDetail from '../components/ShopDetail';
import Map from '../components/Map';
import './ShopPage.css';

export default function ShopPage() {
  const { id } = useParams<{ id: string }>();
  const [shop, setShop] = useState<Shop | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isFavorite, toggleFavorite } = useFavorites();
  const navigate = useNavigate();

  useEffect(() => {
    if (!id) return;

    const shopId = parseInt(id, 10);
    if (isNaN(shopId)) {
      setError('Invalid shop ID');
      setLoading(false);
      return;
    }

    getShop(shopId)
      .then((data) => {
        setShop(data);
        document.title = `${data.name} - Boba Seeker`;
      })
      .catch(() => {
        setError('Shop not found');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="shop-page">
        <div className="shop-page-loading">Loading...</div>
      </div>
    );
  }

  if (error || !shop) {
    return (
      <div className="shop-page">
        <div className="shop-page-error">
          <h2>{error || 'Shop not found'}</h2>
          <Link to="/" className="back-home">Back to map</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="shop-page">
      <div className="shop-page-map">
        <Map
          shops={[shop]}
          selectedShop={shop}
        />
      </div>
      <div className="shop-page-detail">
        <ShopDetail
          shop={shop}
          onBack={() => navigate('/')}
          backLabel="Back to map"
          isFavorite={isFavorite(shop.id)}
          onToggleFavorite={toggleFavorite}
        />
      </div>
    </div>
  );
}
