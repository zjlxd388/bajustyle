# -*- coding: utf-8 -*-
"""
BajuStyle 续翻脚本 v3：单款调用 + 可断点续翻 + 翻译阶段不重建页面
=================================================================
把 products.json 里「名字仍是中文（name == nameZh）」的商品，
逐款用 DeepSeek 翻成 EN / MS / VI（名字 + 描述 1 次调用）。
- 每款独立调用，避免批量长描述超 token 被截断
- 每进程最多 MAX_CALLS 次出站（< 环境限流阈值，避免被杀）
- 翻译阶段只写盘 products.json，不重建页面（全部翻完后再统一重建）
- 已翻译的（name != nameZh）自动跳过，可反复跑直到全部完成

用法：LIMIT=6 python translate_pending.py   （外层 for 循环驱动多次即可跑完全部）
"""
import json, time, sys, os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "products.json"
SLEEP = 2.0          # 每次调用间隔（秒）
MAX_CALLS = 6        # 每进程最多出站调用数（< 环境限制，避免被杀）

sys.path.insert(0, str(BASE_DIR))
import manage
Translator = manage.Translator
requests = __import__("requests")


def translate_one(translator, zh_name, zh_desc):
    """翻译单款，返回 dict 或 None"""
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
        resp = requests.post(
            translator.api_url,
            headers={"Authorization": "Bearer " + translator.api_key,
                     "Content-Type": "application/json"},
            json={"model": translator.model,
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.1,
                  "max_tokens": 4096,
                  "response_format": {"type": "json_object"}},
            timeout=60,
        )
        if resp.status_code != 200:
            return None
        content = resp.json()["choices"][0]["message"]["content"].strip()
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1]
                if content.startswith("json"):
                    content = content[4:]
        return json.loads(content.strip())
    except Exception as e:
        print("  ⚠️ 调用异常:", repr(e))
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

    limit = int(os.environ.get("LIMIT", "0") or 0)
    if limit:
        todo = todo[:limit]
    print(f"🔍 本次待翻：{len(todo)} 件（每进程限 {MAX_CALLS} 次调用）")
    calls = 0
    done = 0
    for cat_id, p in todo:
        if calls >= MAX_CALLS:
            print(f"⏸ 已达本进程出站上限，停止（重跑可续翻剩余 {len(todo) - done} 件）")
            break
        zh_name = p.get("nameZh", "")
        zh_desc = (p.get("desc") or {}).get("zh", "")
        r = translate_one(translator, zh_name, zh_desc)
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
        json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        calls += 1
        done += 1
        print(f"✅ [{done}/{len(todo)}] {zh_name} -> {p.get('name')}")
        time.sleep(SLEEP)

    remaining = len(todo) - done
    if remaining <= 0:
        print("🎉 全部翻译完成！")
    else:
        print(f"🎉 本次完成 {done} 件，剩余 {remaining} 件（重跑本脚本续翻）。")


if __name__ == "__main__":
    main()
