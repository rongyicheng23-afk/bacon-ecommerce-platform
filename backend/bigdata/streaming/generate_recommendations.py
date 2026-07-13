#!/usr/bin/env python3
"""推荐生成器 — 结合用户分类/商品偏好 + 商品热度，生成个性化推荐。

用法（本地管道）:
    python generate_recommendations.py \\
        --db bacon_mall.db \\
        --category-scores category_scores.txt \\
        --product-scores product_scores.txt \\
        --output recommendations.txt \\
        --top 30

结果写入 SQLite recommendation_results 表，同时输出 TSV 文件。
"""

import argparse
import sqlite3
import sys
from datetime import date


def parse_args():
    p = argparse.ArgumentParser(description="Bacon Mall 推荐生成器")
    p.add_argument("--db", required=True, help="SQLite 数据库路径")
    p.add_argument("--category-scores", help="用户分类偏好 TSV: user_id\\tcategory\\tscore")
    p.add_argument("--product-scores", help="用户商品偏好 TSV: user_id\\tproduct_id\\tscore")
    p.add_argument("--output", default="recommendations.txt")
    p.add_argument("--top", type=int, default=30, help="每用户推荐数量")
    p.add_argument("--batch-date", default=date.today().isoformat())
    return p.parse_args()


def load_category_scores(path: str) -> dict[int, dict[str, float]]:
    """返回 {user_id: {category: score}}"""
    scores: dict[int, dict[str, float]] = {}
    if not path:
        return scores
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue
            uid = int(parts[0])
            cat = parts[1]
            score = float(parts[2])
            scores.setdefault(uid, {})[cat] = score
    return scores


def load_product_scores(path: str) -> dict[int, dict[int, float]]:
    """返回 {user_id: {product_id: score}}"""
    scores: dict[int, dict[int, float]] = {}
    if not path:
        return scores
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue
            uid = int(parts[0])
            pid = int(parts[1])
            score = float(parts[2])
            scores.setdefault(uid, {})[pid] = score
    return scores


def get_top_categories(cat_scores: dict[str, float], n: int = 3) -> list[str]:
    return sorted(cat_scores, key=cat_scores.get, reverse=True)[:n]


def generate(
    db_path: str,
    cat_scores: dict[int, dict[str, float]],
    prod_scores: dict[int, dict[int, float]],
    top: int,
    batch_date: str,
) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row

    # 所有活跃商品
    products = conn.execute(
        "SELECT product_id, category, sales_count, stock, price FROM products WHERE status = 'active'"
    ).fetchall()
    if not products:
        print("[gen] 没有活跃商品", file=sys.stderr)
        return []

    # 全站热门（按销量降序）
    global_hot = sorted(products, key=lambda p: -p["sales_count"])
    hot_ids = [p["product_id"] for p in global_hot]

    # 所有用户
    users = conn.execute("SELECT user_id FROM users WHERE status = 'active' AND role = 'buyer'").fetchall()
    all_user_ids = [u["user_id"] for u in users]

    # 若没有用户偏好数据，添加已知用户
    known_users = set(cat_scores.keys()) | set(prod_scores.keys())
    for uid in all_user_ids:
        if uid not in known_users:
            known_users.add(uid)

    recommendations: list[dict] = []
    ts = date.today().isoformat() + "T00:00:00"

    for user_id in sorted(known_users):
        # 用户已购商品
        purchased = set(
            r[0] for r in conn.execute(
                "SELECT DISTINCT product_id FROM behavior_logs WHERE user_id = ? AND action = 'purchase'",
                (user_id,),
            ).fetchall()
        )

        user_cats = cat_scores.get(user_id, {})
        user_prods = prod_scores.get(user_id, {})

        ranked: list[tuple[int, float, str]] = []  # (product_id, score, reason)

        if user_cats:
            top_cats = get_top_categories(user_cats)
            for p in products:
                if p["product_id"] in purchased:
                    continue
                if p["category"] in top_cats:
                    # 推荐分数 = 分类偏好 × 0.5 + 商品偏好 × 0.3 + 热度 × 0.2
                    cat_score = user_cats.get(p["category"], 0) * 0.5
                    prod_score = user_prods.get(p["product_id"], 0) * 0.3
                    pop_score = (p["sales_count"] / max(1, max(p["sales_count"] for p in products))) * 10 * 0.2
                    total = cat_score + prod_score + pop_score
                    reason = f"偏好{p['category']}分类"
                    ranked.append((p["product_id"], total, reason))

            # 排序取 top
            ranked.sort(key=lambda x: -x[1])
            for pid, score, reason in ranked[:top]:
                recommendations.append({
                    "user_id": user_id, "product_id": pid,
                    "score": round(score, 2), "reason_code": reason,
                    "rank_no": len([r for r in recommendations if r["user_id"] == user_id]) + 1,
                })

        # 冷启动：新用户或无偏好数据的用户，推荐全站热销
        if not ranked:
            for pid in hot_ids:
                if pid in purchased:
                    continue
                if len([r for r in recommendations if r["user_id"] == user_id]) >= top:
                    break
                recommendations.append({
                    "user_id": user_id, "product_id": pid,
                    "score": round(10.0 - len([r for r in recommendations if r["user_id"] == user_id]) * 0.1, 2),
                    "reason_code": "全站热销",
                    "rank_no": len([r for r in recommendations if r["user_id"] == user_id]) + 1,
                })

    # 写入数据库 + 输出文件
    with open(args.output, "w", encoding="utf-8") as out:
        conn.execute("DELETE FROM recommendation_results WHERE batch_date = ?", (batch_date,))
        for rec in recommendations:
            conn.execute(
                """INSERT OR REPLACE INTO recommendation_results
                   (user_id, product_id, score, reason_code, rank_no, batch_date, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (rec["user_id"], rec["product_id"], rec["score"],
                 rec["reason_code"], rec["rank_no"], batch_date, ts),
            )
            out.write(f"{rec['user_id']}\t{rec['product_id']}\t{rec['score']}\t{rec['reason_code']}\t{rec['rank_no']}\t{batch_date}\n")

    conn.commit()
    conn.close()

    # 统计
    user_count = len(set(r["user_id"] for r in recommendations))
    print(f"[gen] {len(recommendations)} 条推荐, {user_count} 个用户, batch={batch_date}", file=sys.stderr)
    return recommendations


if __name__ == "__main__":
    args = parse_args()
    generate(args.db, load_category_scores(args.category_scores), load_product_scores(args.product_scores), args.top, args.batch_date)
