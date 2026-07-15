#!/bin/bash
# 上传行为日志 JSONL 到 HDFS
# 用法: bash upload_to_hdfs.sh [日期]
# 示例: bash upload_to_hdfs.sh 2026-07-12

set -e

DATE="${1:-$(date +%Y-%m-%d)}"
EXPORT_DIR="exports"
LOCAL_FILE="${EXPORT_DIR}/behavior-${DATE}.jsonl"
HDFS_DIR="/bacon-mall/raw/behavior/date=${DATE}"

echo "=== 上传行为日志到 HDFS ==="
echo "本地文件: ${LOCAL_FILE}"
echo "HDFS 目录: ${HDFS_DIR}"

if [ ! -f "${LOCAL_FILE}" ]; then
    echo "❌ 文件不存在: ${LOCAL_FILE}"
    echo "   请先运行: python scripts/export_behaviors.py"
    exit 1
fi

# 检查 HDFS 命令是否可用
if ! command -v hadoop &> /dev/null; then
    echo "⚠️  hadoop 命令未找到，跳过 HDFS 上传（本地模式）"
    echo "   文件位于: ${LOCAL_FILE}"
    exit 0
fi

# 创建目录并上传
hadoop fs -mkdir -p "${HDFS_DIR}"
hadoop fs -put -f "${LOCAL_FILE}" "${HDFS_DIR}/part-00000.jsonl"

echo "✅ 上传完成"
echo "   查看: hadoop fs -ls ${HDFS_DIR}"
