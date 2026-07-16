#!/bin/zsh
# 由 macOS launchd 每天触发：Mac 导出行为日志，Hadoop 集群完成离线计算。
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOCK_DIR="$ROOT_DIR/.recommendation-pipeline.lock"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[$(date '+%F %T')] 推荐任务已在运行，跳过本次触发。"
  exit 0
fi
trap 'rmdir "$LOCK_DIR"' EXIT

cd "$ROOT_DIR"
source .venv/bin/activate
bash bigdata/scripts/run_pipeline.sh hadoop-remote
