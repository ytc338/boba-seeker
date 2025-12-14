import './DrinkRec.css';

interface DrinkRecProps {
  brandName?: string;
}

// Drink recommendations by brand
const DRINK_RECS: Record<string, { name: string; nameZh?: string; description: string }[]> = {
  '50嵐': [
    { name: 'Four Seasons Green Tea', nameZh: '四季春', description: 'Light, floral green tea - the signature drink' },
    { name: 'Okinawa Milk Tea', nameZh: '沖繩黑糖奶茶', description: 'Rich brown sugar milk tea' },
  ],
  'CoCo': [
    { name: 'Panda Milk Tea', nameZh: '3Q奶茶', description: 'Milk tea with tapioca, pudding, and coconut jelly' },
    { name: 'Fresh Taro Milk', nameZh: '鮮芋牛奶', description: 'Creamy taro with real taro chunks' },
  ],
  '珍煮丹': [
    { name: 'Brown Sugar Pearl Milk', nameZh: '黑糖珍珠鮮奶', description: 'Famous tiger stripe brown sugar boba' },
    { name: 'Dirty Brown Sugar', nameZh: '髒髒珍珠鮮奶茶', description: 'Brown sugar with milk tea base' },
  ],
  '迷客夏': [
    { name: 'Velvet Fresh Milk Tea', nameZh: '珍珠紅茶拿鐵', description: 'Smooth milk tea with fresh milk' },
    { name: 'Taro Delight', nameZh: '大甲芋頭鮮奶', description: 'Fresh taro from Dajia region' },
  ],
  'Tiger Sugar': [
    { name: 'Brown Sugar Boba', nameZh: '黑糖波霸厚鮮奶', description: 'The iconic tiger stripe drink' },
    { name: 'Cream Mousse', nameZh: '奶蓋', description: 'Add cream mousse topping for extra richness' },
  ],
  'Kung Fu Tea': [
    { name: 'Kung Fu Milk Tea', description: 'Classic Hong Kong style milk tea' },
    { name: 'Mango Green Tea', description: 'Refreshing mango with green tea base' },
  ],
  'default': [
    { name: 'Classic Pearl Milk Tea', nameZh: '珍珠奶茶', description: 'The original bubble tea - can\'t go wrong!' },
    { name: 'Taro Milk Tea', nameZh: '芋頭奶茶', description: 'Creamy and slightly sweet purple taro' },
    { name: 'Mango Green Tea', nameZh: '芒果綠', description: 'Fresh and fruity summer favorite' },
  ],
};

export default function DrinkRec({ brandName }: DrinkRecProps) {
  const drinks = brandName && DRINK_RECS[brandName] 
    ? DRINK_RECS[brandName] 
    : DRINK_RECS['default'];

  return (
    <div className="drink-rec">
      <h3 className="drink-rec-title">
        🧋 {brandName ? `${brandName} Picks` : 'Popular Drinks'}
      </h3>
      <div className="drink-list">
        {drinks.map((drink, index) => (
          <div key={index} className="drink-item">
            <div className="drink-name">
              {drink.name}
              {drink.nameZh && <span className="drink-name-zh">{drink.nameZh}</span>}
            </div>
            <p className="drink-description">{drink.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
