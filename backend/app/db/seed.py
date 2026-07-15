"""种子数据：demo 用户 + 78 商品（与前端 mock 对齐）"""
import json
import sqlite3

from app.core.security import hash_password
from app.db.database import now_iso

PRODUCT_SEEDS = [
    ("无线降噪耳机 Pro", "40dB深度降噪，蓝牙5.3，50小时续航，折叠便携，通勤学习必备", 299, "数码",
     ['https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800', 'https://images.unsplash.com/photo-1550029392-2e0a0a0a0a0a?w=800', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800']),
    ("机械键盘 红轴版", "87键紧凑布局，PBT键帽，RGB背光，USB-C可拆卸连线", 349, "数码",
     ['https://images.unsplash.com/photo-1523275335684-339abb4ab7c3?w=800', 'https://images.unsplash.com/photo-1491637639811-06e6cc62ac3b?w=800', 'https://images.unsplash.com/photo-1533090161767-e55e38f0d180?w=800']),
    ("人体工学无线鼠标", "垂直握持设计，DPI五档调节，蓝牙+2.4G双模，充电款", 159, "数码",
     ['https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=800', 'https://images.unsplash.com/photo-1560343090-f0409e92791a?w=800', 'https://images.unsplash.com/photo-1546868871-af0de0ae72be?w=800']),
    ("20000mAh快充移动电源", "22.5W快充输出，LED电量显示，轻薄机身，飞机可携带", 139, "数码",
     ['https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=800', 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800', 'https://images.unsplash.com/photo-1527443224157-49a85947c04b?w=800']),
    ("1080P高清摄像头", "自动对焦，内置降噪麦克风，即插即用，隐私镜头盖", 189, "数码",
     ['https://images.unsplash.com/photo-1494698851510-8d6c8d7b27e2?w=800', 'https://images.unsplash.com/photo-1461151730306-3c31e6a44cd4?w=800', 'https://images.unsplash.com/photo-1468495244123-6c6c332eee6e?w=800']),
    ("智能运动手环", "心率血氧监测，50米防水，14天续航，多运动模式", 249, "数码",
     ['https://images.unsplash.com/photo-1541807084-5d4e2f8c9e5f?w=800', 'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800', 'https://images.unsplash.com/photo-1598532163257-ae3c6b2524b6?w=800']),
    ("铝合金平板支架", "可折叠多角度，防滑硅胶垫，兼容4-13寸设备", 89, "数码",
     ['https://images.unsplash.com/photo-1549495118-6e4c2c9e9e5b?w=800', 'https://images.unsplash.com/photo-1526406915898-13f7f6c6c6c6?w=800', 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800']),
    ("GaN 65W三口充电器", "氮化镓超小体积，2C1A三接口，支持笔记本快充", 129, "数码",
     ['https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800', 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800', 'https://images.unsplash.com/photo-1498049794561-ecb9e0e3d247?w=800']),
    ("USB-C 七合一扩展坞", "HDMI 4K@60Hz，USB 3.0×3，SD/TF读卡，PD 100W", 229, "数码",
     ['https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800', 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800', 'https://images.unsplash.com/photo-1526379096198-a3e3e3e3e3e3?w=800']),
    ("蓝牙便携音箱", "IPX7防水，20小时续航，TWS串联立体声，户外派对必备", 179, "数码",
     ['https://images.unsplash.com/photo-1518770660439-4636190af475?w=800', 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800', 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800']),
    ("防蓝光护目眼镜", "阻隔90%有害蓝光，超轻TR90镜框，适合长时间屏幕办公", 79, "数码",
     ['https://images.unsplash.com/photo-1488590528505-98d2b5c09dc0?w=800', 'https://images.unsplash.com/photo-1531746790096-70828c1e7e4e?w=800', 'https://images.unsplash.com/photo-1568952433726-3896e4c1c3a0?w=800']),
    ("无线投屏器", "即插即投，手机/笔记本→电视/投影仪，1080P高清", 109, "数码",
     ['https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800', 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800', 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800']),
    ("通勤双肩背包", "大容量防泼水，多隔层收纳，透气背板，适合日常出行", 169, "服饰",
     ['https://images.unsplash.com/photo-1551434678-e076c7b83f3b?w=800', 'https://images.unsplash.com/photo-1507207611509-ec012433ff52?w=800', 'https://images.unsplash.com/photo-1434626881859-194d67b2b370?w=800']),
    ("经典帆布鞋 低帮", "复古百搭款，透气帆布面料，橡胶防滑大底，男女同款", 149, "服饰",
     ['https://images.unsplash.com/photo-1496902526515-1e6c1c1c1c1c?w=800', 'https://images.unsplash.com/photo-1542744094-3a3a3a3a3a3a?w=800', 'https://images.unsplash.com/photo-1580894732444-8ecded7900cd?w=800']),
    ("加绒连帽卫衣", "320g纯棉加绒，宽松落肩版型，秋冬保暖百搭", 139, "服饰",
     ['https://images.unsplash.com/photo-1515378960530-7c0da6231fb1?w=800', 'https://images.unsplash.com/photo-1580894894513-3d2e3e3e3e3e?w=800', 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800']),
    ("纯棉短袖T恤 两件装", "200g重磅纯棉，宽松版型，黑白两色，不起球不缩水", 89, "服饰",
     ['https://images.unsplash.com/photo-1517430816452-9f1c1c1c1c1c?w=800', 'https://images.unsplash.com/photo-1551645120-dee2d0f0f0f0?w=800', 'https://images.unsplash.com/photo-1499951360447-b1c1c1c1c1c1?w=800']),
    ("羊毛混纺围巾", "含30%羊毛，柔软亲肤，190×65cm大尺寸，秋冬保暖", 89, "服饰",
     ['https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800', 'https://images.unsplash.com/photo-1560472355-b66ff0c44a44?w=800', 'https://images.unsplash.com/photo-1571171637578-41b7c1c1c1c1?w=800']),
    ("商务休闲长裤", "弹力免烫面料，修身版型，适合通勤和商务场合", 179, "服饰",
     ['https://images.unsplash.com/photo-1581091226825-b3e3e3e3e3e3?w=800', 'https://images.unsplash.com/photo-1483058712412-424242424242?w=800', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800']),
    ("轻薄防晒衣 UPF50+", "超轻可收纳，透气速干，连帽设计，夏季户外必备", 139, "服饰",
     ['https://images.unsplash.com/photo-1587654780291-6e6e6e6e6e6e?w=800', 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800', 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800']),
    ("精梳棉袜 5双装", "新疆长绒棉，透气吸汗，弹力袜口不勒脚，男女通用", 35, "服饰",
     ['https://images.unsplash.com/photo-1593642532744-d377ab51f447?w=800', 'https://images.unsplash.com/photo-1544829728-e5e5e5e5e5e5?w=800', 'https://images.unsplash.com/photo-1572569511251-b128bc965b9b?w=800']),
    ("头层牛皮自动扣皮带", "商务休闲两用，合金扣头，可裁剪长度，礼盒装", 119, "服饰",
     ['https://images.unsplash.com/photo-1621607512214-6e6e6e6e6e6e?w=800', 'https://images.unsplash.com/photo-1581235720204-6e6e6e6e6e6e?w=800', 'https://images.unsplash.com/photo-0062-unique-bacon-mall?w=800']),
    ("轻便跑鞋 飞织面", "透气飞织鞋面，EVA缓震中底，橡胶防滑大底", 229, "服饰",
     ['https://images.unsplash.com/photo-0063-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0064-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0065-unique-bacon-mall?w=800']),
    ("防晒冰袖 两双装", "UPF50+物理防晒，冰感面料，弹力无痕，夏季户外", 19, "服饰",
     ['https://images.unsplash.com/photo-0066-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0067-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0068-unique-bacon-mall?w=800']),
    ("帆布腰带 无孔款", "自动扣设计，休闲百搭，适合牛仔裤和休闲裤", 49, "服饰",
     ['https://images.unsplash.com/photo-0069-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0070-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0071-unique-bacon-mall?w=800']),
    ("LED护眼台灯", "三档色温无极调光，无频闪防蓝光，USB供电，适合阅读办公", 159, "家居",
     ['https://images.unsplash.com/photo-0072-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0073-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0074-unique-bacon-mall?w=800']),
    ("316不锈钢保温杯 500ml", "12小时保温保冷，食品级材质，车载杯型，多色可选", 89, "家居",
     ['https://images.unsplash.com/photo-0075-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0076-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0077-unique-bacon-mall?w=800']),
    ("超声波香薰加湿器 500ml", "静音加湿，自动断电，七彩氛围灯，可加精油", 99, "家居",
     ['https://images.unsplash.com/photo-0078-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0079-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0080-unique-bacon-mall?w=800']),
    ("全棉床笠三件套 1.5m", "100%纯棉，弹力包裹床垫，含床笠+枕套×2", 199, "家居",
     ['https://images.unsplash.com/photo-0081-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0082-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0083-unique-bacon-mall?w=800']),
    ("多层实木置物架", "北欧风格，三层开放设计，承重15kg，客厅书房通用", 279, "家居",
     ['https://images.unsplash.com/photo-0084-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0085-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0086-unique-bacon-mall?w=800']),
    ("记忆棉办公坐垫", "慢回弹记忆棉，中空透气，矫正坐姿，久坐不累", 79, "家居",
     ['https://images.unsplash.com/photo-0087-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0088-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0089-unique-bacon-mall?w=800']),
    ("全遮光隔热窗帘 1.5×2.4m", "三层梭织面料，遮光率99%，隔音隔热，含挂钩", 139, "家居",
     ['https://images.unsplash.com/photo-0090-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0091-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0092-unique-bacon-mall?w=800']),
    ("可升降移动电脑桌", "气动升降72-115cm，万向滚轮带刹车，站坐两用", 399, "家居",
     ['https://images.unsplash.com/photo-0093-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0094-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0095-unique-bacon-mall?w=800']),
    ("收纳箱三件套 66L", "可折叠牛津布+钢架，大容量，前开口设计方便取物", 99, "家居",
     ['https://images.unsplash.com/photo-0096-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0097-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0098-unique-bacon-mall?w=800']),
    ("浴室防滑垫 40×70cm", "硅藻泥吸水速干，底部防滑，可机洗，多色可选", 49, "家居",
     ['https://images.unsplash.com/photo-0099-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0100-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0101-unique-bacon-mall?w=800']),
    ("珊瑚绒午休毯 150×200cm", "超柔法兰绒，办公室空调毯，沙发追剧好伴侣", 69, "家居",
     ['https://images.unsplash.com/photo-0102-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0103-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0104-unique-bacon-mall?w=800']),
    ("加厚防滑瑜伽垫 10mm", "TPE环保材质，双面防滑纹理，含收纳绑带+背包", 89, "运动",
     ['https://images.unsplash.com/photo-0105-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0106-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0107-unique-bacon-mall?w=800']),
    ("无绳负重跳绳", "配重球设计模拟真实手感，室内静音，液晶计数显示", 45, "运动",
     ['https://images.unsplash.com/photo-0108-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0109-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0110-unique-bacon-mall?w=800']),
    ("速干运动T恤 男款", "透气速干面料，四针六线无骨缝制，反光LOGO", 79, "运动",
     ['https://images.unsplash.com/photo-0111-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0112-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0113-unique-bacon-mall?w=800']),
    ("弹簧支撑运动护膝 一对", "四根弹簧支撑，硅胶防滑条，篮球跑步健身适用", 69, "运动",
     ['https://images.unsplash.com/photo-0114-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0115-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0116-unique-bacon-mall?w=800']),
    ("Tritan运动水壶 750ml", "BPA-free材质，弹盖一键开启，防漏锁扣，健身携带", 55, "运动",
     ['https://images.unsplash.com/photo-0117-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0118-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0119-unique-bacon-mall?w=800']),
    ("全碳素羽毛球拍 一对", "碳纤维材质85g超轻，已穿线，含球拍包+3只球", 189, "运动",
     ['https://images.unsplash.com/photo-0120-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0121-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0122-unique-bacon-mall?w=800']),
    ("弹力带套装 5阻力级", "天然乳胶材质，5条不同阻力，含收纳袋+训练指南", 35, "运动",
     ['https://images.unsplash.com/photo-0123-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0124-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0125-unique-bacon-mall?w=800']),
    ("可折叠铝合金登山杖", "7075铝合金，三节伸缩，EVA握把，含杖尖保护套", 149, "运动",
     ['https://images.unsplash.com/photo-0126-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0127-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0128-unique-bacon-mall?w=800']),
    ("超薄隐形运动腰包", "防水面料，双拉链设计，可放手机钥匙，跑步不晃动", 29, "运动",
     ['https://images.unsplash.com/photo-0129-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0130-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0131-unique-bacon-mall?w=800']),
    ("防雾泳镜 高清款", "双层防雾镜片，UV防护，硅胶密封圈，可调节鼻架", 79, "运动",
     ['https://images.unsplash.com/photo-0132-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0133-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0134-unique-bacon-mall?w=800']),
    ("透气健身手套 半指款", "掌心加厚缓震，透气网眼面料，触屏指尖，引体向上", 39, "运动",
     ['https://images.unsplash.com/photo-0135-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0136-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0137-unique-bacon-mall?w=800']),
    ("明前龙井绿茶 250g礼盒", "杭州原产明前采摘，一芽一叶，栗香回甘，送礼自饮皆可", 168, "食品",
     ['https://images.unsplash.com/photo-0138-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0139-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0140-unique-bacon-mall?w=800']),
    ("72%黑巧克力 12片礼盒", "比利时进口可可豆，丝滑醇厚，独立包装，办公室零食", 79, "食品",
     ['https://images.unsplash.com/photo-0141-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0142-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0143-unique-bacon-mall?w=800']),
    ("澳洲进口即食燕麦片 1kg", "高纤维低脂肪，免煮即食，健身减脂早餐", 49, "食品",
     ['https://images.unsplash.com/photo-0144-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0145-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0146-unique-bacon-mall?w=800']),
    ("新疆红枣枸杞茶 30包", "独立三角包，和田红枣+宁夏枸杞，养生暖宫", 49, "食品",
     ['https://images.unsplash.com/photo-0147-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0148-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0149-unique-bacon-mall?w=800']),
    ("云南小粒速溶黑咖啡 50条", "冻干技术保留原香，冷热水即溶，零糖零脂", 69, "食品",
     ['https://images.unsplash.com/photo-0150-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0151-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0152-unique-bacon-mall?w=800']),
    ("内蒙古风干牛肉干 250g", "精选牛后腿肉，传统五香口味，独立小包装", 65, "食品",
     ['https://images.unsplash.com/photo-0153-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0154-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0155-unique-bacon-mall?w=800']),
    ("手冲咖啡套装 入门款", "玻璃分享壶+陶瓷滤杯+不锈钢滤网+量勺", 239, "食品",
     ['https://images.unsplash.com/photo-0156-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0157-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0158-unique-bacon-mall?w=800']),
    ("混合坚果礼盒 1.2kg 6罐", "夏威夷果+碧根果+腰果+开心果+巴旦木+核桃", 199, "食品",
     ['https://images.unsplash.com/photo-0159-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0160-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0161-unique-bacon-mall?w=800']),
    ("蒟蒻果冻 0脂低卡 12枚", "果汁含量≥25%，葡萄+白桃+荔枝三口味，办公室零食", 29, "食品",
     ['https://images.unsplash.com/photo-0162-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0163-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0164-unique-bacon-mall?w=800']),
    ("全麦面包粉 高筋套装 1kg", "高筋粉+全麦粉+酵母三件套，家庭烘焙入门", 39, "食品",
     ['https://images.unsplash.com/photo-0165-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0166-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0167-unique-bacon-mall?w=800']),
    ("新西兰麦卢卡蜂蜜 UMF10+", "原装进口，天然纯正无添加，250g玻璃罐装", 279, "食品",
     ['https://images.unsplash.com/photo-0168-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0169-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0170-unique-bacon-mall?w=800']),
    ("氨基酸温和洁面乳 120g", "弱酸性配方，泡沫细腻丰富，洗后不紧绷，适合所有肤质", 69, "美妆",
     ['https://images.unsplash.com/photo-0171-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0172-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0173-unique-bacon-mall?w=800']),
    ("清爽防晒霜 SPF50+ PA++++", "物理+化学双重防晒，清爽不油腻，面部全身通用 60ml", 99, "美妆",
     ['https://images.unsplash.com/photo-0174-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0175-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0176-unique-bacon-mall?w=800']),
    ("丝绒哑光口红三支套装", "豆沙色+正红+橘棕，显白不挑皮，滋润不拔干", 109, "美妆",
     ['https://images.unsplash.com/photo-0177-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0178-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0179-unique-bacon-mall?w=800']),
    ("神经酰胺保湿面霜 50g", "修护皮肤屏障，深层锁水，适合干性和敏感肌", 139, "美妆",
     ['https://images.unsplash.com/photo-0180-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0181-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0182-unique-bacon-mall?w=800']),
    ("玻尿酸补水面膜 20片装", "三重玻尿酸精华，蚕丝膜布，每日一片水润透亮", 59, "美妆",
     ['https://images.unsplash.com/photo-0183-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0184-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0185-unique-bacon-mall?w=800']),
    ("烟酰胺亮肤精华液 30ml", "5%烟酰胺+维C衍生物，淡化痘印提亮肤色", 169, "美妆",
     ['https://images.unsplash.com/photo-0186-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0187-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0188-unique-bacon-mall?w=800']),
    ("12色大地玫瑰眼影盘", "哑光+珠光+闪片三质地主，显色服帖，日常通勤百搭", 79, "美妆",
     ['https://images.unsplash.com/photo-0189-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0190-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0191-unique-bacon-mall?w=800']),
    ("三合一温和卸妆水 500ml", "眼唇面部通用，无油配方，敏感肌可用，大瓶实惠", 49, "美妆",
     ['https://images.unsplash.com/photo-0192-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0193-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0194-unique-bacon-mall?w=800']),
    ("极细双头眉笔 防水持久", "0.5mm极细笔芯，自带眉刷，三色可选，新手友好", 29, "美妆",
     ['https://images.unsplash.com/photo-0195-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0196-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0197-unique-bacon-mall?w=800']),
    ("香氛氨基酸沐浴露 500ml", "持久留香12小时，温和清洁不假滑，泡沫绵密", 59, "美妆",
     ['https://images.unsplash.com/photo-0198-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0199-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0200-unique-bacon-mall?w=800']),
    ("男士控油洁面套装 三件套", "洁面乳+爽肤水+保湿乳，控油清爽适合油性肌肤", 149, "美妆",
     ['https://images.unsplash.com/photo-0201-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0202-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0203-unique-bacon-mall?w=800']),
    ("《深入理解计算机系统》原书第3版", "CS经典黑皮书，全面讲解系统底层原理，程序员必读", 139, "图书",
     ['https://images.unsplash.com/photo-0204-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0205-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0206-unique-bacon-mall?w=800']),
    ("《算法导论》原书第4版", "MIT经典教材，全面覆盖算法设计与分析，程序员面试必备", 128, "图书",
     ['https://images.unsplash.com/photo-0207-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0208-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0209-unique-bacon-mall?w=800']),
    ("《设计模式：可复用面向对象软件的基础》", "GoF四人帮经典，23种设计模式详解，软件工程里程碑", 79, "图书",
     ['https://images.unsplash.com/photo-0210-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0211-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0212-unique-bacon-mall?w=800']),
    ("《JavaScript高级程序设计》第4版", "前端红宝书，ES6+全面讲解，Web开发者必读", 99, "图书",
     ['https://images.unsplash.com/photo-0213-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0214-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0215-unique-bacon-mall?w=800']),
    ("《Python编程：从入门到实践》第3版", "零基础学Python，含数据可视化+Django Web项目实战", 89, "图书",
     ['https://images.unsplash.com/photo-0216-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0217-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0218-unique-bacon-mall?w=800']),
    ("《人性的弱点》全集", "戴尔·卡耐基经典人际关系著作，提升沟通与情商", 35, "图书",
     ['https://images.unsplash.com/photo-0219-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0220-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0221-unique-bacon-mall?w=800']),
    ("《思考，快与慢》", "诺贝尔经济学奖得主丹尼尔·卡尼曼，探索人类认知偏差", 69, "图书",
     ['https://images.unsplash.com/photo-0222-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0223-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0224-unique-bacon-mall?w=800']),
    ("《三体》全集 典藏版", "刘慈欣科幻巨著三部曲，雨果奖获奖作品，中国科幻巅峰", 99, "图书",
     ['https://images.unsplash.com/photo-0225-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0226-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0227-unique-bacon-mall?w=800']),
    ("《百年孤独》50周年纪念版", "加西亚·马尔克斯魔幻现实主义经典，拉美文学巅峰", 55, "图书",
     ['https://images.unsplash.com/photo-0228-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0229-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0230-unique-bacon-mall?w=800']),
    ("《小王子》中英法三语珍藏版", "圣埃克苏佩里永恒经典，精装全彩插图，适合全年龄", 39, "图书",
     ['https://images.unsplash.com/photo-0231-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0232-unique-bacon-mall?w=800', 'https://images.unsplash.com/photo-0233-unique-bacon-mall?w=800']),
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
