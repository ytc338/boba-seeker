import type { Shop } from '../types';

const CARD_WIDTH = 1200;
const CARD_HEIGHT = 630;

export async function generateShareCard(shop: Shop): Promise<Blob> {
  const canvas = document.createElement('canvas');
  canvas.width = CARD_WIDTH;
  canvas.height = CARD_HEIGHT;
  const ctx = canvas.getContext('2d')!;

  // Background gradient
  const gradient = ctx.createLinearGradient(0, 0, CARD_WIDTH, CARD_HEIGHT);
  gradient.addColorStop(0, '#FFF5E6');
  gradient.addColorStop(0.5, '#FFE8D6');
  gradient.addColorStop(1, '#FFD6BA');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  // Decorative circles
  ctx.globalAlpha = 0.08;
  ctx.fillStyle = '#FF6B6B';
  ctx.beginPath();
  ctx.arc(CARD_WIDTH - 100, 100, 200, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(100, CARD_HEIGHT - 80, 150, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalAlpha = 1;

  // Tagline at top
  ctx.font = 'bold 28px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.fillStyle = '#E85D5D';
  ctx.textAlign = 'center';
  ctx.fillText('Boba Seeker picked this for me!', CARD_WIDTH / 2, 80);

  // Boba icon
  ctx.font = '80px serif';
  ctx.fillText('🧋', CARD_WIDTH / 2, 200);

  // Shop name
  ctx.font = 'bold 48px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.fillStyle = '#2C2420';
  const shopName = truncateText(ctx, shop.name, CARD_WIDTH - 120);
  ctx.fillText(shopName, CARD_WIDTH / 2, 300);

  // Brand name
  if (shop.brand?.name) {
    ctx.font = '32px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = '#8B7355';
    ctx.fillText(shop.brand.name, CARD_WIDTH / 2, 355);
  }

  // Rating
  if (shop.rating) {
    ctx.font = '28px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = '#E8A317';
    const stars = '★'.repeat(Math.round(shop.rating));
    ctx.fillText(`${stars} ${shop.rating.toFixed(1)}`, CARD_WIDTH / 2, 410);
  }

  // Location
  const location = [shop.city, shop.country === 'TW' ? 'Taiwan' : shop.country === 'SG' ? 'Singapore' : 'USA']
    .filter(Boolean).join(', ');
  if (location) {
    ctx.font = '24px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = '#8B7355';
    ctx.fillText(location, CARD_WIDTH / 2, 460);
  }

  // Footer branding
  ctx.font = '20px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.fillStyle = '#B8A08A';
  ctx.fillText('bobaseeker.com', CARD_WIDTH / 2, CARD_HEIGHT - 40);

  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) resolve(blob);
      else reject(new Error('Failed to generate share card'));
    }, 'image/png');
  });
}

function truncateText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string {
  if (ctx.measureText(text).width <= maxWidth) return text;
  let truncated = text;
  while (ctx.measureText(truncated + '...').width > maxWidth && truncated.length > 0) {
    truncated = truncated.slice(0, -1);
  }
  return truncated + '...';
}
