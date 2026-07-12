#!/usr/bin/env python3
"""Hadoop Streaming Mapper: 用户商品偏好

输入: behavior JSONL
输出: user_id|product_id\taction_weight
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

    user_id = record.get("userId") or 0
    product_id = record.get("productId")
    if product_id is None:
        continue
    action = record.get("action", "view")
    weight = WEIGHTS.get(action, 0)

    print(f"{user_id}|{product_id}\t{weight}")
