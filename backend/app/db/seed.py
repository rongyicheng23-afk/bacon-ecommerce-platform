"""种子数据：demo 用户 + 104 商品（与前端 mock 对齐）"""
import json
import sqlite3

from app.core.security import hash_password
from app.db.database import now_iso

PRODUCT_SEEDS = [
    ("智能降噪耳机", "通勤、运动和学习都适合的无线蓝牙耳机，支持主动降噪与通透模式。", 188, "数码",
     ["https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85"]),
    ("轻薄机械键盘", "适合办公、学习和编程的轻薄机械键盘，红轴静音设计。", 269, "数码",
     ["https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85"]),
    ("保温咖啡杯", "简洁耐用的日常保温杯，适合办公桌和通勤，12 小时保温。", 79, "家居",
     ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1577937927133-6c9a5c1c5c9f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1563297320-b6a2c95cd396?auto=format&fit=crop&w=900&q=85"]),
    ("运动休闲背包", "轻便大容量，适合上课、出行和日常通勤，防泼水面料。", 159, "服饰",
     ["https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85"]),
    ("护眼台灯", "柔和照明，适合夜间学习和居家办公，多档亮度和色温调节。", 129, "家居",
     ["https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85"]),
    ("便携移动电源", "20000mAh 大容量，小巧便携，满足手机、耳机等设备日常充电。", 109, "数码",
     ["https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85"]),
    ("无线充电底座", "桌面无线快充，支持手机和耳机同时补电，兼容 Qi 协议。", 99, "数码",
     ["https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1622045246592-7b3b8b3b3b3b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85"]),
    ("简约双肩包", "适合通勤和短途出行的轻量背包，多隔层设计，背负舒适。", 139, "服饰",
     ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85"]),
    ("人体工学鼠标", "长时间办公更舒适，减少手腕压力，支持蓝牙和 2.4G 双模连接。", 119, "数码",
     ["https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85"]),
    ("香薰加湿器", "适合宿舍和卧室的小型桌面加湿器，搭配精油使用更放松。", 89, "家居",
     ["https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1585342289952-2ef11c70c5c5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85"]),
    ("瑜伽垫", "加厚防滑设计，适合居家健身和瑜伽练习，附赠收纳绑带。", 79, "运动",
     ["https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85"]),
    ("速干跑步短袖", "透气速干面料，适合夏季户外运动和日常穿搭。", 69, "运动",
     ["https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1434389677669-e08b4cda4a10?auto=format&fit=crop&w=900&q=85"]),
    ("智能手环", "心率血氧监测，50 米防水，14 天超长续航，支持多种运动模式。", 229, "数码",
     ["https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1557438159-51eec7a6c9e8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85"]),
    ("简约帆布鞋", "百搭经典款，舒适耐磨，适合日常通勤和休闲出行。", 149, "服饰",
     ["https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85"]),
    ("桌面 LED 补光灯", "三色温调节，适合直播补光、视频会议和桌面摄影。", 129, "数码",
     ["https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1517242027094-631f8c218a0f?auto=format&fit=crop&w=900&q=85"]),
    ("纯棉床笠三件套", "亲肤纯棉面料，弹力包裹床垫，含床笠 + 枕套一对。", 179, "家居",
     ["https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1616627562376-f1e5c9ba8f4e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85"]),
    ("零食大礼包", "坚果果干混合装，办公室休闲零食组合，独立小包装方便分享。", 88, "食品",
     ["https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85"]),
    ("手冲咖啡套装", "包含手冲壶、滤杯和分享壶，适合入门手冲咖啡爱好者。", 219, "食品",
     ["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1514432324607-a09d9b4aefda?auto=format&fit=crop&w=900&q=85"]),
    ("高清网络摄像头", "1080P 自动对焦，内置降噪麦克风，即插即用适合远程办公。", 169, "数码",
     ["https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85"]),
    ("羊毛混纺围巾", "秋冬保暖必备，柔软舒适不扎脖，多色可选百搭实用。", 89, "服饰",
     ["https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1606744824167-1e3fbc2a67d7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85"]),
    ("无绳跳绳", "配重球设计模拟真实跳绳手感，室内静音不扰邻，适合居家运动。", 39, "运动",
     ["https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601422407692-ec4eeec6207a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85"]),
    ("实木置物架", "多层开放式设计，适合客厅、书房收纳书籍和装饰品。", 259, "家居",
     ["https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85"]),
    ("颈挂式运动耳机", "轻量化颈挂设计，IPX5 防水防汗，12 小时续航适合户外运动。", 139, "数码",
     ["https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85"]),
    ("弹力修身长裤", "高弹力面料穿着舒适，修身版型不紧绷，适合通勤和商务休闲。", 169, "服饰",
     ["https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85"]),
    ("冷萃咖啡壶", "玻璃瓶身 + 细密滤网，睡前加水冷藏，早起即享顺滑冷萃。", 99, "食品",
     ["https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85"]),
    ("防蓝光眼镜", "适合长时间面对屏幕的办公和学习人群，减少眼疲劳。", 59, "数码",
     ["https://images.unsplash.com/photo-1574258495973-f010dfbb5371?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1577803645773-f96470509666?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85"]),
    ("瑜伽砖两块装", "高密度 EVA 材质，辅助拉伸和体式练习，初学者必备工具。", 35, "运动",
     ["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85"]),
    ("遮光窗帘", "加厚三层遮光面料，隔音隔热，适合卧室和影音室使用。", 119, "家居",
     ["https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85"]),
    ("每日坚果混合装", "核桃腰果巴旦木开心果 4 种混合，每日一小袋补充营养。", 69, "食品",
     ["https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1536591146385-e7fa9ab39d28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1508717272100-8ee02bc8593c?auto=format&fit=crop&w=900&q=85"]),
    ("折叠露营椅", "轻量铝合金框架，承重 120kg，收纳方便适合户外郊游。", 189, "运动",
     ["https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85"]),
    ("平板电脑支架", "全铝合金可折叠，多角度调节，适合办公和绘画使用。", 89, "数码",
     ["https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85"]),
    ("USB-C 扩展坞", "7合1多功能，支持HDMI 4K输出、SD卡读取和USB 3.0扩展。", 199, "数码",
     ["https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85"]),
    ("无线鼠标静音款", "轻薄便携，静音按键不打扰他人，适合图书馆和办公室。", 49, "数码",
     ["https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85"]),
    ("Type-C 快充数据线", "双口快充，支持65W笔记本和手机同时充电，尼龙编织耐用。", 39, "数码",
     ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85"]),
    ("蓝牙音箱便携款", "IPX7防水，20小时续航，户外露营派对必备。", 159, "数码",
     ["https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85"]),
    ("手机云台稳定器", "三轴防抖，一键切换横竖拍，支持人脸追踪和延时摄影。", 299, "数码",
     ["https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85"]),
    ("机械键盘键帽套装", "PBT材质热升华工艺，169键大全套，兼容主流轴体。", 79, "数码",
     ["https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85"]),
    ("显示器挂灯", "非对称光源不反光，三档色温调节，USB供电即插即用。", 149, "数码",
     ["https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1557438159-51eec7a6c9e8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85"]),
    ("桌面微型投影仪", "便携迷你，支持1080P解码，适合卧室观影和商务演示。", 499, "数码",
     ["https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85"]),
    ("平板触控笔", "磁吸充电，防误触，4096级压感，适合绘画和笔记。", 129, "数码",
     ["https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85"]),
    ("无线投屏器", "即插即投，支持手机和笔记本无线投屏到电视和投影仪。", 99, "数码",
     ["https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85"]),
    ("氮化镓充电头", "65W三口快充，小巧便携，兼容手机平板笔记本。", 109, "数码",
     ["https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85"]),
    ("北欧风落地灯", "简约设计暖光LED，适合客厅和卧室角落氛围照明。", 239, "家居",
     ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85"]),
    ("免打孔置物架", "卫生间厨房通用，强力免钉胶安装，承重10kg。", 29, "家居",
     ["https://images.unsplash.com/photo-1585336261022-680e530ce2d7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85"]),
    ("记忆棉坐垫", "久坐不累，适合办公椅和汽车座椅，矫正坐姿分散压力。", 69, "家居",
     ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85"]),
    ("收纳箱三件套", "可折叠设计，牛津布+钢架，适合衣物和杂物分类收纳。", 89, "家居",
     ["https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85"]),
    ("静音挂钟", "简约北欧风格，静音机芯不滴答，适合卧室和书房。", 49, "家居",
     ["https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1577803645773-f96470509666?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85"]),
    ("浴室防滑垫", "吸水速干，可机洗，底部防滑贴合地面安全可靠。", 39, "家居",
     ["https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85"]),
    ("珊瑚绒空调毯", "柔软亲肤，办公室午休和沙发追剧好伴侣。", 59, "家居",
     ["https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85"]),
    ("可调节电脑桌", "升降调节，站坐交替办公更健康，带移动滚轮。", 349, "家居",
     ["https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85"]),
    ("磁吸刀架", "厨房不锈钢壁挂式，免打孔强磁吸附，整齐收纳刀具。", 45, "家居",
     ["https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85"]),
    ("防滑衣架10个装", "无痕防滑设计，ABS材质坚固耐用，适合各类衣物。", 25, "家居",
     ["https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85"]),
    ("纯棉短袖T恤", "200g重磅纯棉，宽松版型不挑身材，夏季百搭基础款。", 59, "服饰",
     ["https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=900&q=85"]),
    ("轻薄防晒衣", "UPF50+高倍防晒，透气速干，可收纳至口袋方便携带。", 129, "服饰",
     ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85"]),
    ("商务休闲衬衫", "免烫抗皱面料，修身剪裁，适合面试和日常通勤。", 169, "服饰",
     ["https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85"]),
    ("羊绒混纺毛衣", "含羊绒成分柔软保暖，圆领百搭款，秋冬内搭单穿皆可。", 239, "服饰",
     ["https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85"]),
    ("运动休闲卫衣", "加绒保暖，落肩宽松版型，适合秋冬日常穿搭和运动。", 139, "服饰",
     ["https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85"]),
    ("商务皮带", "头层牛皮自动扣，简约商务风，送礼自用两相宜。", 99, "服饰",
     ["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85"]),
    ("纯棉袜子5双装", "精梳棉透气吸汗，弹力袜口不勒脚，日常百搭基础款。", 29, "服饰",
     ["https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85"]),
    ("轻便跑鞋", "飞织鞋面透气舒适，EVA缓震鞋底，适合日常慢跑和健走。", 199, "服饰",
     ["https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1529966103427-3e39c4561c5a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85"]),
    ("防晒冰袖两双装", "UPF50+物理防晒，冰感面料一秒降温，夏季户外必备。", 19, "服饰",
     ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85"]),
    ("帆布腰带", "无孔自动扣设计，休闲百搭，适合牛仔裤和休闲裤。", 39, "服饰",
     ["https://images.unsplash.com/photo-1529966103427-3e39c4561c5a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85"]),
    ("运动水壶750ml", "Tritan材质安全无毒，弹盖一键开启，适合健身跑步携带。", 49, "运动",
     ["https://images.unsplash.com/photo-1585342289952-2ef11c70c5c5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=900&q=85"]),
    ("健身手套", "透气防滑掌垫，保护手腕，适合引体向上和哑铃训练。", 39, "运动",
     ["https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85"]),
    ("弹力带套装", "5条不同阻力，附收纳袋和训练指南，适合居家力量训练。", 29, "运动",
     ["https://images.unsplash.com/photo-1543465077-db45d34b88a5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534245343088-2c5e5cd41c74?auto=format&fit=crop&w=900&q=85"]),
    ("户外速干毛巾", "超细纤维吸水速干，小巧轻便，适合健身游泳和户外运动。", 35, "运动",
     ["https://images.unsplash.com/photo-1606744824167-1e3fbc2a67d7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85"]),
    ("登山杖一对", "7075铝合金轻量，可伸缩调节，EVA防滑握把。", 129, "运动",
     ["https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1572569911257-b128bc965b9a?auto=format&fit=crop&w=900&q=85"]),
    ("运动腰包", "超薄隐形设计，防水面料，放手机钥匙轻松跑步。", 25, "运动",
     ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85"]),
    ("泳镜防雾款", "高清防雾镜片，硅胶密封圈不进水，适合游泳和潜水。", 69, "运动",
     ["https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1536591146385-e7fa9ab39d28?auto=format&fit=crop&w=900&q=85"]),
    ("羽毛球拍一对", "碳纤维材质轻量耐用，含球拍包和3只球，适合休闲运动。", 159, "运动",
     ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85"]),
    ("运动护膝", "弹簧支撑硅胶防滑，适合跑步篮球深蹲，缓解膝关节压力。", 59, "运动",
     ["https://images.unsplash.com/photo-1605773527852-c546a8584ea3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1560105832-3544d4e5e8a0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85"]),
    ("骑行手套", "掌心加厚缓震，透气网眼面料，触屏指尖方便操作手机。", 45, "运动",
     ["https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=85"]),
    ("有机绿茶礼盒", "明前采摘嫩芽，清香回甘，精美礼盒装适合送礼。", 168, "食品",
     ["https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85"]),
    ("黑巧克力礼盒", "72%可可含量，丝滑口感，独立包装方便分享。", 79, "食品",
     ["https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1588286840104-8957b019727f?auto=format&fit=crop&w=900&q=85"]),
    ("即食燕麦片", "澳洲进口原料，高纤维低脂肪，适合健身和减脂早餐。", 39, "食品",
     ["https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85"]),
    ("红枣枸杞茶", "独立三角包，即泡即饮，养生暖宫适合女生日常调理。", 49, "食品",
     ["https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1504630083234-14187a9df0f5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85"]),
    ("全麦面包粉", "高筋面粉+全麦粉套装，含酵母，适合家庭烘焙。", 35, "食品",
     ["https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85"]),
    ("牛肉干五香味", "内蒙古风干牛肉，独立小包装，高蛋白低脂肪零食。", 59, "食品",
     ["https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85"]),
    ("进口蜂蜜", "新西兰麦卢卡蜂蜜UMF10+，天然纯正无添加。", 259, "食品",
     ["https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85"]),
    ("速溶黑咖啡", "云南小粒咖啡，冻干技术保留原香，冷热水即溶。", 69, "食品",
     ["https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85"]),
    ("坚果礼盒", "6罐混合装，含夏威夷果、碧根果、腰果等，年节送礼。", 199, "食品",
     ["https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85"]),
    ("蒟蒻果冻", "0脂肪低卡路里，果汁含量≥25%，办公室休闲零食。", 29, "食品",
     ["https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1501045337507-64de3b3e5a0e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85"]),
    ("补水保湿面霜", "含神经酰胺和玻尿酸，锁水修护屏障，适合干性和敏感肌。", 129, "美妆",
     ["https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1534073828943-f801091bb18c?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1586816879360-004f5b0c51e5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85"]),
    ("防晒霜SPF50+", "清爽不油腻，物理+化学双重防晒，面部全身通用。", 89, "美妆",
     ["https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559496417-e7f25cb247f3?auto=format&fit=crop&w=900&q=85"]),
    ("氨基酸洗面奶", "温和清洁不紧绷，泡沫细腻丰富，适合每日早晚使用。", 69, "美妆",
     ["https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1622045246592-7b3b8b3b3b3b?auto=format&fit=crop&w=900&q=85"]),
    ("口红三支套装", "豆沙/正红/橘棕三色，丝绒哑光质地，显白不挑皮。", 99, "美妆",
     ["https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575844264771-892081089af0?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?auto=format&fit=crop&w=900&q=85"]),
    ("眼影盘12色", "大地色+玫瑰色系组合，粉质细腻显色度高，日常通勤百搭。", 79, "美妆",
     ["https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85"]),
    ("面膜补水套装", "玻尿酸精华液面膜20片装，补水保湿舒缓修护。", 59, "美妆",
     ["https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1585412727339-54e4bae3bbf9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?auto=format&fit=crop&w=900&q=85"]),
    ("精华液30ml", "烟酰胺+维C双重亮肤，淡化痘印提亮肤色，质地清爽好吸收。", 159, "美妆",
     ["https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565008447742-04327ac71d8e?auto=format&fit=crop&w=900&q=85"]),
    ("卸妆水500ml", "温和卸妆不刺激，眼唇面部三合一，敏感肌可用。", 49, "美妆",
     ["https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1538688525198-9b88f6f53126?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1520549233664-03f65c7d1320?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1593810450967-f9df427093e3?auto=format&fit=crop&w=900&q=85"]),
    ("眉笔双头款", "极细笔芯精准勾勒，自带眉刷晕染自然，持久不脱妆。", 29, "美妆",
     ["https://images.unsplash.com/photo-1556742502-ec7c0e9f34b1?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1565538810643-b5bdb714032a?auto=format&fit=crop&w=900&q=85"]),
    ("沐浴露香氛款", "持久留香，氨基酸配方温和清洁，泡沫绵密易冲洗。", 49, "美妆",
     ["https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1616627562376-f1e5c9ba8f4e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1591076482161-42ce6da69f67?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599490656913-b1fa4f1a0d16?auto=format&fit=crop&w=900&q=85"]),
    ("护发精油", "摩洛哥坚果油成分，修复毛躁分叉，吹发前涂抹保护发丝。", 89, "美妆",
     ["https://images.unsplash.com/photo-1609081219090-a6d81d3085bf?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85"]),
    ("男士洁面套装", "洁面乳+爽肤水+乳液三件套，控油清爽适合油性肌肤。", 139, "美妆",
     ["https://images.unsplash.com/photo-1543248939-b5d49ce4dc6b?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1583394838336-acd977736f90?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1584108444478-af0b8f3520d0?auto=format&fit=crop&w=900&q=85"]),
    ("《深入理解计算机系统》", "经典CS教材，全面讲解计算机系统原理和底层机制。", 139, "图书",
     ["https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541534741688-d60781cd7c1f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=900&q=85"]),
    ("《算法导论》第四版", "算法领域经典著作，涵盖各种算法设计和分析方法。", 128, "图书",
     ["https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1556010661-1dc21a5d7ae6?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1541140532154-b024d1c0c78e?auto=format&fit=crop&w=900&q=85"]),
    ("《设计模式》", "GoF经典之作，23种设计模式系统讲解，软件工程师必读。", 79, "图书",
     ["https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?auto=format&fit=crop&w=900&q=85"]),
    ("《JavaScript高级程序设计》", "前端开发红宝书，全面深入讲解JS核心概念和进阶用法。", 99, "图书",
     ["https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1559305616-3f99cd43e8cb?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1601924994987-69e26d50dc26?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?auto=format&fit=crop&w=900&q=85"]),
    ("《Python编程从入门到实践》", "零基础学Python，项目驱动式教学，含数据可视化和Web开发。", 89, "图书",
     ["https://images.unsplash.com/photo-1591370874773-6702e8f12fd8?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1597072689227-888e5f0c9c96?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1600857544200-b2f666693a28?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1515378791036-b8f1ee53c1a5?auto=format&fit=crop&w=900&q=85"]),
    ("《人性的弱点》", "卡耐基经典人际关系著作，提升沟通能力和情商。", 35, "图书",
     ["https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1537905569824-89e4375f9d64?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1561883088-039e53143d73?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85"]),
    ("《思考，快与慢》", "诺贝尔经济学奖得主著作，探索人类认知偏差和决策机制。", 69, "图书",
     ["https://images.unsplash.com/photo-1598289431512-b97b0917affc?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1517242027094-631f8c218a0f?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?auto=format&fit=crop&w=900&q=85"]),
    ("《三体》全集", "刘慈欣科幻巨著，雨果奖获奖作品，中国科幻巅峰之作。", 93, "图书",
     ["https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1532980400857-e8d9d275d858?auto=format&fit=crop&w=900&q=85"]),
    ("《百年孤独》", "马尔克斯魔幻现实主义经典，拉丁美洲文学的代表作。", 55, "图书",
     ["https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=900&q=85"]),
    ("《小王子》", "圣埃克苏佩里经典童话，适合所有年龄阅读的心灵之书。", 29, "图书",
     ["https://images.unsplash.com/photo-1589571894960-20bbe2828d0a?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=900&q=85", "https://images.unsplash.com/photo-1543076447-68196a3d6b1e?auto=format&fit=crop&w=900&q=85"]),
]

COLORS = ["深空灰", "珍珠白", "午夜蓝"]
VERSIONS = [
    ("标准版", 0, 0),
    ("Pro 版", 60, -15),
    ("旗舰版", 130, -30),
]

CATEGORY_SEEDS = [
    ("数码", None, 1),
    ("服饰", None, 2),
    ("家居", None, 3),
    ("运动", None, 4),
    ("食品", None, 5),
    ("美妆", None, 6),
    ("图书", None, 7),
]


def seed_demo_data(conn: sqlite3.Connection) -> None:
    ts = now_iso()

    # 种子分类
    for name, parent_id, sort_order in CATEGORY_SEEDS:
        category = conn.execute(
            "SELECT 1 FROM categories WHERE name = ?", (name,)
        ).fetchone()
        if not category:
            conn.execute(
                "INSERT INTO categories (name, parent_id, sort_order, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (name, parent_id, sort_order, "active", ts, ts),
            )

    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        conn.execute(
            """INSERT INTO users (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            ("荣同学", "student@example.com", "13800002026", "buyer", None, None, hash_password("123456"), "active", ts, ts),
        )
        seller_cur = conn.execute(
            """INSERT INTO users (username, email, phone, role, shop_name, main_category, password_hash, status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            ("Bacon 数码旗舰店", "seller@example.com", "13900002026", "seller", "Bacon 数码旗舰店", "数码", hash_password("123456"), "active", ts, ts),
        )
        seller_id = seller_cur.lastrowid
        conn.execute(
            "INSERT INTO shops (owner_user_id, name, description, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (seller_id, "Bacon 数码旗舰店", "专业的数码产品店铺，提供各类数码设备及配件。", "active", ts, ts),
        )

    # 旧数据库可能已有用户但还没有 shops 表数据，启动时只补缺失店铺。
    sellers = conn.execute(
        "SELECT user_id, username, shop_name, main_category FROM users WHERE role = 'seller'"
    ).fetchall()
    for seller_row in sellers:
        shop = conn.execute(
            "SELECT 1 FROM shops WHERE owner_user_id = ?", (seller_row["user_id"],)
        ).fetchone()
        if not shop:
            shop_name = seller_row["shop_name"] or f"{seller_row['username']}的店铺"
            description = (
                f"主营{seller_row['main_category']}商品。"
                if seller_row["main_category"] else "欢迎来到本店。"
            )
            conn.execute(
                "INSERT INTO shops (owner_user_id, name, description, status, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (seller_row["user_id"], shop_name, description, "active", ts, ts),
            )

    # 保证课程演示账号能直接完成下单流程。
    demo_buyer = conn.execute(
        "SELECT user_id, username, phone FROM users WHERE email = 'student@example.com'"
    ).fetchone()
    if demo_buyer and not conn.execute(
        "SELECT 1 FROM addresses WHERE user_id = ?", (demo_buyer["user_id"],)
    ).fetchone():
        conn.execute(
            "INSERT INTO addresses (user_id, name, phone, detail, is_default, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
            (
                demo_buyer["user_id"], demo_buyer["username"], demo_buyer["phone"] or "13800002026",
                "广东省广州市天河区 Bacon Mall 演示收货地址", 1, ts, ts,
            ),
        )

    seller = conn.execute("SELECT user_id FROM users WHERE role = 'seller' LIMIT 1").fetchone()
    seller_id = seller["user_id"] if seller else None
    shop = conn.execute("SELECT shop_id FROM shops WHERE owner_user_id = ?", (seller_id,)).fetchone() if seller_id else None
    shop_id = shop["shop_id"] if shop else None

    for idx, (name, desc, price, cat, imgs) in enumerate(PRODUCT_SEEDS):
        product_id = 1001 + idx
        product = conn.execute(
            "SELECT product_id FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()
        if not product:
            conn.execute(
                """INSERT INTO products (product_id, seller_id, shop_id, name, description, price, stock, sales_count, status, image_urls, category, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (product_id, seller_id, shop_id, name, desc, price, 0, 0, "active", json.dumps(imgs, ensure_ascii=False), cat, ts, ts),
            )
        total_stock = 0
        total_price = float("inf")
        for ci, color in enumerate(COLORS):
            for vi, (vname, vdelta, sdelta) in enumerate(VERSIONS):
                sku_name = f"{color} · {vname}"
                sku_price = price + vdelta
                sku_stock = max(5, 40 - ci * 8 - sdelta)
                total_stock += sku_stock
                total_price = min(total_price, sku_price)
                existing_sku = conn.execute(
                    "SELECT 1 FROM product_skus WHERE product_id = ? AND name = ?",
                    (product_id, sku_name),
                ).fetchone()
                if not existing_sku:
                    conn.execute(
                        """INSERT INTO product_skus (product_id, sku_code, name, price, stock, image_url, attributes, created_at, updated_at)
                           VALUES (?,?,?,?,?,?,?,?,?)""",
                        (product_id, f"SKU-{product_id}-{ci}-{vi}", sku_name, sku_price, sku_stock, imgs[ci % len(imgs)], json.dumps({"颜色": color, "版本": vname}, ensure_ascii=False), ts, ts),
                    )
        aggregate = conn.execute(
            "SELECT MIN(price) AS min_price, SUM(stock) AS total_stock FROM product_skus WHERE product_id = ?",
            (product_id,),
        ).fetchone()
        conn.execute(
            "UPDATE products SET price = ?, stock = ? WHERE product_id = ?",
            (aggregate["min_price"] or total_price, aggregate["total_stock"] or total_stock, product_id),
        )
