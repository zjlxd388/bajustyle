# -*- coding: utf-8 -*-
"""
BajuStyle 批量上架脚本（本地版，不自动部署）
============================================
用法：把商品按规范放进 待上架/ 目录，然后运行：
    python bulk_import.py

脚本会：
  1. 扫描 待上架/ 下的文件夹，识别 分类 / 子分类（中文名自动映射）
  2. 把每个子文件夹当作一个商品，里面的图片自动归到该商品（第一张当封面）
  3. 复制图片到 images/（重命名为 ASCII 安全名，避免重名）
  4. 写入 products.json 并本地重建全部页面（regenerate_all）
  5. 处理完把 待上架/ 改名为 待上架_已处理_时间戳/，防止重复导入
  ⚠️ 本脚本只做本地导入（中文填四语），不联网翻译。
     翻译请另跑 translate_pending.py（带限流+续翻，可重复执行）。
  ⚠️ 全程不执行 git push，部署需另行确认
"""
import os, re, json, shutil, time, sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INBOX = BASE_DIR / "待上架"
IMAGE_DIR = BASE_DIR / "images"
DATA_FILE = BASE_DIR / "products.json"
REPORT_FILE = BASE_DIR / "批量上架报告.txt"

# 分类中文 -> 系统 id
CAT_MAP = {
    "衣服": "clothing", "衣物": "clothing",
    "鞋子": "shoes", "鞋": "shoes",
    "包包": "bags", "包": "bags", "包袋": "bags",
    "手表": "sb", "腕表": "sb",
    "饰品": "sp", "配饰": "sp",
}
# 衣服子分类中文 -> id（仅作已知映射，未知会自动新建）
SUBCAT_MAP = {
    "短袖": "short", "长袖": "long",
    "短裤": "pants-short", "长裤": "a", "裤子": "a",
}
CAT_EMOJI = {"clothing": "👗", "shoes": "👟", "bags": "👜", "sb": "⌚", "sp": "💍"}
CAT_PREFIX = {"clothing": "c", "shoes": "s", "bags": "b", "sb": "w", "sp": "p"}
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp")

# 导入生成器与翻译器（manage.py 顶部无副作用，可安全 import）
sys.path.insert(0, str(BASE_DIR))
import manage
HTMLGenerator = manage.HTMLGenerator
Translator = manage.Translator


def parse_info(folder):
    """读取 信息.txt：名称 / 价格 / 描述（描述可多行）"""
    info = {"名称": "", "价格": "", "描述": ""}
    f = folder / "信息.txt"
    if not f.exists():
        return info
    cur = None
    for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"^\s*(名称|价格|描述)\s*[:=]\s*(.*)$", line)
        if m:
            cur = m.group(1)
            info[cur] = m.group(2).strip()
        elif cur == "描述" and line.strip():
            info["描述"] += ("\n" if info["描述"] else "") + line.strip()
    return info


def collect_images(folder):
    imgs = []
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in IMG_EXT:
            imgs.append(p)
    return imgs


def next_id(data, cat_id):
    prefix = CAT_PREFIX.get(cat_id, cat_id[:2])
    existing = set()
    for plist in data.get("products", {}).values():
        for p in plist:
            existing.add(p.get("id", ""))
    n = 1
    while f"{prefix}{n}" in existing:
        n += 1
    return f"{prefix}{n}"


def make_subcat(data, cat_id, sub_zh, translator):
    """定位或新建子分类，返回 sub_id；未知名称自动创建"""
    subs = data["categories"][cat_id].setdefault("subcategories", [])
    # 已知映射
    if sub_zh in SUBCAT_MAP:
        return SUBCAT_MAP[sub_zh], False
    # 已存在同名
    for s in subs:
        if s.get("name", {}).get("zh", "") == sub_zh:
            return s["id"], False
    # 新建
    sub_id = f"sub{len(subs) + 1}"
    names = {"zh": sub_zh, "en": sub_zh, "ms": sub_zh, "vi": sub_zh}
    if translator and getattr(translator, "api_key", None):
        r, err = translator.translate(sub_zh, ["en", "ms", "vi"])
        if r:
            names.update({k: r.get(k, sub_zh) for k in ("en", "ms", "vi")})
    subs.append({"id": sub_id, "name": names})
    return sub_id, True


