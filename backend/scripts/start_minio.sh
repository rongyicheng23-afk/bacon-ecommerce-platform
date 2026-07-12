#!/bin/bash
# 启动 MinIO 服务（开发用）
# 数据存储在 backend/minio_data/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../minio_data"

mkdir -p "${DATA_DIR}"

echo "=== MinIO 开发服务器 ==="
echo "数据目录: ${DATA_DIR}"
echo "控制台:   http://127.0.0.1:9001"
echo "API:      http://127.0.0.1:9000"
echo "账号:     minioadmin / minioadmin"
echo ""

minio server "${DATA_DIR}" --console-address ":9001"
