#!/bin/bash
# 启动 MinIO 开发服务器
# API: http://127.0.0.1:9002  控制台: http://127.0.0.1:9001
# 账号: minioadmin / minioadmin

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../minio_data_community"
mkdir -p "${DATA_DIR}"

# 查找 MinIO 二进制：优先 tools/minio-community，其次 PATH 中的 minio
if [ -x "${SCRIPT_DIR}/../tools/minio-community" ]; then
    MINIO_BIN="${SCRIPT_DIR}/../tools/minio-community"
elif command -v minio &> /dev/null; then
    MINIO_BIN="minio"
else
    echo "❌ 未找到 MinIO"
    echo "   brew install minio  或  下载社区版到 backend/tools/minio-community"
    exit 1
fi

echo "=== MinIO 开发服务器 ==="
echo "二进制:   ${MINIO_BIN}"
echo "数据目录: ${DATA_DIR}"
echo "API:      http://127.0.0.1:9002"
echo "控制台:   http://127.0.0.1:9001"
echo "账号:     minioadmin / minioadmin"
echo ""

MINIO_ROOT_USER=minioadmin MINIO_ROOT_PASSWORD=minioadmin "${MINIO_BIN}" server "${DATA_DIR}" --address ":9002" --console-address ":9001"
