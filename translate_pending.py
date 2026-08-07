# -*- coding: utf-8 -*-
"""
BajuStyle 续翻脚本（Phase 2，可重复执行、可断点续翻）
==================================================
把 products.json 里「名字仍是中文（name == nameZh）」的商品，
用 DeepSeek 一次性翻成 EN / MS / VI（名字 + 描述合并为 1 次调用）。
- 每次翻译后立刻写盘 + 重建页面，进程被杀也不丢已翻部分
- 调用间 sleep 3 秒，降低限流概率
- 已翻译的（name != nameZh）自动跳过，可反复跑直到全部完成

用法：python translate_pending.py
"""
import json, time, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "products.json"

sys.path.insert(0, str(BASE_DIR))
import manage
Translator = manage.Translator
HTMLGenerator = manage.HTMLGenerator

SLEEP = 3.0  # 每次 API 调用间隔（秒）


def translate_combo(translator, zh_name, zh_desc):
    """一次调用同时翻译名字 + 描述，返回 dict 或 None"""
    if not zh_name and not zh_desc:
        return None
    prompt = (
        'Output a JSON object with exactly these 6 keys: '
        '"name_en","name_ms","name_vi","desc_en","desc_ms","desc_vi".\n'
        'Translate the following Chinese fashion product into English (en), '
        'Bahasa Melayu (ms), Vietnamese (vi). Keep the description structure and bullet points.\n\n'
        'Product name (Chinese): ' + (zh_name or "") + '\n'
        'Product description (Chinese): ' + (zh_desc or "")
    )
    try:
        resp = __import__("requests").post(
            translator.api_url,
            headers={"Authorization": "Bearer " + translator.api_key,
                     "Content-Type": "application/json"},
            json={"model": translator.model,
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.1,
                  "max_tokens": 4096,
                  "response_format": {"type": "json_object"}},
            timeout=40,
        )
        if resp.status_code != 200:
            return None
        content = resp.json()["choices"][0]["message"]["content"].strip()
        # 去 markdown 包裹
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1]
                if content.startswith("json"):
                    content = content[4:]
        return json.loads(content.strip())
    except Exception:
        return None


def main():
    translator = Translator()
    if not translator.api_key:
        print("❌ 未配置 DeepSeek Key（config.json）。无法自动翻译，请先配置。")
        return

    data = json.load(open(DATA_FILE, encoding="utf-8"))
    todo = []
    for cat_id, plist in data.get("products", {}).items():
        for p in plist:
            if p.get("name") == p.get("nameZh") or not p.get("name"):
                todo.append((cat_id, p))

    if not todo:
        print("✅ 没有待翻译的商品，全部已是四语。")
        return

    print(f"🔍 待翻译商品：{len(todo)} 件（每款 1 次合并调用）")
    done = 0
    for cat_id, p in todo:
        zh_name = p.get("nameZh", "")
        zh_desc = (p.get("desc") or {}).get("zh", "")
        r = translate_combo(translator, zh_name, zh_desc)
        if r:
            p["name"] = r.get("name_en", zh_name)
            p["nameMs"] = r.get("name_ms", zh_name)
            p["nameVi"] = r.get("name_vi", zh_name)
            d = p.setdefault("desc", {})
            d["en"] = r.get("desc_en", zh_desc)
            d["ms"] = r.get("desc_ms", zh_desc)
            d["vi"] = r.get("desc_vi", zh_desc)
        else:
            print(f"  ⚠️ {zh_name} 翻译失败，保留中文（可重跑）")
        # 立刻写盘 + 重建，保证进度不丢
        json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        HTMLGenerator.regenerate_all(data)
        done += 1
        print(f"✅ [{done}/{len(todo)}] {zh_name} -> {p.get('name')}")
        time.sleep(SLEEP)

    print(f"🎉 完成翻译 {done} 件。可再跑一次确认无遗漏。")


if __name__ == "__main__":
    main()
