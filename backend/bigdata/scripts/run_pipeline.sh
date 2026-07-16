#!/bin/bash
# === Bacon Mall 推荐管道 ===
# 完整流程: 导出日志 → 计算偏好 → 生成推荐 → 导入数据库
#
# 用法:
#   本地模式:  bash run_pipeline.sh local
#   Hadoop模式（在 master 上运行）: bash run_pipeline.sh hadoop
#   远程 Hadoop 模式（在 Mac 上运行）: bash run_pipeline.sh hadoop-remote
#
set -e

MODE="${1:-local}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")/.."
STREAMING_DIR="${ROOT_DIR}/bigdata/streaming"
EXPORT_DIR="${ROOT_DIR}/exports"

# 从 .env 读取数据库路径，否则用默认值
if [ -f "${ROOT_DIR}/.env" ]; then
    DB_PATH=$(grep -E '^BACON_DB_PATH=' "${ROOT_DIR}/.env" | head -1 | sed 's/^BACON_DB_PATH=//' | xargs)
fi
DB_PATH="${DB_PATH:-${ROOT_DIR}/bacon_mall.db}"
BATCH_DATE="$(date +%Y-%m-%d)"
HADOOP_SSH_TARGET="${HADOOP_SSH_TARGET:-root@127.0.0.1}"
HADOOP_SSH_PORT="${HADOOP_SSH_PORT:-2222}"
HADOOP_REMOTE_DIR="${HADOOP_REMOTE_DIR:-/tmp/bacon-mall-hadoop}"

echo "========================================"
echo "  Bacon Mall 推荐管道"
echo "  模式: ${MODE}"
echo "  日期: ${BATCH_DATE}"
echo "========================================"

# Step 1: 导出行为日志
echo ""
echo "[1/6] 导出行为日志..."
cd "${ROOT_DIR}"
python scripts/export_behaviors.py
INPUT_FILE="${EXPORT_DIR}/behavior-${BATCH_DATE}.jsonl"

if [ ! -f "${INPUT_FILE}" ]; then
    echo "⚠️  今日无新日志，尝试使用最新导出文件..."
    INPUT_FILE=$(ls -t "${EXPORT_DIR}"/behavior-*.jsonl 2>/dev/null | head -1)
fi

if [ -z "${INPUT_FILE}" ] || [ ! -f "${INPUT_FILE}" ]; then
    echo "❌ 没有可用的行为日志文件"
    exit 1
fi

# 从文件名提取实际日期（用于 HDFS 路径）
ACTUAL_DATE=$(basename "${INPUT_FILE}" .jsonl | sed 's/behavior-//')
echo "   输入: ${INPUT_FILE} ($(wc -l < "${INPUT_FILE}") 条)  实际日期: ${ACTUAL_DATE}"

# Step 2: 上传 HDFS（仅 Hadoop 模式）
if [ "${MODE}" = "hadoop" ]; then
    echo ""
    echo "[2/6] 上传 HDFS..."
    bash "${SCRIPT_DIR}/upload_to_hdfs.sh" "${ACTUAL_DATE}"
elif [ "${MODE}" = "hadoop-remote" ]; then
    echo ""
    echo "[2/6] 上传 HDFS（通过 ${HADOOP_SSH_TARGET}:${HADOOP_SSH_PORT}）..."
    ssh -p "${HADOOP_SSH_PORT}" "${HADOOP_SSH_TARGET}" "mkdir -p '${HADOOP_REMOTE_DIR}'"
    scp -P "${HADOOP_SSH_PORT}" \
        "${INPUT_FILE}" \
        "${STREAMING_DIR}/category_preference_mapper.py" \
        "${STREAMING_DIR}/category_preference_reducer.py" \
        "${STREAMING_DIR}/product_preference_mapper.py" \
        "${STREAMING_DIR}/product_preference_reducer.py" \
        "${HADOOP_SSH_TARGET}:${HADOOP_REMOTE_DIR}/"
    ssh -p "${HADOOP_SSH_PORT}" "${HADOOP_SSH_TARGET}" "
        export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
        export HADOOP_HOME=/opt/module/hadoop-3.3.0
        export PATH=\$PATH:\$HADOOP_HOME/bin
        hadoop fs -mkdir -p /bacon-mall/raw/behavior/date=${ACTUAL_DATE}
        hadoop fs -put -f '${HADOOP_REMOTE_DIR}/$(basename "${INPUT_FILE}")' /bacon-mall/raw/behavior/date=${ACTUAL_DATE}/part-00000.jsonl
    "
