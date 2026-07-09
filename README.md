# Bacon Mall Frontend

“专业实习2”项目前端：基于用户行为日志的电商个性化推荐系统。

当前阶段先完成网页端电商平台的前端可演示闭环，后续再接入 Python + FastAPI、SQLite/MySQL、Hadoop/HDFS 离线推荐计算。

## 技术栈

- Vue 3
- Vite 6
- TypeScript
- Pinia
- Axios

## 已完成的前端功能

- 首页：运营轮播、分类入口、热卖单品、为你精选瀑布流
- 首页推荐：根据浏览、收藏、加购、购买等行为日志动态排序商品
- 商品库：搜索、分类筛选、价格筛选、库存筛选、排序
- 商品详情：商品图片、价格、库存、规格、数量、详情、评价、相关推荐
- 收藏：收藏/取消收藏，并在个人中心展示最近收藏
- 购物车：首页、商品库、详情页加购后真实写入本地购物车
- 结算：购物车选择商品后进入订单确认页
- 支付：前端模拟支付，支付后订单进入“待发货”
- 订单：订单列表、订单详情、待付款/待发货/待收货/已完成/已取消
- 登录注册：本地 mock 登录注册，不依赖后端
- 个人中心：账号信息、订单概览、最近行为、兴趣分类、最近收藏
- 行为日志：本地记录浏览、收藏、取消收藏、加购、购买、结算、支付等行为

## 本地运行

安装依赖：

```bash
npm install
```

启动开发服务器：

```bash
npm run dev -- --host 127.0.0.1
```

浏览器打开：

```text
http://127.0.0.1:5173/
```

构建检查：

```bash
npm run build
```

## 测试账号

```text
邮箱：student@example.com
密码：123456
```

也可以在注册页创建本地 mock 用户。

## 页面入口

```text
/                 首页
/products         商品库
/product/:id      商品详情
/cart             购物车
/checkout         订单确认
/payment/:orderId 模拟支付
/orders           我的订单
/order/:id        订单详情
/profile          个人中心
/login            登录
/register         注册
```

## 本地 Mock 数据

当前前端阶段使用浏览器 `localStorage` 保存数据：

```text
mockUsers            mock 用户
currentUser          当前登录用户
token                mock 登录 token
behaviorLogs         用户行为日志
favoriteProductIds   收藏商品 id
mockCartItems        购物车商品
checkoutDraft        待结算订单草稿
mockOrders           mock 订单
```

## 推荐逻辑

前端当前先实现轻量推荐排序，用于演示“用户行为影响首页内容”：

```text
浏览商品：较低权重
收藏商品：中等权重
加入购物车：较高权重
购买/支付：最高权重
近期行为：有时间加成
```

首页“为你精选”会根据 `behaviorLogs` 中的商品和分类偏好动态排序。后续接入后端和 Hadoop 后，这部分会替换为 FastAPI 返回的推荐结果。

## 后续后端与大数据计划

1. 创建 FastAPI 后端项目
2. 使用 SQLite 建用户、商品、购物车、订单、行为日志表
3. 前端从 localStorage mock 切换到后端接口
4. 后端定期导出用户行为日志
5. 上传日志到 Hadoop HDFS
6. 使用 Hadoop Streaming + Python 计算用户偏好和推荐分数
7. 推荐结果回写数据库
8. FastAPI 提供推荐接口给首页使用

## 项目定位

Hadoop 集群不是数据库，也不是前端运行环境。它在本项目中的作用是存储和批量分析用户行为日志，用来证明项目具备“大数据离线计算 + 个性化推荐”的核心部分。
