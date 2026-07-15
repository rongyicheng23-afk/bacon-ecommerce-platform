#!/usr/bin/env python3
"""为 Bacon Mall 批量导入 Pexels 商品主图。"""
import argparse
import csv
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from app.services.media_service import MediaStorageError, ensure_buckets, get_object_url, upload_image

PLAN_PATH = ROOT / "docs" / "product_image_plan.csv"
DB_PATH = ROOT / "bacon_mall.db"
STAGING_DIR = Path.home() / "Desktop" / "BaconMall-商品素材" / "Pexels"
API_URL = "https://api.pexels.com/v1/search"

KEYWORDS = [
    ("耳机", "wireless headphones product"), ("键盘", "mechanical keyboard product"),
    ("鼠标", "wireless mouse product"), ("移动电源", "power bank product"),
    ("快充电源", "power bank product"), ("摄像头", "webcam product"),
    ("手环", "fitness tracker product"), ("平板支架", "tablet stand product"),
    ("充电器", "USB charger product"), ("扩展坞", "USB hub product"),
    ("音箱", "portable bluetooth speaker product"), ("护目眼镜", "blue light glasses product"),
    ("投屏器", "wireless display adapter product"),
    ("双肩背包", "backpack product"), ("帆布鞋", "canvas sneakers product"),
    ("卫衣", "hoodie product"), ("短袖", "t shirt product"), ("围巾", "wool scarf product"),
    ("长裤", "casual trousers product"), ("防晒衣", "light jacket product"),
    ("棉袜", "cotton socks product"), ("皮带", "leather belt product"),
    ("跑鞋", "running shoes product"), ("冰袖", "arm sleeves product"), ("腰带", "canvas belt product"),
    ("洁面", "facial cleanser product"), ("防晒霜", "sunscreen product"),
    ("口红", "lipstick product"), ("面霜", "face cream product"),
    ("面膜", "face mask skincare product"), ("精华", "face serum product"),
    ("眼影", "eyeshadow palette product"), ("卸妆水", "micellar water product"),
    ("眉笔", "eyebrow pencil product"), ("沐浴露", "body wash product"),
    ("瑜伽垫", "yoga mat product"), ("跳绳", "jump rope product"),
    ("运动T恤", "sports t shirt product"), ("护膝", "knee support product"),
    ("水壶", "sports water bottle product"), ("羽毛球拍", "badminton racket product"),
    ("弹力带", "resistance bands product"), ("登山杖", "trekking poles product"),
    ("腰包", "running waist bag product"), ("泳镜", "swimming goggles product"),
    ("手套", "fitness gloves product"),
    ("龙井", "green tea product"), ("巧克力", "dark chocolate product"),
    ("燕麦", "oatmeal product"), ("红枣", "jujube tea product"),
    ("黑咖啡", "instant coffee product"), ("牛肉干", "beef jerky product"),
    ("手冲咖啡", "pour over coffee product"), ("坚果", "mixed nuts product"),
    ("果冻", "fruit jelly product"), ("面包粉", "bread flour product"), ("蜂蜜", "honey jar product"),
    ("台灯", "desk lamp product"), ("保温杯", "vacuum flask product"),
    ("加湿器", "humidifier product"), ("床笠", "bedding product"),
    ("置物架", "wooden shelf product"), ("坐垫", "office seat cushion product"),
    ("窗帘", "blackout curtain product"), ("电脑桌", "computer desk product"),
    ("收纳箱", "storage box product"), ("防滑垫", "bath mat product"),
    ("午休毯", "fleece blanket product"),
]
CATEGORY_FALLBACK = {"图书": "books stack", "家居": "home product", "数码": "electronics product", "服饰": "clothing product", "美妆": "cosmetics product", "运动": "sports equipment product", "食品": "food product"}


def query_for(row: dict) -> str:
    if row["分类"] == "图书":
        return "books stack"
    for needle, query in KEYWORDS:
        if needle in row["商品名"]:
            return query
    return CATEGORY_FALLBACK[row["分类"]]


def search(query: str) -> list[dict]:
    key = os.environ.get("PEXELS_API_KEY", "")
    if not key:
        raise ValueError("缺少 PEXELS_API_KEY")
    request = Request(
        f"{API_URL}?{urlencode({'query': query, 'per_page': 30})}",
        headers={"Authorization": key, "User-Agent": "BaconMallCourseProject/1.0"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response).get("photos", [])


def download(url: str) -> bytes:
    with urlopen(Request(url, headers={"User-Agent": "BaconMallCourseProject/1.0"}), timeout=45) as response:
        return response.read()


def load_rows() -> list[dict]:
    with PLAN_PATH.open(encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def save_rows(rows: list[dict]) -> None:
    with PLAN_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="下载、上传 MinIO 并更新数据库；默认仅预览")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    rows = load_rows()
    targets = [row for row in rows if row["状态"] != "已绑定"]
    if args.limit:
        targets = targets[:args.limit]
    if args.apply and not ensure_buckets():
        raise SystemExit("MinIO 不可用，请先执行 backend/scripts/start_minio.sh")

    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    cached: dict[str, list[dict]] = {}
    conn = sqlite3.connect(DB_PATH) if args.apply else None
    success, failed = 0, []
    for row in targets:
        query = query_for(row)
        try:
            if query not in cached:
                if cached:
                    time.sleep(0.4)
                cached[query] = search(query)
            options = cached[query]
            if not options:
                raise ValueError("未找到候选图")
            photo = options[int(row["productId"]) % len(options)]
            print(f'{row["productId"]}\t{row["商品名"]}\t{query}\t{photo["url"]}')
            if not args.apply:
                continue
            image = download(photo["src"]["large"])
            filename = f'{row["productId"]}-cover.jpg'
            (STAGING_DIR / filename).write_bytes(image)
            object_key = upload_image(image, filename, "image/jpeg")
            object_url = get_object_url(object_key)
            conn.execute("UPDATE products SET image_urls = ?, updated_at = datetime('now') WHERE product_id = ?", (json.dumps([object_url]), row["productId"]))
            row["英文搜索词"] = query
            row["图片来源页面"] = photo["url"]
            row["摄影师/作者"] = f'{photo["photographer"]} · Pexels'
            row["本地文件名"] = filename
            row["MinIO URL"] = object_url
            row["状态"] = "已绑定"
            success += 1
        except (OSError, ValueError, MediaStorageError) as exc:
            failed.append((row["productId"], str(exc)))
            print(f'FAILED\t{row["productId"]}\t{exc}', file=sys.stderr)
    if conn:
        conn.commit()
        conn.close()
        save_rows(rows)
    print(f'completed={success} failed={len(failed)}')
    for product_id, reason in failed:
        print(f'FAILED {product_id}: {reason}')


if __name__ == "__main__":
    main()
