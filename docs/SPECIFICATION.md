# Bacon Mall 项目说明书

## 项目信息

| 项目 | 内容 |
|------|------|
| 项目名称 | Bacon Mall — 基于用户行为日志的电商个性化推荐系统 |
| 课程 | 专业实习 2 |
| 技术方向 | 全栈 Web + 大数据离线计算 |
| 代码仓库 | github.com/rongyicheng23-afk/bacon-ecommerce-platform |

---

## 一、项目背景

传统电商平台的推荐系统通常依赖用户行为数据。本项目构建了一个完整的电商闭环，从用户浏览/收藏/加购/购买行为的采集，到 Hadoop 离线计算用户偏好，最终生成个性化推荐并展现在首页。

## 二、系统功能

### 买家端
- 商品浏览（分类、搜索、筛选、排序）
- 商品详情（多 SKU、图片、评价）
- 收藏、购物车、地址管理
- 下单、模拟支付、订单追踪

### 商家端
- 商品管理（创建、编辑、上架/下架）
- 订单处理（发货）
- 数据看板（营收、订单统计）

### 推荐引擎
- 行为日志自动采集（view/search/favorite/cart/purchase）
- JSON Lines 导出 + HDFS 上传
- Hadoop Streaming 离线偏好计算
- 个性化推荐生成 + 结果回写
- 冷启动策略（全站热销兜底）

## 三、技术架构

| 层次 | 技术 | 版本 |
|------|------|------|
| 前端 | Vue 3 + Vite 6 + TypeScript + Pinia | — |
| 后端 | FastAPI + Pydantic | 0.116 |
| 数据库 | SQLite 3 | — |
| 对象存储 | MinIO / 本地文件系统 | 双模 |
| 大数据 | Hadoop 3.x + YARN Streaming | — |
| 计算语言 | Python 3 | 3.12 |

## 四、数据库设计

15 张表，含外键约束、CHECK 约束、UNIQUE 约束、索引。

核心表：users, shops, products, product_skus, cart_items, orders, order_items, favorites, addresses, behavior_logs, recommendation_results, recommendation_runs, categories, sessions

详见 [ARCHITECTURE.md](ARCHITECTURE.md) ER 图。

## 五、推荐算法

```
score = category_preference × 0.5 + product_preference × 0.3 + popularity × 0.2
```

行为权重：view=1, search=2, favorite=3, cart=4, purchase=5

冷启动：新用户推荐全站热销商品。

## 六、项目文件结构

```
bacon-mall-frontend/                # 前端 + 后端 Monorepo
├── src/                            # Vue 3 前端
│   ├── services/                   # API 调用（已对接后端）
│   ├── stores/                     # Pinia 状态管理
│   ├── views/                      # 页面组件
│   └── composables/                # 可组合函数
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── main.py                 # 应用入口
│   │   ├── core/                   # 配置、安全
│   │   ├── db/                     # 数据库模型、种子、迁移
│   │   ├── routers/                # API 路由（9 个模块）
│   │   ├── schemas/                # Pydantic 模型
│   │   └── services/               # 业务逻辑
│   ├── bigdata/                    # Hadoop 推荐引擎
│   │   ├── streaming/              # Mapper/Reducer
│   │   └── scripts/                # 管道脚本
│   └── scripts/                    # 工具脚本
└── docs/                           # 项目文档
```

## 七、启动方式

见 README.md 或 [DEMO.md](DEMO.md)。

## 八、后续扩展方向

- MySQL 数据库切换
- 协同过滤算法
- 实时推荐（Spark Streaming）
- 优惠券/评价系统
