import requests
import json
import time
from urllib.parse import urljoin

HEADERS = {"User-Agent": "okhttp/4.12.0"}
TIMEOUT = 10

# 多仓源（入口）
MULTI_SOURCES = [
    {"url": "http://tvbox.xn--4kq62z5rby2qupq9ub.top/", "name": "放牛娃子域"},
    {"url": "http://我不是.摸鱼儿.top", "name": "摸鱼儿主站"},
    {"url": "http://www.小不点.com", "name": "摸鱼儿备用站"},
    {"url": "http://www.xn--sss604efuw.com/", "name": "饭太硬主站"},
    {"url": "https://www.xn--4kq62z5rby2qupq9ub.top/", "name": "放牛娃主站"},
]

# 直接单仓源（不需要解析多仓）
SINGLE_SOURCES = [
    {"url": "http://www.饭太硬.cc/tv", "name": "饭太硬cc"},
    {"url": "http://fty.xxooo.cf/tv", "name": "饭太硬cf"},
    {"url": "https://raw.atomgit.com/xxxooo/fan/blobs/cef5f441c422cffe4852e0fc8b102f9be6d2bb2b/in.bmp", "name": "饭太硬AtomGit"},
    {"url": "http://mitvbox.xyz/%E5%B0%8F%E7%B1%B3/DEMO.json", "name": "小米TVBox"},
    {"url": "http://ok213.top/tv", "name": "OK213"},
    {"url": "http://cdn.qiaoji8.com/tvbox.json", "name": "巧技"},
    {"url": "https://gh-proxy.net/https://raw.githubusercontent.com/yoursmile66/TVBox/refs/heads/main/XC.json", "name": "YourSmile"},
    {"url": "http://www.饭太硬.com/tv", "name": "饭太硬com"},
    {"url": "http://ok321.top/tv", "name": "OK321"},
]


def fetch_json(url):
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers=HEADERS)
        if r.status_code >= 400:
            return None
        text = r.text.strip()
        if text.startswith('﻿'):
            text = text[1:]
        return json.loads(text)
    except:
        return None


def parse_multi_source(url):
    """解析多仓地址，返回单仓URL列表"""
    data = fetch_json(url)
    if not data:
        return []
    urls = data.get("urls", [])
    if not urls and isinstance(data, list):
        urls = data
    result = []
    for item in urls:
        if isinstance(item, dict) and "url" in item:
            result.append({"url": item["url"], "name": item.get("name", "")})
    return result


def parse_single_source(url):
    """解析单仓地址，返回TVBox配置"""
    data = fetch_json(url)
    if not data or not isinstance(data, dict):
        return None
    if "sites" not in data and "urls" in data:
        return None
    return data


def merge_configs(configs):
    """合并多个单仓配置，去重"""
    merged = {
        "sites": [],
        "lives": [],
        "parses": [],
        "flags": ["flag"],
    }

    seen_site_keys = set()
    seen_live_urls = set()
    seen_parse_urls = set()

    for cfg in configs:
        if not cfg:
            continue

        for site in cfg.get("sites", []):
            key = site.get("key", "")
            if key and key not in seen_site_keys:
                seen_site_keys.add(key)
                merged["sites"].append(site)

        for live in cfg.get("lives", []):
            live_key = live.get("url", "") or live.get("name", "")
            if live_key and live_key not in seen_live_urls:
                seen_live_urls.add(live_key)
                merged["lives"].append(live)

        for parse in cfg.get("parses", []):
            parse_key = parse.get("url", "") or parse.get("name", "")
            if parse_key and parse_key not in seen_parse_urls:
                seen_parse_urls.add(parse_key)
                merged["parses"].append(parse)

    if not merged["parses"]:
        del merged["parses"]
    if not merged["lives"]:
        del merged["lives"]

    return merged


def main():
    all_single_urls = []
    valid_multi = []

    # 第一步：解析多仓，获取单仓URL
    print("=" * 50)
    print("第一步：解析多仓源")
    print("=" * 50)
    for src in MULTI_SOURCES:
        print(f"\n解析多仓: {src['name']} -> {src['url']}")
        singles = parse_multi_source(src["url"])
        if singles:
            valid_multi.append(src)
            print(f"  [OK] 获取到 {len(singles)} 个单仓")
            for s in singles:
                all_single_urls.append(s)
        else:
            print(f"  [FAIL] 无法解析")
        time.sleep(0.3)

    # 加入直接单仓源
    for src in SINGLE_SOURCES:
        all_single_urls.append(src)

    # URL去重
    seen_urls = set()
    unique_singles = []
    for s in all_single_urls:
        if s["url"] not in seen_urls:
            seen_urls.add(s["url"])
            unique_singles.append(s)

    print(f"\n去重后共 {len(unique_singles)} 个单仓URL")

    # 第二步：抓取单仓配置
    print("\n" + "=" * 50)
    print("第二步：抓取单仓配置")
    print("=" * 50)
    configs = []
    valid_singles = []
    failed_singles = []

    for s in unique_singles:
        print(f"\n抓取: {s['name']} -> {s['url']}")
        cfg = parse_single_source(s["url"])
        if cfg:
            configs.append(cfg)
            valid_singles.append(s)
            sites_count = len(cfg.get("sites", []))
            print(f"  [OK] sites={sites_count}")
        else:
            failed_singles.append(s)
            print(f"  [FAIL] 失败")
        time.sleep(0.3)

    # 第三步：合并去重
    print("\n" + "=" * 50)
    print("第三步：合并去重")
    print("=" * 50)
    merged = merge_configs(configs)
    print(f"合并结果: sites={len(merged['sites'])}, lives={len(merged.get('lives', []))}, parses={len(merged.get('parses', []))}")

    # 输出 merged.json（合并后的超级单仓）
    with open("merged.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # 输出 multi.json（完整源列表，不依赖验证结果）
    result = {"urls": MULTI_SOURCES + SINGLE_SOURCES}
    with open("multi.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 输出 single_list.json（所有解析出的可用单仓URL列表）
    with open("single_list.json", "w", encoding="utf-8") as f:
        json.dump({"singles": valid_singles}, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"完成!")
    print(f"  多仓可用: {len(valid_multi)}/{len(MULTI_SOURCES)}")
    print(f"  单仓可用: {len(valid_singles)}/{len(unique_singles)}")
    print(f"  合并sites: {len(merged['sites'])}")
    print(f"\n输出文件:")
    print(f"  multi.json    - 多仓源列表（影视仓用）")
    print(f"  merged.json   - 合并后的超级单仓（直接用）")
    print(f"  single_list.json - 所有可用单仓URL列表")

    if failed_singles:
        print(f"\n失败的单仓 ({len(failed_singles)}):")
        for s in failed_singles[:20]:
            print(f"  - {s['name']}: {s['url']}")


if __name__ == "__main__":
    main()
