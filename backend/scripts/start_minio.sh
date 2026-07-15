#!/bin/bash
# 启动 MinIO 开发服务器
# API: http://127.0.0.1:9002  控制台: http://127.0.0.1:9001
# 账号: minioadmin / minioadmin

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../minio_data_community"
mkdir -p "${DATA_DIR}"

# 只使用固定的社区版，避免 Homebrew 当前的 AIStor 在无许可证时拒绝 S3 操作。
MINIO_BIN="${SCRIPT_DIR}/../tools/minio-community"
if [ ! -x "${MINIO_BIN}" ]; then
    echo "未找到 MinIO 社区版: ${MINIO_BIN}"
    echo "请执行："
    echo "  mkdir -p ${SCRIPT_DIR}/../tools"
    echo "  curl -fL https://dl.min.io/server/minio/release/darwin-arm64/archive/minio.RELEASE.2025-09-07T16-13-09Z -o ${MINIO_BIN}"
    echo "  chmod +x ${MINIO_BIN}"
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
