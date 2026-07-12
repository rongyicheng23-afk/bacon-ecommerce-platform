# Bacon Mall — 大数据推荐引擎

基于 Hadoop Streaming + Python 的离线推荐系统。

## 架构

```
行为日志 (SQLite)
    ↓ export_behaviors.py
JSONL 文件 (exports/)
    ↓ upload_to_hdfs.sh
HDFS (/bacon-mall/raw/behavior/)
    ↓ Hadoop Streaming
用户偏好 (HDFS /bacon-mall/warehouse/)
    ↓ generate_recommendations.py
推荐结果 (recommendation_results 表)
    ↓ FastAPI GET /api/recommendations
前端首页 "为你精选"
```

## 目录

```
bigdata/
├── streaming/
│   ├── category_preference_mapper.py   # Map: 日志 → user|category → weight
│   ├── category_preference_reducer.py  # Reduce: 聚合 user×category 分数
│   ├── product_preference_mapper.py    # Map: 日志 → user|product → weight
│   ├── product_preference_reducer.py   # Reduce: 聚合 user×product 分数
│   └── generate_recommendations.py     # 生成推荐 + 写入 DB
├── scripts/
│   ├── upload_to_hdfs.sh               # 上传 JSONL → HDFS
│   ├── run_pipeline.sh                 # 一键运行完整管道
│   └── import_results.py               # 导入推荐结果 TSV → SQLite
└── README.md
```

## 本地运行（不需要 Hadoop）

```bash
cd backend && source .venv/bin/activate

# 1. 导出行为日志
python scripts/export_behaviors.py

# 2. 运行完整管道（本地模式）
bash bigdata/scripts/run_pipeline.sh local
```

管道的 5 个步骤：
1. 导出未导出过的行为日志 → JSONL
2. 上传 HDFS（本地模式跳过）
3. 计算用户分类/商品偏好分数
4. 生成推荐结果，写入 recommendation_results 表
5. 记录运行日志到 recommendation_runs 表

## Hadoop 集群运行

```bash
# 确保 Hadoop 集群已启动
bash bigdata/scripts/run_pipeline.sh hadoop
```

## 推荐算法

```
recommend_score = category_preference × 0.5 + product_preference × 0.3 + popularity × 0.2
```

行为权重:
- view=1, search=2, favorite=3, cart=4, purchase=5

冷启动: 新用户推荐全站热销商品（按 sales_count 排序）。

## 结果验证

```sql
-- 查看推荐结果
SELECT u.username, p.name, r.score, r.reason_code
FROM recommendation_results r
JOIN users u ON u.user_id = r.user_id
JOIN products p ON p.product_id = r.product_id
WHERE r.batch_date = '2026-07-12'
ORDER BY r.user_id, r.rank_no
LIMIT 20;
```
