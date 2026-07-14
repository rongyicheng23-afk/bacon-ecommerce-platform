#!/bin/bash
# 启动 MinIO 社区版（开发用）
# API: http://127.0.0.1:9002  控制台: http://127.0.0.1:9003
# 账号: minioadmin / minioadmin

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../minio_data_community"
MINIO_BIN="${SCRIPT_DIR}/../tools/minio-community"

mkdir -p "${DATA_DIR}"

if [ ! -f "${MINIO_BIN}" ]; then
    echo "❌ 未找到社区版 MinIO: ${MINIO_BIN}"
    echo "   下载: curl -o ${MINIO_BIN} https://dl.min.io/server/minio/release/darwin-arm64/minio"
    echo "   chmod +x ${MINIO_BIN}"
    exit 1
fi

echo "=== MinIO 社区版 ==="
echo "数据目录: ${DATA_DIR}"
echo "API:      http://127.0.0.1:9002"
echo "控制台:   http://127.0.0.1:9003"
echo "账号:     minioadmin / minioadmin"
echo ""

MINIO_ROOT_USER=minioadmin MINIO_ROOT_PASSWORD=minioadmin "${MINIO_BIN}" server "${DATA_DIR}" --address ":9002" --console-address ":9003"
