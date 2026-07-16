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

管道的 6 个步骤：
1. 导出未导出过的行为日志 → JSONL
2. 上传 HDFS（本地模式跳过）
3. 计算用户分类/商品偏好分数
4. 生成推荐结果 TSV 文件
5. 将推荐结果导入 SQLite 的 `recommendation_results` 表
6. 记录运行日志到 `recommendation_runs` 表

## Hadoop 集群运行

后端和 SQLite 在 Mac、Hadoop 在 `master` 虚拟机时，从 Mac 的 `backend/` 目录执行：

```bash
source .venv/bin/activate
bash bigdata/scripts/run_pipeline.sh hadoop-remote
```

该模式会自动把 JSONL 日志与 Streaming 脚本传到 `root@127.0.0.1:2222` 的 `master`，在 HDFS/YARN 上运行两个作业，再把聚合结果取回 Mac 导入 SQLite。可用环境变量覆盖默认连接：`HADOOP_SSH_TARGET`、`HADOOP_SSH_PORT`、`HADOOP_REMOTE_DIR`。

如果是在已经同时具备 Hadoop 客户端和 SQLite 数据库的机器上运行，才使用：

```bash
# 确保 Hadoop 集群已启动
bash bigdata/scripts/run_pipeline.sh hadoop
```

## 每日自动运行（macOS）

本项目已为当前 Mac 注册 `com.bacon-mall.recommendation` 的 LaunchAgent：每天 `02:00` 自动运行 `backend/scripts/run_scheduled_recommendation.sh`，等价于执行：

```bash
bash bigdata/scripts/run_pipeline.sh hadoop-remote
```

执行日志位于 `backend/logs/recommendation-pipeline.log`，错误日志位于 `backend/logs/recommendation-pipeline-error.log`。同一时间只允许一个任务运行，避免重复计算。

自动任务运行前，Mac 必须已开机并登录，三台 Hadoop 虚拟机和 Hadoop 集群也必须处于运行状态；否则本次任务会失败并把原因写入错误日志。需要立刻手动触发一次时，可执行：

```bash
launchctl kickstart -k gui/$(id -u)/com.bacon-mall.recommendation
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
