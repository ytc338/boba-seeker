import './DrinkRec.css';

interface DrinkRecProps {
  brandName?: string;
}

interface Drink {
  name: string;
  nameZh?: string;
  description: string;
  tier?: 'first-timer' | 'regular';
}

// Drink recommendations by brand, keyed by canonical brand name.
// Multiple keys can point to the same brand for alias matching.
const DRINK_RECS: Record<string, Drink[]> = {
  // === TAIWAN MAJORS ===
  'Wushiland Boba': [
    { name: 'Four Seasons Green Tea', nameZh: '四季春', description: 'Light, floral oolong - the signature order', tier: 'first-timer' },
    { name: 'Okinawa Milk Tea', nameZh: '沖繩黑糖奶茶', description: 'Rich brown sugar milk tea with pearls', tier: 'first-timer' },
    { name: 'Yakult Green Tea', nameZh: '養樂多綠茶', description: 'Sweet-tart probiotic kick, great iced', tier: 'regular' },
  ],
  'CoCo Fresh Tea & Juice': [
    { name: 'Panda Milk Tea', nameZh: '3Q奶茶', description: 'Milk tea with tapioca, pudding, and coconut jelly', tier: 'first-timer' },
    { name: 'Fresh Taro Milk', nameZh: '鮮芋牛奶', description: 'Creamy taro with real taro chunks', tier: 'first-timer' },
    { name: 'Passion Fruit Green Tea', nameZh: '百香果綠茶', description: 'Bright and tangy fruit tea, no milk', tier: 'regular' },
  ],
  '清心福全': [
    { name: 'Pearl Milk Tea', nameZh: '珍珠奶茶', description: 'The classic - done right with fresh pearls', tier: 'first-timer' },
    { name: 'Kumquat Lemon', nameZh: '金桔檸檬', description: 'Tart citrus refresher, very popular in summer', tier: 'regular' },
  ],
  '迷客夏': [
    { name: 'Fresh Milk Tea', nameZh: '珍珠紅茶拿鐵', description: 'Smooth black tea latte with real milk, not creamer', tier: 'first-timer' },
    { name: 'Dajia Taro Fresh Milk', nameZh: '大甲芋頭鮮奶', description: 'Famous taro from Dajia region, creamy and thick', tier: 'first-timer' },
    { name: 'Grape Fruit Green', nameZh: '葡萄柚綠', description: 'Real grapefruit pulp with green tea', tier: 'regular' },
  ],
  '珍煮丹': [
    { name: 'Brown Sugar Pearl Milk', nameZh: '黑糖珍珠鮮奶', description: 'The famous tiger stripe brown sugar boba', tier: 'first-timer' },
    { name: 'Dirty Brown Sugar Tea', nameZh: '髒髒珍珠鮮奶茶', description: 'Brown sugar layered with milk tea base', tier: 'regular' },
  ],
  '茶的魔手': [
    { name: 'Green Tea Latte', nameZh: '翡翠拿鐵', description: 'Fresh green tea with milk, light and clean', tier: 'first-timer' },
    { name: 'Lemon Aiyu', nameZh: '檸檬愛玉', description: 'Lemon with aiyu jelly - classic Taiwanese refresher', tier: 'regular' },
  ],
  '可不可熟成紅茶': [
    { name: 'Aged Black Tea Latte', nameZh: '熟成紅茶拿鐵', description: 'Their signature aged tea with fresh milk', tier: 'first-timer' },
    { name: 'Aged Oolong Latte', nameZh: '熟成烏龍拿鐵', description: 'Roasted oolong flavor, less sweet', tier: 'regular' },
  ],
  '麻古茶坊': [
    { name: 'Mango Smoothie', nameZh: '芒果牛奶冰沙', description: 'Real mango blended with fresh milk', tier: 'first-timer' },
    { name: 'Grape Fruit Green Tea', nameZh: '葡萄柚綠茶', description: 'Fresh grapefruit pulp in green tea base', tier: 'regular' },
  ],
  '龜記': [
    { name: 'Winter Melon Tea', nameZh: '冬瓜茶', description: 'Classic Taiwanese winter melon, caramel-sweet', tier: 'first-timer' },
    { name: 'Winter Melon Lemon', nameZh: '冬瓜檸檬', description: 'Sweet melon meets citrus tang', tier: 'regular' },
  ],
  '得正': [
    { name: 'Black Tea', nameZh: '紅茶', description: 'Simple, well-brewed black tea with clean flavor', tier: 'first-timer' },
    { name: 'Four Seasons Spring', nameZh: '四季春', description: 'Fragrant oolong, light and floral', tier: 'regular' },
  ],
  '一沐日': [
    { name: 'Fresh Milk Tea', nameZh: '鮮奶茶', description: 'Quality tea with farm-fresh milk', tier: 'first-timer' },
    { name: 'Oolong Milk Tea', nameZh: '烏龍鮮奶茶', description: 'Roasted oolong base, aromatic and smooth', tier: 'regular' },
  ],
  '五桐號': [
    { name: 'Tie Guan Yin Latte', nameZh: '鐵觀音拿鐵', description: 'Roasted Tie Guan Yin with fresh milk', tier: 'first-timer' },
    { name: 'Osmanthus Oolong', nameZh: '桂花烏龍', description: 'Floral osmanthus with oolong tea', tier: 'regular' },
  ],
  '八曜和茶': [
    { name: 'Japanese Hojicha Latte', nameZh: '焙茶拿鐵', description: 'Roasted Japanese green tea with milk', tier: 'first-timer' },
    { name: 'Matcha Latte', nameZh: '抹茶拿鐵', description: 'Rich matcha with fresh milk', tier: 'regular' },
  ],

  // === INTERNATIONAL CHAINS ===
  'Tiger Sugar': [
    { name: 'Brown Sugar Boba + Pearl Milk', nameZh: '黑糖波霸厚鮮奶', description: 'The iconic tiger stripe drink that started the trend', tier: 'first-timer' },
    { name: 'Brown Sugar Boba + Tea Latte', nameZh: '黑糖波霸鮮奶茶', description: 'Tiger stripes with a tea base - more balanced', tier: 'regular' },
    { name: 'Cream Mousse Brown Sugar', nameZh: '黑糖奶蓋', description: 'Add cream mousse topping for salt-sweet contrast', tier: 'regular' },
  ],
  'Gong Cha': [
    { name: 'Earl Grey Milk Tea', description: 'Fragrant bergamot milk tea, their bestseller', tier: 'first-timer' },
    { name: 'Dirty Brown Sugar Milk Tea', description: 'Caramelized brown sugar with fresh milk', tier: 'first-timer' },
    { name: 'Strawberry Yogurt', description: 'Fruit tea with yogurt base, refreshing', tier: 'regular' },
  ],
  'Kung Fu Tea': [
    { name: 'Kung Fu Milk Tea', description: 'Classic Hong Kong style milk tea, rich and bold', tier: 'first-timer' },
    { name: 'Taro Milk Tea', description: 'Creamy taro that is consistently good', tier: 'first-timer' },
    { name: 'Passion Fruit Green Tea', description: 'Tangy fruit tea, great for non-milk-tea drinkers', tier: 'regular' },
  ],
  'Sharetea': [
    { name: 'Classic Pearl Milk Tea', nameZh: '珍珠奶茶', description: 'Their flagship drink, reliable and creamy', tier: 'first-timer' },
    { name: 'Taro Milk Tea', nameZh: '芋頭奶茶', description: 'Smooth, sweet purple taro', tier: 'first-timer' },
    { name: 'Peach Oolong Tea', description: 'Fruity and fragrant, light option', tier: 'regular' },
  ],
  'The Alley': [
    { name: 'Deerioca Fresh Milk', nameZh: '鹿丸鮮奶', description: 'Signature tapioca pearls with fresh milk, brown sugar swirl', tier: 'first-timer' },
    { name: 'Royal No.9 Milk Tea', description: 'Premium black tea blend with creamer', tier: 'regular' },
  ],
  'Yi Fang Taiwan Fruit Tea': [
    { name: 'Pineapple Green Tea', nameZh: '鳳梨綠茶', description: 'Fresh pineapple juice with green tea, signature drink', tier: 'first-timer' },
    { name: 'Passion Fruit Green Tea', nameZh: '百香果綠茶', description: 'Real passion fruit seeds with green tea', tier: 'first-timer' },
    { name: 'Aiyu Lemon', nameZh: '愛玉檸檬', description: 'Taiwanese aiyu jelly with fresh lemon', tier: 'regular' },
  ],
  'Xing Fu Tang': [
    { name: 'Brown Sugar Boba Milk', nameZh: '黑糖珍珠鮮奶', description: 'Hand-stirred brown sugar pearls made fresh in-store', tier: 'first-timer' },
    { name: 'Taro Boba Milk', nameZh: '芋圓鮮奶', description: 'Taro with their signature brown sugar pearls', tier: 'regular' },
  ],
  'TP Tea': [
    { name: 'Tieguanyin Tea Latte', nameZh: '鐵觀音拿鐵', description: 'Roasted oolong with fresh milk - their star drink', tier: 'first-timer' },
    { name: 'Plum Oolong', nameZh: '梅の烏龍', description: 'Plum-infused oolong, tart and fragrant', tier: 'regular' },
  ],
  'Ten Ren': [
    { name: '913 King\'s Oolong Milk Tea', nameZh: '913茶王奶茶', description: 'Their iconic high-mountain oolong milk tea', tier: 'first-timer' },
    { name: 'Jasmine Green Milk Tea', nameZh: '茉香綠奶茶', description: 'Jasmine-scented green tea with milk', tier: 'regular' },
  ],
  'HEYTEA': [
    { name: 'Cheezo Green Tea', nameZh: '芝芝綠茶', description: 'Their signature - salted cheese foam over green tea', tier: 'first-timer' },
    { name: 'Mango Pomelo Sago', nameZh: '芒芒甘露', description: 'Mango, pomelo, and sago - tropical dessert drink', tier: 'first-timer' },
    { name: 'Cheezo Grape', nameZh: '芝芝葡萄', description: 'Cheese foam with real grape - viral hit', tier: 'regular' },
  ],
  'Chicha San Chen': [
    { name: 'Brown Sugar Pearl Milk', nameZh: '黑糖珍珠鮮奶', description: 'Their premium take on brown sugar boba', tier: 'first-timer' },
    { name: 'Jade Oolong Tea', nameZh: '翡翠烏龍', description: 'Light, fragrant jade oolong served cold', tier: 'regular' },
  ],
  'Happy Lemon': [
    { name: 'Rock Salt Cheese Tea', nameZh: '岩鹽芝士茶', description: 'Pioneers of cheese tea - salty foam over tea', tier: 'first-timer' },
    { name: 'Lemon Aiyu Green Tea', nameZh: '愛玉檸檬', description: 'Fresh lemon with aiyu jelly', tier: 'regular' },
  ],
  'Meet Fresh': [
    { name: 'Taro Ball', nameZh: '芋圓', description: 'Signature dessert with taro, sweet potato, and tapioca balls', tier: 'first-timer' },
    { name: 'Grass Jelly', nameZh: '仙草', description: 'Herbal jelly with toppings - traditional Taiwanese dessert', tier: 'regular' },
  ],

  // === SINGAPORE BRANDS ===
  'KOI Thé': [
    { name: 'Golden Oolong Macchiato', description: 'Their signature - oolong with milk foam cap', tier: 'first-timer' },
    { name: 'Hazelnut Pearl Milk Tea', description: 'Nutty milk tea with chewy pearls', tier: 'regular' },
  ],
  'LiHO Tea': [
    { name: 'Brown Sugar Pearl Milk', description: 'Singapore\'s take on brown sugar boba', tier: 'first-timer' },
    { name: 'Cheese Tea', description: 'Salted cheese foam over black tea', tier: 'regular' },
  ],
  'Nayuki': [
    { name: 'Supreme Cheese Strawberry', nameZh: '霸氣芝士草莓', description: 'Fresh strawberry with cheese foam - their signature', tier: 'first-timer' },
    { name: 'Mango Cheese Tea', nameZh: '芝士芒芒', description: 'Fresh mango with cheese foam on tea base', tier: 'regular' },
  ],
  'Chagee': [
    { name: 'Boya Bindung Latte', nameZh: '伯牙絕弦', description: 'Their viral drink - jasmine green tea latte', tier: 'first-timer' },
    { name: 'Light Oolong Tea', nameZh: '原葉鮮沏', description: 'Pure brewed oolong, no sugar', tier: 'regular' },
  ],
  'R&B Tea': [
    { name: 'Brown Sugar Pearl Fresh Milk', nameZh: '黑糖珍珠鮮奶', description: 'Flame-torched brown sugar with fresh milk', tier: 'first-timer' },
    { name: 'Cheese Fresh Milk Tea', description: 'Cheese foam on black tea latte', tier: 'regular' },
  ],
  'PlayMade': [
    { name: 'Earl Grey Milk Tea', description: 'Made with handmade pearls in various flavors', tier: 'first-timer' },
    { name: 'Pick Your Pearls', description: 'Choose from 8+ pearl flavors - strawberry, charcoal, etc.', tier: 'regular' },
  ],
  'Each A Cup': [
    { name: 'Pearl Milk Tea', description: 'Classic Singaporean-style boba, consistent quality', tier: 'first-timer' },
    { name: 'Aloe Vera Honey Lemon', description: 'Refreshing citrus with real aloe vera', tier: 'regular' },
  ],

  // === US REGIONAL ===
  '7 Leaves Cafe': [
    { name: 'Mung Bean Milk Tea', description: 'Vietnamese-inspired - earthy mung bean with milk tea', tier: 'first-timer' },
    { name: 'Taro Milk Tea', description: 'Creamy and purple, a fan favorite', tier: 'first-timer' },
    { name: 'Sea Cream Jasmine', description: 'Jasmine tea with salted cream foam', tier: 'regular' },
  ],
  'Sunright Tea Studio': [
    { name: 'Dong Ding Oolong Milk Tea', nameZh: '凍頂烏龍奶茶', description: 'Premium Taiwanese oolong with fresh milk', tier: 'first-timer' },
    { name: 'Dirty Boba', description: 'Brown sugar marble with fresh milk', tier: 'regular' },
  ],
  'Boba Guys': [
    { name: 'Classic Milk Tea', description: 'Organic loose-leaf tea with real milk, no powder', tier: 'first-timer' },
    { name: 'Strawberry Matcha Latte', description: 'Colorful and photogenic, tastes as good as it looks', tier: 'regular' },
  ],
  'Feng Cha Teahouse': [
    { name: 'Tiger Sugar Milk Tea', description: 'Brown sugar boba with fresh milk', tier: 'first-timer' },
    { name: 'Mango Sago', description: 'Real mango with sago pearls', tier: 'regular' },
  ],
  'Moge Tee': [
    { name: 'Mango Pomelo Sago', nameZh: '芒芒甘露', description: 'Fresh mango, pomelo, and coconut milk', tier: 'first-timer' },
    { name: 'Strawberry Jasmine Green Tea', description: 'Real strawberry with jasmine tea', tier: 'regular' },
  ],

  // === FALLBACK ===
  'default': [
    { name: 'Classic Pearl Milk Tea', nameZh: '珍珠奶茶', description: 'The original bubble tea - can\'t go wrong', tier: 'first-timer' },
    { name: 'Taro Milk Tea', nameZh: '芋頭奶茶', description: 'Creamy and slightly sweet purple taro', tier: 'first-timer' },
    { name: 'Brown Sugar Boba Milk', nameZh: '黑糖珍珠鮮奶', description: 'Caramelized brown sugar with fresh milk and pearls', tier: 'first-timer' },
    { name: 'Mango Green Tea', nameZh: '芒果綠', description: 'Fresh and fruity, great for non-milk-tea drinkers', tier: 'regular' },
    { name: 'Passion Fruit Green Tea', nameZh: '百香果綠茶', description: 'Tangy, tropical, and refreshing', tier: 'regular' },
  ],
};

