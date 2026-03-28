import { useState, useCallback } from 'react';

const STORAGE_KEY = 'boba-seeker-favorites';

function loadFavorites(): Set<number> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Set();
    const ids = JSON.parse(raw);
    if (Array.isArray(ids)) return new Set(ids);
    return new Set();
  } catch {
    return new Set();
  }
}

function saveFavorites(ids: Set<number>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]));
}

export function useFavorites() {
  const [favorites, setFavorites] = useState<Set<number>>(loadFavorites);

  const toggleFavorite = useCallback((shopId: number) => {
    setFavorites((prev) => {
      const next = new Set(prev);
      if (next.has(shopId)) {
        next.delete(shopId);
      } else {
        next.add(shopId);
      }
      saveFavorites(next);
      return next;
    });
  }, []);

  const isFavorite = useCallback((shopId: number) => {
    return favorites.has(shopId);
  }, [favorites]);

  return { favorites, toggleFavorite, isFavorite };
}
