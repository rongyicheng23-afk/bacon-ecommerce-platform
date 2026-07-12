#!/usr/bin/env python3
"""Hadoop Streaming Mapper: 用户分类偏好

输入: behavior JSONL（每行一个 JSON）
输出: user_id|category\taction_weight
"""
import json
import sys

WEIGHTS = {"view": 1, "search": 2, "search_click": 2, "favorite": 3, "cart": 4, "purchase": 5, "unfavorite": -2, "refund": -8}

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        record = json.loads(line)
    except json.JSONDecodeError:
        continue

    user_id = record.get("userId")
    if user_id is None:
        continue  # 跳过游客日志，不参与个性化推荐
    category = record.get("category") or "未分类"
    action = record.get("action", "view")
    weight = WEIGHTS.get(action, 0)

    # 输出: user_id|category \t weight
    print(f"{user_id}|{category}\t{weight}")