else
    echo ""
    echo "[2/6] 上传 HDFS — 跳过（本地模式）"
fi

# Step 3: 计算偏好（本地管道或 Hadoop Streaming）
echo ""
echo "[3/6] 计算用户偏好..."
TMP_DIR="${ROOT_DIR}/tmp_recommendation"
mkdir -p "${TMP_DIR}"

if [ "${MODE}" = "hadoop" ]; then
    # Hadoop Streaming 模式
    HDFS_INPUT="/bacon-mall/raw/behavior/date=${ACTUAL_DATE}"
    HDFS_CAT_OUT="/bacon-mall/warehouse/user_category_scores/date=${ACTUAL_DATE}"
    HDFS_PROD_OUT="/bacon-mall/warehouse/user_product_scores/date=${ACTUAL_DATE}"

    # 删除旧输出目录（Hadoop 要求输出目录不存在）
    hadoop fs -rm -r -skipTrash "${HDFS_CAT_OUT}" 2>/dev/null || true
    hadoop fs -rm -r -skipTrash "${HDFS_PROD_OUT}" 2>/dev/null || true

    # 用户分类偏好
    hadoop jar "${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-streaming-*.jar" \
        -input "${HDFS_INPUT}" \
        -output "${HDFS_CAT_OUT}" \
        -mapper "python3 category_preference_mapper.py" \
        -reducer "python3 category_preference_reducer.py" \
        -file "${STREAMING_DIR}/category_preference_mapper.py" \
        -file "${STREAMING_DIR}/category_preference_reducer.py" || {
            echo "❌ Hadoop 分类偏好任务失败"
            exit 1
        }

    hadoop fs -getmerge "${HDFS_CAT_OUT}" "${TMP_DIR}/category_scores.txt"

    # 用户商品偏好
    hadoop jar "${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-streaming-*.jar" \
        -input "${HDFS_INPUT}" \
        -output "${HDFS_PROD_OUT}" \
        -mapper "python3 product_preference_mapper.py" \
        -reducer "python3 product_preference_reducer.py" \
        -file "${STREAMING_DIR}/product_preference_mapper.py" \
        -file "${STREAMING_DIR}/product_preference_reducer.py"

    hadoop fs -getmerge "${HDFS_PROD_OUT}" "${TMP_DIR}/product_scores.txt"
