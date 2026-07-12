#!/bin/bash
# === Bacon Mall 推荐管道 ===
# 完整流程: 导出日志 → 计算偏好 → 生成推荐 → 导入数据库
#
# 用法:
#   本地模式:  bash run_pipeline.sh local
#   Hadoop模式: bash run_pipeline.sh hadoop
#
set -e

MODE="${1:-local}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")/.."
STREAMING_DIR="${ROOT_DIR}/bigdata/streaming"
EXPORT_DIR="${ROOT_DIR}/exports"
DB_PATH="${ROOT_DIR}/bacon_mall.db"
BATCH_DATE="$(date +%Y-%m-%d)"

echo "========================================"
echo "  Bacon Mall 推荐管道"
echo "  模式: ${MODE}"
echo "  日期: ${BATCH_DATE}"
echo "========================================"

# Step 1: 导出行为日志
echo ""
echo "[1/5] 导出行为日志..."
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
echo "   输入: ${INPUT_FILE} ($(wc -l < "${INPUT_FILE}") 条)"

# Step 2: 上传 HDFS（仅 Hadoop 模式）
if [ "${MODE}" = "hadoop" ]; then
    echo ""
    echo "[2/5] 上传 HDFS..."
    bash "${SCRIPT_DIR}/upload_to_hdfs.sh" "${BATCH_DATE}"
else
    echo ""
    echo "[2/5] 上传 HDFS — 跳过（本地模式）"
fi

# Step 3: 计算偏好（本地管道或 Hadoop Streaming）
echo ""
echo "[3/5] 计算用户偏好..."
TMP_DIR="${ROOT_DIR}/tmp_recommendation"
mkdir -p "${TMP_DIR}"

if [ "${MODE}" = "hadoop" ]; then
    # Hadoop Streaming 模式
    HDFS_INPUT="/bacon-mall/raw/behavior/date=${BATCH_DATE}"
    HDFS_CAT_OUT="/bacon-mall/warehouse/user_category_scores/date=${BATCH_DATE}"
    HDFS_PROD_OUT="/bacon-mall/warehouse/user_product_scores/date=${BATCH_DATE}"

    # 用户分类偏好
    hadoop jar "${HADOOP_HOME}/share/hadoop/tools/lib/hadoop-streaming-*.jar" \
        -input "${HDFS_INPUT}" \
        -output "${HDFS_CAT_OUT}" \
        -mapper "python3 category_preference_mapper.py" \
        -reducer "python3 category_preference_reducer.py" \
        -file "${STREAMING_DIR}/category_preference_mapper.py" \
        -file "${STREAMING_DIR}/category_preference_reducer.py"

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
else
    # 本地管道模式
    python3 "${STREAMING_DIR}/category_preference_mapper.py" < "${INPUT_FILE}" | sort | python3 "${STREAMING_DIR}/category_preference_reducer.py" > "${TMP_DIR}/category_scores.txt"
    echo "   分类偏好: $(wc -l < "${TMP_DIR}/category_scores.txt") 行"

    python3 "${STREAMING_DIR}/product_preference_mapper.py" < "${INPUT_FILE}" | sort | python3 "${STREAMING_DIR}/product_preference_reducer.py" > "${TMP_DIR}/product_scores.txt"
    echo "   商品偏好: $(wc -l < "${TMP_DIR}/product_scores.txt") 行"
fi

# Step 4: 生成推荐
echo ""
echo "[4/5] 生成推荐结果..."
python3 "${STREAMING_DIR}/generate_recommendations.py" \
    --db "${DB_PATH}" \
    --category-scores "${TMP_DIR}/category_scores.txt" \
    --product-scores "${TMP_DIR}/product_scores.txt" \
    --output "${TMP_DIR}/recommendations.txt" \
    --batch-date "${BATCH_DATE}" \
    --top 30

REC_COUNT=$(wc -l < "${TMP_DIR}/recommendations.txt")
echo "   推荐结果: ${REC_COUNT} 条"

# Step 5: 记录运行日志
echo ""
echo "[5/5] 记录运行日志..."
python3 -c "
from app.db.database import get_connection, now_iso
ts = now_iso()
with get_connection() as conn:
    conn.execute('''INSERT INTO recommendation_runs (batch_date, status, total_products, started_at, finished_at, created_at)
                    VALUES (?,?,?,?,?,?)''',
                 ('${BATCH_DATE}', 'completed', ${REC_COUNT}, ts, ts, ts))
    conn.commit()
print('   run recorded')
"

echo ""
echo "========================================"
echo "  完成！"
echo "  分类偏好: ${TMP_DIR}/category_scores.txt"
echo "  商品偏好: ${TMP_DIR}/product_scores.txt"
echo "  推荐结果: ${TMP_DIR}/recommendations.txt"
echo "========================================"
