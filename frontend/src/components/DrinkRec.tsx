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
    { name: 'Boba Milk Tea', nameZh: '波霸奶茶', description: 'Their #1 best seller - classic milk tea with large pearls', tier: 'first-timer' },
    { name: 'Four Seasons Green Tea', nameZh: '四季春', description: 'Light, floral oolong - a top 10 staple', tier: 'first-timer' },
    { name: 'Ice Cream Black Tea', nameZh: '冰淇淋紅茶', description: 'Creamy black tea, their #2 best seller', tier: 'regular' },
    { name: 'Yakult Green Tea', nameZh: '多多綠茶', description: 'Sweet-tart probiotic kick, great iced', tier: 'regular' },
  ],
  'CoCo Fresh Tea & Juice': [
    { name: '3 Guys Milk Tea', nameZh: '3Q奶茶', description: 'Milk tea with tapioca, pudding, and coconut jelly', tier: 'first-timer' },
    { name: 'Brown Sugar Pearl Latte', nameZh: '黑糖珍珠拿鐵', description: 'Caramelized brown sugar with fresh milk and pearls', tier: 'first-timer' },
    { name: 'Passion Fruit Green Tea', nameZh: '百香果綠茶', description: 'Bright and tangy fruit tea, no milk', tier: 'regular' },
  ],
  '清心福全': [
    { name: 'Yakult Green Tea', nameZh: '優多綠茶', description: 'Their actual #1 best seller - probiotic meets green tea', tier: 'first-timer' },
    { name: 'Pearl Milk Tea', nameZh: '珍珠奶茶', description: 'The classic - done right with fresh pearls', tier: 'first-timer' },
    { name: 'Kumquat Lemon', nameZh: '金桔檸檬', description: 'Tart citrus refresher, very popular in summer', tier: 'regular' },
    { name: 'Oolong Green Tea', nameZh: '烏龍綠茶', description: 'Their signature oolong-green blend', tier: 'regular' },
  ],
  '迷客夏': [
    { name: 'Pearl Black Tea Latte', nameZh: '珍珠紅茶拿鐵', description: 'Smooth black tea latte with real milk, not creamer', tier: 'first-timer' },
    { name: 'Dajia Taro Fresh Milk', nameZh: '大甲芋頭鮮奶', description: 'Famous taro from Dajia region, creamy and thick', tier: 'first-timer' },
    { name: 'Genmaicha Matcha Latte', nameZh: '玄米抹茶乳香拿鐵', description: 'Roasted rice tea with matcha and milk', tier: 'regular' },
  ],
  '珍煮丹': [
    { name: 'Brown Sugar Pearl Milk', nameZh: '黑糖珍珠鮮奶', description: 'The famous tiger stripe brown sugar boba', tier: 'first-timer' },
    { name: 'Thai Tea Latte', description: 'Rich Thai tea with fresh milk - their second best seller', tier: 'regular' },
  ],
  '茶的魔手': [
    { name: 'Hawthorn Oolong', nameZh: '山楂烏龍', description: 'Their #1 best seller - tart hawthorn with smooth oolong', tier: 'first-timer' },
    { name: 'Earl Grey Fresh Milk Tea', nameZh: '伯爵鮮奶茶', description: 'Fragrant bergamot tea with fresh milk', tier: 'first-timer' },
    { name: 'Fresh Milk Pu-erh', nameZh: '鮮奶普洱', description: 'Earthy pu-erh with creamy fresh milk', tier: 'regular' },
  ],
  '可不可熟成紅茶': [
    { name: 'Aged Black Tea Latte', nameZh: '熟成紅茶拿鐵', description: 'Their signature aged tea with fresh milk', tier: 'first-timer' },
    { name: 'Aged Cold Dew', nameZh: '熟成冷露', description: 'Winter melon + black tea, their signature cold drink', tier: 'regular' },
  ],
  '麻古茶坊': [
    { name: 'Cheese Jinxuan Double Q', nameZh: '芝芝金萱雙Q', description: 'Cheese foam over Jinxuan tea with two chewy toppings - their signature', tier: 'first-timer' },
    { name: 'Passion Fruit Double Q', nameZh: '百香雙Q果', description: 'Fresh passion fruit pulp with tapioca and coconut jelly', tier: 'regular' },
  ],
  '龜記': [
    { name: 'Red Grapefruit Jade Green Tea', nameZh: '紅柚翡翠', description: 'Their #1 on Dcard - fresh grapefruit with jade green tea', tier: 'first-timer' },
    { name: 'Apple Red Xuan', nameZh: '蘋果紅萱', description: 'Apple paired with red oolong, their #2 best seller', tier: 'regular' },
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
    { name: 'Brown Sugar Boba + Cream Mousse', nameZh: '黑糖波霸奶蓋', description: 'Tiger stripes topped with salt-sweet cream mousse, their #2', tier: 'first-timer' },
    { name: 'Brown Sugar Boba + Tea Latte', nameZh: '黑糖波霸鮮奶茶', description: 'Tiger stripes with a tea base - more balanced', tier: 'regular' },
  ],
  'Gong Cha': [
    { name: 'Brown Sugar Milk Tea with Pearls', description: 'Their verified #1 best seller', tier: 'first-timer' },
    { name: 'Pearl Milk Tea', description: 'The classic - consistently good across all locations', tier: 'first-timer' },
    { name: 'Milk Foam Earl Grey', description: 'From their signature milk foam series, fragrant bergamot', tier: 'regular' },
  ],
  'Kung Fu Tea': [
    { name: 'Kung Fu Milk Tea', description: 'Their signature blend - rich and bold', tier: 'first-timer' },
    { name: 'Taro Milk Tea', description: 'Creamy taro that is consistently good', tier: 'first-timer' },
    { name: 'Passion Fruit Green Tea', description: 'Tangy fruit tea, great for non-milk-tea drinkers', tier: 'regular' },
  ],
  'Sharetea': [
    { name: 'Wintermelon Milk Tea', nameZh: '冬瓜奶茶', description: 'Their verified best seller - caramel-sweet melon with milk tea', tier: 'first-timer' },
    { name: 'Classic Pearl Milk Tea', nameZh: '珍珠奶茶', description: 'Reliable and creamy, a safe first order', tier: 'first-timer' },
    { name: 'Mango Green Tea', nameZh: '芒果綠茶', description: 'Fresh mango with green tea, fruity and light', tier: 'regular' },
  ],
  'The Alley': [
    { name: 'Deerioca Fresh Milk', nameZh: '鹿丸鮮奶', description: 'Signature tapioca pearls with fresh milk, brown sugar swirl', tier: 'first-timer' },
    { name: 'No. 3 Alley Milk Tea', description: 'Their verified second best seller, premium tea blend', tier: 'regular' },
  ],
  'Yi Fang Taiwan Fruit Tea': [
    { name: 'Pineapple Green Tea', nameZh: '鳳梨綠茶', description: 'Fresh pineapple juice with green tea, signature drink', tier: 'first-timer' },
    { name: 'Passion Fruit Green Tea', nameZh: '百香果綠茶', description: 'Real passion fruit seeds with green tea', tier: 'first-timer' },
    { name: 'Aiyu Lemon', nameZh: '愛玉檸檬', description: 'Taiwanese aiyu jelly with fresh lemon', tier: 'regular' },
  ],
  'Xing Fu Tang': [
    { name: 'Brown Sugar Boba Milk', nameZh: '黑糖珍珠鮮奶', description: 'Flame-torched wok brown sugar pearls, made fresh in-store', tier: 'first-timer' },
    { name: 'Brown Sugar Pearl + Herbal Jelly Milk', nameZh: '黑糖珍珠仙草鮮奶', description: 'Their brown sugar pearls with herbal jelly and fresh milk', tier: 'regular' },
  ],
  'TP Tea': [
    { name: 'Tieguanyin Tea Latte', nameZh: '鐵觀音拿鐵', description: 'Roasted oolong with fresh milk - their star drink', tier: 'first-timer' },
    { name: 'Osmanthus Green Tea', nameZh: '桂花綠茶', description: 'Floral osmanthus with green tea, light and fragrant', tier: 'regular' },
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
    { name: 'Brown Sugar Milk Tea', description: 'Their verified #1 best seller', tier: 'first-timer' },
    { name: 'Golden Bubble Milk Tea', description: 'Their signature golden oolong with bubbles', tier: 'first-timer' },
    { name: 'Honey Green Tea', description: 'Light and refreshing, a popular lighter option', tier: 'regular' },
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
    { name: 'Boya Bindung Latte', nameZh: '伯牙絕弦', description: 'Their mega-seller (60-70% of all sales) - jasmine green tea latte. Note: Chagee does not offer boba toppings', tier: 'first-timer' },
    { name: 'Tie Guan Yin Milk Tea', nameZh: '鐵觀音奶茶', description: 'Roasted oolong milk tea, a popular alternative', tier: 'regular' },
  ],
  'R&B Tea': [
    { name: 'Brown Sugar Pearl Fresh Milk', nameZh: '黑糖珍珠鮮奶', description: 'Flame-torched brown sugar with fresh milk', tier: 'first-timer' },
    { name: 'Cheese Fresh Milk Tea', description: 'Cheese foam on black tea latte', tier: 'regular' },
  ],
  'PlayMade': [
    { name: 'Earl Grey Milk Tea with Strawberry Pearls', description: 'Their signature handmade flavored pearls with earl grey', tier: 'first-timer' },
    { name: 'Brown Sugar Pearl Milk', description: 'Brown sugar with your choice of 8+ handmade pearl flavors', tier: 'regular' },
  ],
  'Each A Cup': [
    { name: 'Pearl Milk Tea', description: 'Classic Singaporean-style boba, consistent quality', tier: 'first-timer' },
    { name: 'Aloe Vera Honey Lemon', description: 'Refreshing citrus with real aloe vera', tier: 'regular' },
  ],

  // === US REGIONAL ===
  "BenGong's Tea": [
    { name: 'Tiramisu Milk Tea', nameZh: '提拉米苏御制奶茶', description: 'Milk tea with torched crème brûlée cream cap - a crowd favorite', tier: 'first-timer' },
    { name: 'Strawberry Cream Slush', nameZh: '元气莓莓雪芙', description: 'Fresh strawberry blended slush with cream, their signature', tier: 'first-timer' },
    { name: 'Brown Sugar Boba Milk Tea', description: 'Hand-made brown sugar with Taiwanese hand-made boba', tier: 'regular' },
  ],
  '7 Leaves Cafe': [
    { name: 'Mung Bean Milk Tea', description: 'Vietnamese-inspired - earthy mung bean with milk tea', tier: 'first-timer' },
    { name: 'Taro Milk Tea', description: 'Creamy and purple, a fan favorite', tier: 'first-timer' },
    { name: 'Sea Cream Tea Jasmine', description: 'Jasmine tea with salted cream foam', tier: 'regular' },
    { name: 'Thai Tea', description: 'One of their most popular - classic Thai tea flavor', tier: 'regular' },
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
  // BenGong's Tea
  '本宮的茶': "BenGong's Tea",
  'BenGongs Tea': "BenGong's Tea",
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

  // Don't render anything if we don't have verified recs for this brand
  if (!hasMatch) return null;

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