elif [ "${MODE}" = "hadoop-remote" ]; then
    HDFS_INPUT="/bacon-mall/raw/behavior/date=${ACTUAL_DATE}"
    HDFS_CAT_OUT="/bacon-mall/warehouse/user_category_scores/date=${ACTUAL_DATE}"
    HDFS_PROD_OUT="/bacon-mall/warehouse/user_product_scores/date=${ACTUAL_DATE}"

    ssh -p "${HADOOP_SSH_PORT}" "${HADOOP_SSH_TARGET}" "
        set -e
        export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
        export HADOOP_HOME=/opt/module/hadoop-3.3.0
        export PATH=\$PATH:\$HADOOP_HOME/bin
        STREAMING_JAR=\$(find \$HADOOP_HOME/share/hadoop/tools/lib -name 'hadoop-streaming-*.jar' | head -1)
        hadoop fs -rm -r -skipTrash '${HDFS_CAT_OUT}' 2>/dev/null || true
        hadoop fs -rm -r -skipTrash '${HDFS_PROD_OUT}' 2>/dev/null || true
        hadoop jar \$STREAMING_JAR \\
          -input '${HDFS_INPUT}' -output '${HDFS_CAT_OUT}' \\
          -mapper 'python3 category_preference_mapper.py' -reducer 'python3 category_preference_reducer.py' \\
          -file '${HADOOP_REMOTE_DIR}/category_preference_mapper.py' \\
          -file '${HADOOP_REMOTE_DIR}/category_preference_reducer.py'
        hadoop jar \$STREAMING_JAR \\
          -input '${HDFS_INPUT}' -output '${HDFS_PROD_OUT}' \\
          -mapper 'python3 product_preference_mapper.py' -reducer 'python3 product_preference_reducer.py' \\
          -file '${HADOOP_REMOTE_DIR}/product_preference_mapper.py' \\
          -file '${HADOOP_REMOTE_DIR}/product_preference_reducer.py'
        hadoop fs -getmerge '${HDFS_CAT_OUT}' '${HADOOP_REMOTE_DIR}/category_scores.txt'
        hadoop fs -getmerge '${HDFS_PROD_OUT}' '${HADOOP_REMOTE_DIR}/product_scores.txt'
    "
    scp -P "${HADOOP_SSH_PORT}" \
        "${HADOOP_SSH_TARGET}:${HADOOP_REMOTE_DIR}/category_scores.txt" \
        "${HADOOP_SSH_TARGET}:${HADOOP_REMOTE_DIR}/product_scores.txt" \
        "${TMP_DIR}/"
else
    # 本地管道模式
    python3 "${STREAMING_DIR}/category_preference_mapper.py" < "${INPUT_FILE}" | sort | python3 "${STREAMING_DIR}/category_preference_reducer.py" > "${TMP_DIR}/category_scores.txt"
    echo "   分类偏好: $(wc -l < "${TMP_DIR}/category_scores.txt") 行"

    python3 "${STREAMING_DIR}/product_preference_mapper.py" < "${INPUT_FILE}" | sort | python3 "${STREAMING_DIR}/product_preference_reducer.py" > "${TMP_DIR}/product_scores.txt"
    echo "   商品偏好: $(wc -l < "${TMP_DIR}/product_scores.txt") 行"
fi

# Step 4: 生成推荐
echo ""
echo "[4/6] 生成推荐结果..."
python3 "${STREAMING_DIR}/generate_recommendations.py" \
    --db "${DB_PATH}" \
    --category-scores "${TMP_DIR}/category_scores.txt" \
    --product-scores "${TMP_DIR}/product_scores.txt" \
    --output "${TMP_DIR}/recommendations.txt" \
    --batch-date "${BATCH_DATE}" \
    --top 30

REC_COUNT=$(wc -l < "${TMP_DIR}/recommendations.txt")
echo "   推荐结果: ${REC_COUNT} 条"

# Step 5: 将离线结果回写业务数据库，/api/recommendations 才能读取到它。
echo ""
echo "[5/6] 导入推荐结果..."
python3 "${SCRIPT_DIR}/import_results.py" "${TMP_DIR}/recommendations.txt" --batch-date "${BATCH_DATE}"

# Step 6: 记录运行日志
echo ""
echo "[6/6] 记录运行日志..."
python3 -c "
from app.db.database import get_connection, now_iso
ts = now_iso()
user_count = 0
try:
    with open('${TMP_DIR}/recommendations.txt') as f:
        users = set()
        for line in f:
            parts = line.strip().split('\t')
            if parts: users.add(parts[0])
        user_count = len(users)
except: pass
with get_connection() as conn:
    conn.execute('''INSERT INTO recommendation_runs (batch_date, status, total_users, total_products, started_at, finished_at, created_at)
                    VALUES (?,?,?,?,?,?,?)''',
                 ('${BATCH_DATE}', 'completed', user_count, ${REC_COUNT}, ts, ts, ts))
    conn.commit()
print(f'   run recorded: {user_count} users, ${REC_COUNT} recs')
"

echo ""
echo "========================================"
echo "  完成！"
echo "  分类偏好: ${TMP_DIR}/category_scores.txt"
echo "  商品偏好: ${TMP_DIR}/product_scores.txt"
echo "  推荐结果: ${TMP_DIR}/recommendations.txt"
echo "========================================"
