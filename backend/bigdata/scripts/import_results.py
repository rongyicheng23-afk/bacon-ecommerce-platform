#!/usr/bin/env python3
"""将推荐结果 TSV 导入 SQLite recommendation_results 表。

用法:
    python import_results.py recommendations.txt --batch-date 2026-07-12
"""
import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.db.database import get_connection, now_iso


def import_results(filepath: str, batch_date: str):
    count = 0
    ts = now_iso()
    with get_connection() as conn:
        # 清除同批次旧数据
        conn.execute("DELETE FROM recommendation_results WHERE batch_date = ?", (batch_date,))
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) < 4:
                    continue
                user_id, product_id, score, reason = parts[0], parts[1], parts[2], parts[3]
                rank_no = parts[4] if len(parts) > 4 else "0"
                conn.execute(
                    """INSERT INTO recommendation_results
                       (user_id, product_id, score, reason_code, rank_no, batch_date, created_at)
                       VALUES (?,?,?,?,?,?,?)""",
                    (int(user_id), int(product_id), float(score), reason, int(rank_no), batch_date, ts),
                )
                count += 1
        conn.commit()
    print(f"[import] {count} 条推荐已导入 (batch={batch_date})")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("file", help="推荐结果 TSV 文件")
    p.add_argument("--batch-date", required=True)
    args = p.parse_args()
    import_results(args.file, args.batch_date)
