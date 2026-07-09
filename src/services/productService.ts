import axios from 'axios'
import type { Product, ProductSku, ProductResponse } from '@/types'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'
const now = new Date().toISOString()

interface SeedProduct {
  name: string
  description: string
  price: number
  imageUrls: string[]
  category: string
}

const productSeeds: SeedProduct[] = [
  {
    name: '智能降噪耳机',
    description: '通勤、运动和学习都适合的无线蓝牙耳机，支持主动降噪与通透模式。',
    price: 188,
    imageUrls: [
      'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '轻薄机械键盘',
    description: '适合办公、学习和编程的轻薄机械键盘，红轴静音设计。',
    price: 269,
    imageUrls: [
      'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '保温咖啡杯',
    description: '简洁耐用的日常保温杯，适合办公桌和通勤，12 小时保温。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1577937927133-6c9a5c1c5c9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1563297320-b6a2c95cd396?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '运动休闲背包',
    description: '轻便大容量，适合上课、出行和日常通勤，防泼水面料。',
    price: 159,
    imageUrls: [
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '护眼台灯',
    description: '柔和照明，适合夜间学习和居家办公，多档亮度和色温调节。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '便携移动电源',
    description: '20000mAh 大容量，小巧便携，满足手机、耳机等设备日常充电。',
    price: 109,
    imageUrls: [
      'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '无线充电底座',
    description: '桌面无线快充，支持手机和耳机同时补电，兼容 Qi 协议。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622045246592-7b3b8b3b3b3b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '简约双肩包',
    description: '适合通勤和短途出行的轻量背包，多隔层设计，背负舒适。',
    price: 139,
    imageUrls: [
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '人体工学鼠标',
    description: '长时间办公更舒适，减少手腕压力，支持蓝牙和 2.4G 双模连接。',
    price: 119,
    imageUrls: [
      'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '香薰加湿器',
    description: '适合宿舍和卧室的小型桌面加湿器，搭配精油使用更放松。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585342289952-2ef11c70c5c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '瑜伽垫',
    description: '加厚防滑设计，适合居家健身和瑜伽练习，附赠收纳绑带。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '速干跑步短袖',
    description: '透气速干面料，适合夏季户外运动和日常穿搭。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1434389677669-e08b4cda4a10?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '智能手环',
    description: '心率血氧监测，50 米防水，14 天超长续航，支持多种运动模式。',
    price: 229,
    imageUrls: [
      'https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1557438159-51eec7a6c9e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '简约帆布鞋',
    description: '百搭经典款，舒适耐磨，适合日常通勤和休闲出行。',
    price: 149,
    imageUrls: [
      'https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '桌面 LED 补光灯',
    description: '三色温调节，适合直播补光、视频会议和桌面摄影。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1517242027094-631f8c218a0f?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '纯棉床笠三件套',
    description: '亲肤纯棉面料，弹力包裹床垫，含床笠 + 枕套一对。',
    price: 179,
    imageUrls: [
      'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1616627562376-f1e5c9ba8f4e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '零食大礼包',
    description: '坚果果干混合装，办公室休闲零食组合，独立小包装方便分享。',
    price: 88,
    imageUrls: [
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '手冲咖啡套装',
    description: '包含手冲壶、滤杯和分享壶，适合入门手冲咖啡爱好者。',
    price: 219,
    imageUrls: [
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '高清网络摄像头',
    description: '1080P 自动对焦，内置降噪麦克风，即插即用适合远程办公。',
    price: 169,
    imageUrls: [
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '羊毛混纺围巾',
    description: '秋冬保暖必备，柔软舒适不扎脖，多色可选百搭实用。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1606744824167-1e3fbc2a67d7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '无绳跳绳',
    description: '配重球设计模拟真实跳绳手感，室内静音不扰邻，适合居家运动。',
    price: 39,
    imageUrls: [
      'https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601422407692-ec4eeec6207a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '实木置物架',
    description: '多层开放式设计，适合客厅、书房收纳书籍和装饰品。',
    price: 259,
    imageUrls: [
      'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '颈挂式运动耳机',
    description: '轻量化颈挂设计，IPX5 防水防汗，12 小时续航适合户外运动。',
    price: 139,
    imageUrls: [
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '弹力修身长裤',
    description: '高弹力面料穿着舒适，修身版型不紧绷，适合通勤和商务休闲。',
    price: 169,
    imageUrls: [
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '冷萃咖啡壶',
    description: '玻璃瓶身 + 细密滤网，睡前加水冷藏，早起即享顺滑冷萃。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '防蓝光眼镜',
    description: '适合长时间面对屏幕的办公和学习人群，减少眼疲劳。',
    price: 59,
    imageUrls: [
      'https://images.unsplash.com/photo-1574258495973-f010dfbb5371?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1577803645773-f96470509666?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '瑜伽砖两块装',
    description: '高密度 EVA 材质，辅助拉伸和体式练习，初学者必备工具。',
    price: 35,
    imageUrls: [
      'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '遮光窗帘',
    description: '加厚三层遮光面料，隔音隔热，适合卧室和影音室使用。',
    price: 119,
    imageUrls: [
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '每日坚果混合装',
    description: '核桃腰果巴旦木开心果 4 种混合，每日一小袋补充营养。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1536591146385-e7fa9ab39d28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1508717272100-8ee02bc8593c?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '折叠露营椅',
    description: '轻量铝合金框架，承重 120kg，收纳方便适合户外郊游。',
    price: 189,
    imageUrls: [
      'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  }
]

const colorOptions = ['深空灰', '珍珠白', '午夜蓝']
const versionOptions = [
  { suffix: '标准版', priceDelta: 0, stockDelta: 0 },
  { suffix: 'Pro 版', priceDelta: 60, stockDelta: -15 },
  { suffix: '旗舰版', priceDelta: 130, stockDelta: -30 }
]

/** 为种子商品生成 SKU 列表 */
const generateSkus = (productId: number, basePrice: number, imageUrls: string[]): ProductSku[] => {
  const skus: ProductSku[] = []
  let skuCounter = productId * 100

  colorOptions.forEach((color, colorIndex) => {
    versionOptions.forEach((version, versionIndex) => {
      skus.push({
        skuId: skuCounter++,
        productId,
        name: `${color} · ${version.suffix}`,
        price: basePrice + version.priceDelta,
        stock: Math.max(5, 40 - colorIndex * 8 - version.stockDelta),
        imageUrl: imageUrls[colorIndex % imageUrls.length],
        attributes: { 颜色: color, 版本: version.suffix }
      })
    })
  })

  return skus
}

/** 计算所有 SKU 中的最低价 */
const minSkuPrice = (skus: ProductSku[]): number =>
  Math.min(...skus.map((s) => s.price))

/** 计算所有 SKU 的库存总和 */
const totalSkuStock = (skus: ProductSku[]): number =>
  skus.reduce((sum, s) => sum + s.stock, 0)

export const mockProducts: Product[] = productSeeds.map((seed, groupIndex) => {
  const productId = 1001 + groupIndex
  const skus = generateSkus(productId, seed.price, seed.imageUrls)

  return {
    productId,
    name: seed.name,
    description: seed.description,
    price: minSkuPrice(skus),
    stock: totalSkuStock(skus),
    status: 'active' as const,
    imageUrls: seed.imageUrls,
    category: seed.category,
    skus,
    createdAt: now,
    updatedAt: now
  }
})

const mockResponse = (data: Product[] | Product): ProductResponse => ({
  code: '0000',
  info: 'mock data',
  data
})

export const productService = {
  async getProducts() {
    try {
      const response = await axios.get<ProductResponse>(`${BASE_URL}/product/list`)
      return response.data
    } catch {
      return mockResponse(mockProducts)
    }
  },

  async getProduct(id: number) {
    try {
      const response = await axios.get<ProductResponse>(`${BASE_URL}/product/get`, {
        params: { productId: id }
      })
      return response.data
    } catch {
      const product = mockProducts.find((item) => item.productId === id)
      return mockResponse(product || mockProducts[0])
    }
  }
}