def main():
    if not INBOX.exists():
        print("❌ 找不到 待上架/ 目录。请先按规范放好文件。")
        return

    data = json.load(open(DATA_FILE, encoding="utf-8"))
    print("📥 阶段一：仅本地导入（中文填四语，不联网，确保成功）")

    report_lines = []
    added = 0
    new_subs = []
    need_translate = []  # (cat_id, pid, zh_name, zh_desc)

    for top in sorted([p for p in INBOX.iterdir() if p.is_dir()]):
        name = top.name
        if "-" in name:
            cat_zh, sub_zh = name.split("-", 1)
            cat_zh = cat_zh.strip()
            sub_zh = sub_zh.strip()
        else:
            cat_zh, sub_zh = name.strip(), ""

        cat_id = CAT_MAP.get(cat_zh)
        if not cat_id:
            print(f"⚠️ 跳过未知分类文件夹：{name}（识别不到「{cat_zh}」）")
            report_lines.append(f"⚠️ 跳过未知分类：{name}")
            continue

        sub_id = ""
        if sub_zh:
            sub_id, created = make_subcat(data, cat_id, sub_zh, None)
            if created:
                new_subs.append(f"{cat_zh}/{sub_zh} -> {sub_id}")
                print(f"➕ 新建子分类：{cat_zh}/{sub_zh}")

        # 找商品文件夹：若 top 直接含图片 -> 整文件夹算1个商品；否则遍历子文件夹
        direct_imgs = collect_images(top)
        if direct_imgs:
            product_folders = [top]
        else:
            product_folders = [p for p in sorted(top.iterdir()) if p.is_dir()]

        for pf in product_folders:
            imgs = collect_images(pf)
            if not imgs:
                print(f"⚠️ 跳过无图片的商品：{pf.name}")
                continue
            info = parse_info(pf)
            zh_name = info["名称"] or pf.name
            price = info["价格"] or "CNY 0.00"
            zh_desc = info["描述"]

            pid = next_id(data, cat_id)
            copied = []
            for i, src in enumerate(imgs, 1):
                ext = src.suffix.lower()
                if ext == ".jpeg":
                    ext = ".jpg"
                dst_name = f"{pid}_{i}{ext}"
                dst = IMAGE_DIR / dst_name
                # 防重名
                while dst.exists():
                    dst_name = f"{pid}_{i}_{int(time.time()*1000)%10000}{ext}"
                    dst = IMAGE_DIR / dst_name
                shutil.copy2(src, dst)
                copied.append(f"images/{dst_name}")

            # 翻译（Phase 1 不联网，先填中文，稍后由 translate_pending.py 续翻）
            en = ms = vi = zh_name
            desc_en = desc_ms = desc_vi = zh_desc
            need_translate.append((cat_id, pid, zh_name, zh_desc))

            prod = {
                "id": pid,
                "img": copied[0],
                "images": copied,
                "emoji": CAT_EMOJI.get(cat_id, "📦"),
                "name": en,
                "nameZh": zh_name,
                "nameMs": ms,
                "nameVi": vi,
                "price": price,
                "desc": {"zh": zh_desc, "en": desc_en, "ms": desc_ms, "vi": desc_vi},
                "cat": cat_id,
                "subcat": sub_id,
            }
            data.setdefault("products", {}).setdefault(cat_id, []).append(prod)
            added += 1
            print(f"✅ {cat_zh}{('/'+sub_zh) if sub_zh else ''} <- {zh_name}（{len(copied)}图, {pid}）")
            report_lines.append(
                f"✅ {zh_name} | 分类={cat_zh} 子分类={sub_zh or '无'} | 图片{len(copied)}张 | ID={pid} | 价格={price}"
            )

    if added == 0:
        print("📭 没有新增任何商品。")
        return

    # 写回数据
    json.dump(data, open(DATA_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 本地重建全部页面（不部署）
    HTMLGenerator.regenerate_all(data)
    print("📄 已本地重建全部页面（未部署）")

    # 新子分类提示
    if new_subs:
        print("🆕 新建子分类：")
        for s in new_subs:
            print("   -", s)

    # 待翻译清单
    if need_translate:
        tl = ["# 待翻译清单（把右侧英文/马来/越南补上后告诉我，或我直接翻译）",
              "# 格式：ID | 中文名 | 中文描述"]
        for cat_id, pid, zn, zd in need_translate:
            tl.append(f"{pid} | {zn} | {zd}")
        (BASE_DIR / "待翻译清单.txt").write_text("\n".join(tl), encoding="utf-8")
        print(f"📝 已生成 待翻译清单.txt（{len(need_translate)} 条待补译）")

    # 报告
    report_lines.insert(0, f"批量上架报告 — {time.strftime('%Y-%m-%d %H:%M')}")
    report_lines.insert(1, f"新增商品：{added} 件 | 新建子分类：{len(new_subs)} 个 | 翻译：本地中文（待执行 translate_pending.py）")
    report_lines.append("")
    report_lines.append("⚠️ 以上仅为本地改动，尚未部署到线上。确认无误后告知我「部署上线」。")
    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")

    # 归档已处理目录，防止重复导入
    archive = BASE_DIR / f"待上架_已处理_{time.strftime('%Y%m%d_%H%M%S')}"
    shutil.move(str(INBOX), str(archive))
    print(f"📦 已将 待上架/ 归档为 {archive.name}（避免重复导入）")
    print(f"📋 报告已写入 {REPORT_FILE.name}")


if __name__ == "__main__":
    main()