// Alias map: maps alternate brand names to the canonical key in DRINK_RECS
const BRAND_ALIASES: Record<string, string> = {
  // Wushiland / 50嵐
  '50嵐': 'Wushiland Boba',
  '50 Lan': 'Wushiland Boba',
  'Wushiland': 'Wushiland Boba',
  // CoCo
  'CoCo': 'CoCo Fresh Tea & Juice',
  'CoCo都可': 'CoCo Fresh Tea & Juice',
  'Coco Fresh': 'CoCo Fresh Tea & Juice',
  // Milksha / 迷客夏
  'Milksha': '迷客夏',
  'MILKSHA': '迷客夏',
  // Yi Fang
  'Yi Fang': 'Yi Fang Taiwan Fruit Tea',
  'Yifang': 'Yi Fang Taiwan Fruit Tea',
  '一芳': 'Yi Fang Taiwan Fruit Tea',
  // KEBUKE / 可不可
  'KEBUKE': '可不可熟成紅茶',
  '可不可': '可不可熟成紅茶',
  // KOI
  'KOI': 'KOI Thé',
  'KOI The': 'KOI Thé',
  // Gong Cha
  '貢茶': 'Gong Cha',
  'GongCha': 'Gong Cha',
  // Sharetea
  'Share Tea': 'Sharetea',
  '歇腳亭': 'Sharetea',
  // The Alley
  '鹿角巷': 'The Alley',
  // Tiger Sugar
  '老虎堂': 'Tiger Sugar',
  // Xing Fu Tang
  '幸福堂': 'Xing Fu Tang',
  // TP Tea
  'TP TEA': 'TP Tea',
  '茶湯會': 'TP Tea',
  // Ten Ren
  "Ten Ren's Tea": 'Ten Ren',
  '天仁': 'Ten Ren',
  '天仁茗茶': 'Ten Ren',
  // HEYTEA
  'Hey Tea': 'HEYTEA',
  '喜茶': 'HEYTEA',
  // Chicha San Chen
  'ChiCha': 'Chicha San Chen',
  '吃茶三千': 'Chicha San Chen',
  // Happy Lemon
  '快樂檸檬': 'Happy Lemon',
  // Meet Fresh
  '鮮芋仙': 'Meet Fresh',
  // Nayuki
  '奈雪的茶': 'Nayuki',
  '奈雪': 'Nayuki',
  // Chagee
  '霸王茶姬': 'Chagee',
  'CHAGEE': 'Chagee',
  // R&B Tea
  'R&B': 'R&B Tea',
  'R&B巡茶': 'R&B Tea',
  // Each A Cup
  'Each-A-Cup': 'Each A Cup',
  '各一杯': 'Each A Cup',
  // Sunright
  'Sunright': 'Sunright Tea Studio',
  'Sunright Tea': 'Sunright Tea Studio',
  '日青良月': 'Sunright Tea Studio',
  // Feng Cha
  'Feng Cha': 'Feng Cha Teahouse',
  '奉茶': 'Feng Cha Teahouse',
  // Moge Tee
  'Moge': 'Moge Tee',
  '愿茶': 'Moge Tee',
  // 7 Leaves
  '7 Leaves': '7 Leaves Cafe',
  'Seven Leaves': '7 Leaves Cafe',
};

