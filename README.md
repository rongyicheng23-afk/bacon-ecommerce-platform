# Bacon's E-commerce Platform

基于大数据分析的电商个性化推荐系统。

本项目用于“专业实习2”，目标是实现一个网页端电商平台，并通过用户行为日志、Hadoop 离线计算和推荐结果回写，展示完整的个性化推荐流程。

## 项目定位

项目不是简单商品展示页，而是参考京东、淘宝、抖音商城等平台的电商业务链路，逐步实现：

- 首页运营位、分类入口、热卖商品和个性化推荐
- 商品搜索、分类筛选和排序
- 商品详情、收藏、加购、购买
- 购物车、订单、支付结果
- 用户行为日志采集
- Hadoop/HDFS 离线分析用户偏好
- FastAPI 返回推荐结果给前端展示

## 技术栈

前端：

- Vue 3
- Vite
- TypeScript
- Pinia
- Axios

后端计划：

- Python
- FastAPI
- SQLite，后续可替换 MySQL

大数据环境：

- CentOS 7 QEMU 虚拟机集群
- Hadoop 3.3.0
- HDFS
- YARN
- MapReduce / Hadoop Streaming + Python

## 当前进度

已完成：

- 前端项目构建通过
- 首页电商化改造
- 商品发现页 `/products`
- 商品搜索、分类筛选、排序
- Mock 商品数据
- 用户行为本地记录，包括浏览、收藏、加购、购买
- 订单字段 TypeScript 命名修复

进行中：

- 按京东式电商平台结构继续完善页面
- 商品详情页重做
- 购物车和订单流程优化

后续计划：

- 新建 FastAPI 后端
- SQLite 建表
- 前端接口切换到后端
- 用户行为写入数据库和日志文件
- 行为日志上传 HDFS
- Hadoop Streaming 计算用户偏好
- 推荐结果回写数据库并展示到首页

## 推荐系统设计

用户行为包括：

- 浏览商品
- 搜索商品
- 收藏商品
- 加入购物车
- 购买商品

行为权重初步设计：

```text
浏览：1
搜索：1
收藏：3
加购：5
购买：8
```

离线推荐思路：

```text
用户行为日志 -> 上传 HDFS -> Hadoop Streaming 分析用户偏好分类 -> 生成推荐商品 -> FastAPI 读取推荐结果 -> 前端展示
```

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

## 页面入口

```text
/              首页
/products      商品发现页
/product/:id   商品详情页
/cart          购物车
/orders        我的订单
/login         登录
/register      注册
```

## 项目说明

本项目用于专业实习课程，前端已围绕“大数据分析 + 电商推荐系统”的方向完成业务化改造。后续会持续扩展 FastAPI 后端、SQLite/MySQL 数据库、用户行为日志采集和 Hadoop 离线推荐能力。
