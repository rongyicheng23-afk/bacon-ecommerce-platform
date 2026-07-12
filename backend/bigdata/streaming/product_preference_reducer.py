#!/usr/bin/env python3
"""Hadoop Streaming Reducer: 用户商品偏好

输入: user_id|product_id\tweight（已排序）
输出: user_id\tproduct_id\tscore
"""
import sys

current_key = None
current_score = 0

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        key, weight_str = line.split("\t", 1)
        weight = int(weight_str)
    except ValueError:
        continue

    if key != current_key:
        if current_key is not None and current_score != 0:
            user_id, product_id = current_key.split("|", 1)
            print(f"{user_id}\t{product_id}\t{current_score}")
        current_key = key
        current_score = 0

    current_score += weight

if current_key is not None and current_score != 0:
    user_id, product_id = current_key.split("|", 1)
    print(f"{user_id}\t{product_id}\t{current_score}")