function lookupDrinks(brandName?: string): Drink[] {
  if (!brandName) return DRINK_RECS['default'];

  // Direct match
  if (DRINK_RECS[brandName]) return DRINK_RECS[brandName];

  // Alias match
  const canonical = BRAND_ALIASES[brandName];
  if (canonical && DRINK_RECS[canonical]) return DRINK_RECS[canonical];

  return DRINK_RECS['default'];
}

export default function DrinkRec({ brandName }: DrinkRecProps) {
  const drinks = lookupDrinks(brandName);
  const hasMatch = brandName && drinks !== DRINK_RECS['default'];

  const firstTimerDrinks = drinks.filter(d => d.tier === 'first-timer');
  const regularDrinks = drinks.filter(d => d.tier === 'regular');
  // If no tiers assigned, show all as one group
  const ungrouped = drinks.filter(d => !d.tier);

  return (
    <div className="drink-rec">
      <h3 className="drink-rec-title">
        {hasMatch ? `What to Order at ${brandName}` : 'Popular Boba Drinks'}
      </h3>

      {firstTimerDrinks.length > 0 && (
        <div className="drink-tier">
          <span className="drink-tier-label">Start here</span>
          <div className="drink-list">
            {firstTimerDrinks.map((drink, i) => (
              <DrinkItem key={i} drink={drink} />
            ))}
          </div>
        </div>
      )}

      {regularDrinks.length > 0 && (
        <div className="drink-tier">
          <span className="drink-tier-label">For regulars</span>
          <div className="drink-list">
            {regularDrinks.map((drink, i) => (
              <DrinkItem key={i} drink={drink} />
            ))}
          </div>
        </div>
      )}

      {ungrouped.length > 0 && (
        <div className="drink-list">
          {ungrouped.map((drink, i) => (
            <DrinkItem key={i} drink={drink} />
          ))}
        </div>
      )}
    </div>
  );
}

function DrinkItem({ drink }: { drink: Drink }) {
  return (
    <div className="drink-item">
      <div className="drink-name">
        {drink.name}
        {drink.nameZh && <span className="drink-name-zh">{drink.nameZh}</span>}
      </div>
      <p className="drink-description">{drink.description}</p>
    </div>
  );
}
