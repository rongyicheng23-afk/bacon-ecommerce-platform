"""导出未导出过的行为日志为 JSON Lines 文件，按日期命名。

用法:
    cd backend && source .venv/bin/activate
    python scripts/export_behaviors.py

输出目录: backend/exports/
文件命名: behavior-YYYY-MM-DD.jsonl
每行一个 JSON 对象。
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.database import get_connection, now_iso


def export(output_dir: str = "exports") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    ts = now_iso()
    exported: dict[str, str] = {}

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT log_id, event_id, user_id, session_id, product_id, product_name,
                   action, category, quantity, sku_id, sku_name, order_id,
                   amount, item_count, source, created_at
            FROM behavior_logs
            WHERE exported_at IS NULL
            ORDER BY created_at ASC
        """).fetchall()

        if not rows:
            print("[export] 没有待导出的日志")
            return exported

        by_date: dict[str, list] = {}
        for r in rows:
            date = r["created_at"][:10]
            by_date.setdefault(date, []).append(r)

        log_ids: list[int] = []
        for date, day_rows in sorted(by_date.items()):
            filepath = os.path.join(output_dir, f"behavior-{date}.jsonl")
            with open(filepath, "a", encoding="utf-8") as f:
                for r in day_rows:
                    record = {
                        "eventId": r["event_id"],
                        "userId": r["user_id"],
                        "sessionId": r["session_id"],
                        "productId": r["product_id"],
                        "productName": r["product_name"],
                        "action": r["action"],
                        "category": r["category"],
                        "quantity": r["quantity"],
                        "skuId": r["sku_id"],
                        "skuName": r["sku_name"],
                        "orderId": r["order_id"],
                        "amount": r["amount"],
                        "itemCount": r["item_count"],
                        "source": r["source"],
                        "timestamp": r["created_at"],
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    log_ids.append(r["log_id"])

            exported[date] = filepath
            print(f"[export] {filepath} — {len(day_rows)} 条")

        if log_ids:
            placeholders = ",".join("?" for _ in log_ids)
            conn.execute(
                f"UPDATE behavior_logs SET exported_at = ? WHERE log_id IN ({placeholders})",
                [ts] + log_ids,
            )
            print(f"[export] 共导出 {len(log_ids)} 条，已标记为已导出")

    return exported


if __name__ == "__main__":
    export()
