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
  },
  {
    name: '平板电脑支架',
    description: '全铝合金可折叠，多角度调节，适合办公和绘画使用。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: 'USB-C 扩展坞',
    description: '7合1多功能，支持HDMI 4K输出、SD卡读取和USB 3.0扩展。',
    price: 199,
    imageUrls: [
      'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '无线鼠标静音款',
    description: '轻薄便携，静音按键不打扰他人，适合图书馆和办公室。',
    price: 49,
    imageUrls: [
      'https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: 'Type-C 快充数据线',
    description: '双口快充，支持65W笔记本和手机同时充电，尼龙编织耐用。',
    price: 39,
    imageUrls: [
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '蓝牙音箱便携款',
    description: 'IPX7防水，20小时续航，户外露营派对必备。',
    price: 159,
    imageUrls: [
      'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '手机云台稳定器',
    description: '三轴防抖，一键切换横竖拍，支持人脸追踪和延时摄影。',
    price: 299,
    imageUrls: [
      'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '机械键盘键帽套装',
    description: 'PBT材质热升华工艺，169键大全套，兼容主流轴体。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '显示器挂灯',
    description: '非对称光源不反光，三档色温调节，USB供电即插即用。',
    price: 149,
    imageUrls: [
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1557438159-51eec7a6c9e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '桌面微型投影仪',
    description: '便携迷你，支持1080P解码，适合卧室观影和商务演示。',
    price: 499,
    imageUrls: [
      'https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '平板触控笔',
    description: '磁吸充电，防误触，4096级压感，适合绘画和笔记。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '无线投屏器',
    description: '即插即投，支持手机和笔记本无线投屏到电视和投影仪。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '氮化镓充电头',
    description: '65W三口快充，小巧便携，兼容手机平板笔记本。',
    price: 109,
    imageUrls: [
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85'
    ],
    category: '数码'
  },
  {
    name: '北欧风落地灯',
    description: '简约设计暖光LED，适合客厅和卧室角落氛围照明。',
    price: 239,
    imageUrls: [
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '免打孔置物架',
    description: '卫生间厨房通用，强力免钉胶安装，承重10kg。',
    price: 29,
    imageUrls: [
      'https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '记忆棉坐垫',
    description: '久坐不累，适合办公椅和汽车座椅，矫正坐姿分散压力。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '收纳箱三件套',
    description: '可折叠设计，牛津布+钢架，适合衣物和杂物分类收纳。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '静音挂钟',
    description: '简约北欧风格，静音机芯不滴答，适合卧室和书房。',
    price: 49,
    imageUrls: [
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1577803645773-f96470509666?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '浴室防滑垫',
    description: '吸水速干，可机洗，底部防滑贴合地面安全可靠。',
    price: 39,
    imageUrls: [
      'https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '珊瑚绒空调毯',
    description: '柔软亲肤，办公室午休和沙发追剧好伴侣。',
    price: 59,
    imageUrls: [
      'https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '可调节电脑桌',
    description: '升降调节，站坐交替办公更健康，带移动滚轮。',
    price: 349,
    imageUrls: [
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '磁吸刀架',
    description: '厨房不锈钢壁挂式，免打孔强磁吸附，整齐收纳刀具。',
    price: 45,
    imageUrls: [
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '防滑衣架10个装',
    description: '无痕防滑设计，ABS材质坚固耐用，适合各类衣物。',
    price: 25,
    imageUrls: [
      'https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85'
    ],
    category: '家居'
  },
  {
    name: '纯棉短袖T恤',
    description: '200g重磅纯棉，宽松版型不挑身材，夏季百搭基础款。',
    price: 59,
    imageUrls: [
      'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '轻薄防晒衣',
    description: 'UPF50+高倍防晒，透气速干，可收纳至口袋方便携带。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '商务休闲衬衫',
    description: '免烫抗皱面料，修身剪裁，适合面试和日常通勤。',
    price: 169,
    imageUrls: [
      'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '羊绒混纺毛衣',
    description: '含羊绒成分柔软保暖，圆领百搭款，秋冬内搭单穿皆可。',
    price: 239,
    imageUrls: [
      'https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '运动休闲卫衣',
    description: '加绒保暖，落肩宽松版型，适合秋冬日常穿搭和运动。',
    price: 139,
    imageUrls: [
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '商务皮带',
    description: '头层牛皮自动扣，简约商务风，送礼自用两相宜。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '纯棉袜子5双装',
    description: '精梳棉透气吸汗，弹力袜口不勒脚，日常百搭基础款。',
    price: 29,
    imageUrls: [
      'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '轻便跑鞋',
    description: '飞织鞋面透气舒适，EVA缓震鞋底，适合日常慢跑和健走。',
    price: 199,
    imageUrls: [
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1529966103427-3e39c4561c5a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '防晒冰袖两双装',
    description: 'UPF50+物理防晒，冰感面料一秒降温，夏季户外必备。',
    price: 19,
    imageUrls: [
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '帆布腰带',
    description: '无孔自动扣设计，休闲百搭，适合牛仔裤和休闲裤。',
    price: 39,
    imageUrls: [
      'https://images.unsplash.com/photo-1529966103427-3e39c4561c5a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85'
    ],
    category: '服饰'
  },
  {
    name: '运动水壶750ml',
    description: 'Tritan材质安全无毒，弹盖一键开启，适合健身跑步携带。',
    price: 49,
    imageUrls: [
      'https://images.unsplash.com/photo-1585342289952-2ef11c70c5c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '健身手套',
    description: '透气防滑掌垫，保护手腕，适合引体向上和哑铃训练。',
    price: 39,
    imageUrls: [
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '弹力带套装',
    description: '5条不同阻力，附收纳袋和训练指南，适合居家力量训练。',
    price: 29,
    imageUrls: [
      'https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '户外速干毛巾',
    description: '超细纤维吸水速干，小巧轻便，适合健身游泳和户外运动。',
    price: 35,
    imageUrls: [
      'https://images.unsplash.com/photo-1606744824167-1e3fbc2a67d7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '登山杖一对',
    description: '7075铝合金轻量，可伸缩调节，EVA防滑握把。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '运动腰包',
    description: '超薄隐形设计，防水面料，放手机钥匙轻松跑步。',
    price: 25,
    imageUrls: [
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '泳镜防雾款',
    description: '高清防雾镜片，硅胶密封圈不进水，适合游泳和潜水。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1536591146385-e7fa9ab39d28?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '羽毛球拍一对',
    description: '碳纤维材质轻量耐用，含球拍包和3只球，适合休闲运动。',
    price: 159,
    imageUrls: [
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '运动护膝',
    description: '弹簧支撑硅胶防滑，适合跑步篮球深蹲，缓解膝关节压力。',
    price: 59,
    imageUrls: [
      'https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '骑行手套',
    description: '掌心加厚缓震，透气网眼面料，触屏指尖方便操作手机。',
    price: 45,
    imageUrls: [
      'https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '运动'
  },
  {
    name: '有机绿茶礼盒',
    description: '明前采摘嫩芽，清香回甘，精美礼盒装适合送礼。',
    price: 168,
    imageUrls: [
      'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '黑巧克力礼盒',
    description: '72%可可含量，丝滑口感，独立包装方便分享。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '即食燕麦片',
    description: '澳洲进口原料，高纤维低脂肪，适合健身和减脂早餐。',
    price: 39,
    imageUrls: [
      'https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '红枣枸杞茶',
    description: '独立三角包，即泡即饮，养生暖宫适合女生日常调理。',
    price: 49,
    imageUrls: [
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '全麦面包粉',
    description: '高筋面粉+全麦粉套装，含酵母，适合家庭烘焙。',
    price: 35,
    imageUrls: [
      'https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '牛肉干五香味',
    description: '内蒙古风干牛肉，独立小包装，高蛋白低脂肪零食。',
    price: 59,
    imageUrls: [
      'https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '进口蜂蜜',
    description: '新西兰麦卢卡蜂蜜UMF10+，天然纯正无添加。',
    price: 259,
    imageUrls: [
      'https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '速溶黑咖啡',
    description: '云南小粒咖啡，冻干技术保留原香，冷热水即溶。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '坚果礼盒',
    description: '6罐混合装，含夏威夷果、碧根果、腰果等，年节送礼。',
    price: 199,
    imageUrls: [
      'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '蒟蒻果冻',
    description: '0脂肪低卡路里，果汁含量≥25%，办公室休闲零食。',
    price: 29,
    imageUrls: [
      'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85'
    ],
    category: '食品'
  },
  {
    name: '补水保湿面霜',
    description: '含神经酰胺和玻尿酸，锁水修护屏障，适合干性和敏感肌。',
    price: 129,
    imageUrls: [
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '防晒霜SPF50+',
    description: '清爽不油腻，物理+化学双重防晒，面部全身通用。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '氨基酸洗面奶',
    description: '温和清洁不紧绷，泡沫细腻丰富，适合每日早晚使用。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1622045246592-7b3b8b3b3b3b?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '口红三支套装',
    description: '豆沙/正红/橘棕三色，丝绒哑光质地，显白不挑皮。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '眼影盘12色',
    description: '大地色+玫瑰色系组合，粉质细腻显色度高，日常通勤百搭。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '面膜补水套装',
    description: '玻尿酸精华液面膜20片装，补水保湿舒缓修护。',
    price: 59,
    imageUrls: [
      'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '精华液30ml',
    description: '烟酰胺+维C双重亮肤，淡化痘印提亮肤色，质地清爽好吸收。',
    price: 159,
    imageUrls: [
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '卸妆水500ml',
    description: '温和卸妆不刺激，眼唇面部三合一，敏感肌可用。',
    price: 49,
    imageUrls: [
      'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '眉笔双头款',
    description: '极细笔芯精准勾勒，自带眉刷晕染自然，持久不脱妆。',
    price: 29,
    imageUrls: [
      'https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '沐浴露香氛款',
    description: '持久留香，氨基酸配方温和清洁，泡沫绵密易冲洗。',
    price: 49,
    imageUrls: [
      'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1616627562376-f1e5c9ba8f4e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '护发精油',
    description: '摩洛哥坚果油成分，修复毛躁分叉，吹发前涂抹保护发丝。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '男士洁面套装',
    description: '洁面乳+爽肤水+乳液三件套，控油清爽适合油性肌肤。',
    price: 139,
    imageUrls: [
      'https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '美妆'
  },
  {
    name: '《深入理解计算机系统》',
    description: '经典CS教材，全面讲解计算机系统原理和底层机制。',
    price: 139,
    imageUrls: [
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《算法导论》第四版',
    description: '算法领域经典著作，涵盖各种算法设计和分析方法。',
    price: 128,
    imageUrls: [
      'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《设计模式》',
    description: 'GoF经典之作，23种设计模式系统讲解，软件工程师必读。',
    price: 79,
    imageUrls: [
      'https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《JavaScript高级程序设计》',
    description: '前端开发红宝书，全面深入讲解JS核心概念和进阶用法。',
    price: 99,
    imageUrls: [
      'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《Python编程从入门到实践》',
    description: '零基础学Python，项目驱动式教学，含数据可视化和Web开发。',
    price: 89,
    imageUrls: [
      'https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《人性的弱点》',
    description: '卡耐基经典人际关系著作，提升沟通能力和情商。',
    price: 35,
    imageUrls: [
      'https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《思考，快与慢》',
    description: '诺贝尔经济学奖得主著作，探索人类认知偏差和决策机制。',
    price: 69,
    imageUrls: [
      'https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1517242027094-631f8c218a0f?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《三体》全集',
    description: '刘慈欣科幻巨著，雨果奖获奖作品，中国科幻巅峰之作。',
    price: 93,
    imageUrls: [
      'https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《百年孤独》',
    description: '马尔克斯魔幻现实主义经典，拉丁美洲文学的代表作。',
    price: 55,
    imageUrls: [
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
  {
    name: '《小王子》',
    description: '圣埃克苏佩里经典童话，适合所有年龄阅读的心灵之书。',
    price: 29,
    imageUrls: [
      'https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85',
      'https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85'
    ],
    category: '图书'
  },
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
