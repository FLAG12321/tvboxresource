import requests
import json
import time

SOURCES = [
    {"url": "http://影视仓.com/duo", "name": "影视仓"},
    {"url": "https://www.iyouhun.com/tv/dc", "name": "有魂多仓"},
    {"url": "http://tvbox.王二小放牛娃.top", "name": "王二小放牛娃"},
    {"url": "http://hello.肥猫.com", "name": "肥猫Hello"},
    {"url": "http://肥猫.com", "name": "肥猫"},
    {"url": "https://盒子迷.top/禁止贩卖", "name": "盒子迷"},
    {"url": "https://3043.kstore.space/bhvip/bh/bh2.json", "name": "BH2源"},
    {"url": "https://3043.kstore.space/bhvip/bh/box.json", "name": "BH-Box"},
    {"url": "http://qxyc.cc/自用测试", "name": "青霞源"},
    {"url": "https://9280.kstore.space/wex.json", "name": "WEX源"},
    {"url": "http://tvbox.xn--4kq62z5rby2qupq9ub.top/", "name": "TVBox聚合"},
    {"url": "http://box.ufuzi.com/tv/qq/短剧频道/api.json", "name": "短剧频道"},
    {"url": "http://cdn.qiaoji8.com/tvbox.json", "name": "巧技"},
    {"url": "https://yydsys.top/duo", "name": "YYDS多仓"},
    {"url": "http://我不是.摸鱼儿.com", "name": "摸鱼儿"},
    {"url": "http://fty.xxoo.cf/tv", "name": "饭太硬1"},
    {"url": "https://raw.atomgit.com/xxxooo/fan/blobs/cef5f441c422cffe4852e0fc8b102f9be6d2bb2b/in.bmp", "name": "饭太硬AtomGit"},
    {"url": "http://www.饭太硬.cc/tv", "name": "饭太硬中文"},
    {"url": "http://xhztv.top/4k.json", "name": "小黄鸭4K"},
    {"url": "http://xhztv.top/xhz", "name": "小黄鸭"},
    {"url": "http://mitvbox.xyz/%E5%B0%8F%E7%B1%B3/DEMO.json", "name": "小米DEMO"},
    {"url": "http://ok213.top/tv", "name": "ok213"},
    {"url": "https://gh-proxy.net/https://raw.githubusercontent.com/yoursmile66/TVBox/refs/heads/main/XC.json", "name": "YourSmile"},
]


def check_source(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True,
                         headers={"User-Agent": "okhttp/4.12.0"})
        return r.status_code < 400
    except:
        return False


def main():
    valid = []
    invalid = []

    for s in SOURCES:
        print(f"检测: {s['name']} -> {s['url']}")
        if check_source(s["url"]):
            valid.append(s)
            print(f"  ✓ 可用")
        else:
            invalid.append(s)
            print(f"  ✗ 不可用")
        time.sleep(0.5)

    result = {"urls": valid}
    with open("multi.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n完成: {len(valid)} 可用 / {len(invalid)} 不可用")
    if invalid:
        print("不可用源:")
        for s in invalid:
            print(f"  - {s['name']}: {s['url']}")


if __name__ == "__main__":
    main()
