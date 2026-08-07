# -*- coding: utf-8 -*-
"""
BajuStyle 网站管理器 — 多图上传 + AI 一键翻译 + 一键部署
双击 启动管理器.bat 或: python manage.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None
import subprocess
import re
import threading
import traceback
import time
try:
    import requests
except Exception:
    requests = None
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
BASE_DIR = Path(__file__).parent.resolve()
PRODUCTS_FILE = BASE_DIR / "products.json"
IMAGES_DIR = BASE_DIR / "images"
CONFIG_FILE = BASE_DIR / "config.json"
HTML_FILES = ["index.html", "clothing.html", "shoes.html", "bags.html", "product-detail.html"]

# ============================================================
# AI 翻译器（使用 DeepSeek API）
# ============================================================
class Translator:
    def __init__(self):
        self.api_key = ""
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self._load_config()

    def _load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                ds = cfg.get("deepseek", {})
                self.api_key = ds.get("api_key", "")
                self.api_url = ds.get("api_url", self.api_url)
                self.model = ds.get("model", self.model)
            except:
                pass

    def translate(self, text, target_langs):
        """
        翻译文本到目标语言
        返回: (result_dict, error_message)
              成功 → ({"en":"...","ms":"...","vi":"..."}, None)
              失败 → ({}, "错误原因")
        """
        if not self.api_key:
            return {}, "未配置 DeepSeek API Key，请在 config.json 中设置"
        if not text or not text.strip():
            return {}, "请输入要翻译的文本"

        lang_names = {'en': 'English', 'ms': 'Bahasa Melayu', 'vi': 'Vietnamese'}
        targets = ', '.join(lang_names.get(l, l) for l in target_langs)

        prompt = (
            'Output a JSON object with exactly these keys: "en", "ms", "vi". '
            'Translate this Chinese fashion product text into English (en), Bahasa Melayu (ms), Vietnamese (vi). '
            'Example output: {"en":"Fashion dress","ms":"Gaun fesyen","vi":"Vay thoi trang"}\n\n'
            'Chinese text to translate: ' + text
        )

        try:
            resp = requests.post(
                self.api_url,
                headers={
                    "Authorization": "Bearer " + self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": max(512, min(4096, len(text) * 6)),
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            if resp.status_code != 200:
                try:
                    err = resp.json()
                except:
                    err = {}
                return {}, "API 返回错误 (HTTP {}):\n{}".format(
                    resp.status_code,
                    err.get('error', {}).get('message', resp.text[:300])
                )

            # 安全解析 API 响应
            try:
                content = resp.json()["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, TypeError) as e:
                return {}, "API 返回结构异常: {}".format(str(e))

            # ── 尝试多种方式提取 JSON ──
            result = None

            # 方式1：直接解析
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                pass

            # 方式2：去掉 markdown 代码块包裹 ```json ... ```
            if result is None and "```" in content:
                parts = content.split("```")
                if len(parts) >= 3:
                    inner = parts[1]
                    if inner.startswith("json"):
                        inner = inner[4:]
                    try:
                        result = json.loads(inner.strip())
                    except json.JSONDecodeError:
                        pass

            # 方式3：正则提取最外层 JSON 对象
            if result is None:
                m = re.search(r'\{.*\}', content, re.DOTALL)
                if m:
                    try:
                        result = json.loads(m.group())
                    except json.JSONDecodeError:
                        pass

            if result is None:
                return {}, (
                    "AI 返回格式异常，无法解析 JSON。\n\n"
                    "原始返回内容:\n" + content[:500]
                )

            # ── 统一 key 名称：兼容 AI 偶尔用全名的情况 ──
            key_map = {
                'english': 'en', 'en': 'en',
                'malay': 'ms', 'ms': 'ms', 'bahasa': 'ms', 'bahasa melayu': 'ms',
                'vietnamese': 'vi', 'vi': 'vi',
            }
            normalized = {}
            for k, v in result.items():
                target = key_map.get(k.lower().strip(), None)
                if target:
                    normalized[target] = v
            if not normalized:
                return {}, "AI 返回的 JSON key 无法识别: " + str(list(result.keys()))
            return normalized, None

        except requests.exceptions.Timeout:
            return {}, "翻译请求超时（30秒），请检查网络"
        except requests.exceptions.ConnectionError:
            return {}, "网络连接失败，请检查网络设置"
        except Exception as e:
            return {}, f"翻译异常: {type(e).__name__}: {e}"


# ============================================================
# 数据管理器
# ============================================================
class DataManager:
    def __init__(self):
        self.data = None

    def load(self):
        if PRODUCTS_FILE.exists():
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "wechat_id": "GDFK17888",
                "categories": {},
                "products": {},
                "homepage_products": {"new_arrivals": [], "best_sellers": []}
            }
            self.save()
        # 确保所有商品都有 images 字段
        for cat_id, prods in self.data.get("products", {}).items():
            for p in prods:
                if "images" not in p:
                    p["images"] = [p.get("img", "")] if p.get("img") else []
                if "desc" not in p:
                    p["desc"] = ""
                if "cat" not in p:
                    p["cat"] = cat_id
        return self.data

    def save(self):
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def get_next_id(self, cat_id):
        products = self.data.get("products", {}).get(cat_id, [])
        max_num = 0
        prefix = cat_id[0]
        for p in products:
            match = re.match(rf'{prefix}(\d+)', p.get('id', ''))
            if match:
                max_num = max(max_num, int(match.group(1)))
        return f"{prefix}{max_num + 1}"

    def total_products(self):
        return sum(len(v) for v in self.data.get("products", {}).values())


# ============================================================
# HTML 生成器
# ============================================================
class HTMLGenerator:
    START = "<!-- @PRODUCTS_START -->"
    END = "<!-- @PRODUCTS_END -->"

    @staticmethod
    def _esc(v):
        return str(v).replace("'", "\\'").replace('\n', '\\n').replace('\r', '')

    @staticmethod
    def _img(p):
        """获取封面图"""
        imgs = p.get("images", [])
        return imgs[0] if imgs else p.get("img", "")

    @staticmethod
    def _imgs(p):
        """获取全部图片（输出为 JS 数组字面量）"""
        imgs = p.get("images", [])
        if not imgs:
            single = p.get("img", "")
            imgs = [single] if single else []
        return json.dumps(imgs, ensure_ascii=False)

    @staticmethod
    def _desc_fields(p):
        """生成四语描述 JS 字段"""
        desc = p.get('desc', '')
        if isinstance(desc, dict):
            return (f"descZh: '{HTMLGenerator._esc(desc.get('zh',''))}', "
                    f"descEn: '{HTMLGenerator._esc(desc.get('en',''))}', "
                    f"descMs: '{HTMLGenerator._esc(desc.get('ms',''))}', "
                    f"descVi: '{HTMLGenerator._esc(desc.get('vi',''))}'")
        else:
            s = HTMLGenerator._esc(desc)
            return f"descZh: '{s}', descEn: '', descMs: '', descVi: ''"

    @staticmethod
    def _js_simple(p):
        return ("        { id: '%s', "
                "name: '%s', nameZh: '%s', nameMs: '%s', nameVi: '%s', "
                "emoji: '%s', price: '%s', subcat: '%s', "
                "%s, "
                "img: '%s', images: %s }"
                ) % (
            p['id'],
            HTMLGenerator._esc(p['name']), HTMLGenerator._esc(p['nameZh']),
            HTMLGenerator._esc(p['nameMs']), HTMLGenerator._esc(p['nameVi']),
            p['emoji'], HTMLGenerator._esc(p.get('price', '')),
            HTMLGenerator._esc(p.get('subcat', '')),
            HTMLGenerator._desc_fields(p),
            HTMLGenerator._img(p), HTMLGenerator._imgs(p)
        )

    @staticmethod
    def _js_full(p):
        return ("        { id: '%s', "
                "name: '%s', nameZh: '%s', nameMs: '%s', nameVi: '%s', "
                "img: '%s', images: %s, cat: '%s', subcat: '%s', "
                "emoji: '%s', price: '%s', "
                "%s }"
                ) % (
            p['id'],
            HTMLGenerator._esc(p['name']), HTMLGenerator._esc(p['nameZh']),
            HTMLGenerator._esc(p['nameMs']), HTMLGenerator._esc(p['nameVi']),
            HTMLGenerator._img(p), HTMLGenerator._imgs(p),
            p.get('cat', ''), HTMLGenerator._esc(p.get('subcat', '')),
            p['emoji'], HTMLGenerator._esc(p.get('price', '')),
            HTMLGenerator._desc_fields(p)
        )

    @staticmethod
    def _js_extended(p, cat_data):
        cat_id = p.get('cat', '')
        cn = cat_data.get(cat_id, {}).get("name", {})
        return ("        { id: '%s', "
                "name: '%s', nameZh: '%s', nameMs: '%s', nameVi: '%s', "
                "img: '%s', images: %s, cat: '%s', subcat: '%s', "
                "catName: '%s', catNameZh: '%s', catNameMs: '%s', catNameVi: '%s', "
                "emoji: '%s', price: '%s', "
                "%s }"
                ) % (
            p['id'],
            HTMLGenerator._esc(p['name']), HTMLGenerator._esc(p['nameZh']),
            HTMLGenerator._esc(p['nameMs']), HTMLGenerator._esc(p['nameVi']),
            HTMLGenerator._img(p), HTMLGenerator._imgs(p),
            cat_id, HTMLGenerator._esc(p.get('subcat', '')),
            cn.get('en', ''), cn.get('zh', ''), cn.get('ms', ''), cn.get('vi', ''),
            p['emoji'], HTMLGenerator._esc(p.get('price', '')),
            HTMLGenerator._desc_fields(p)
        )


    @classmethod
    def _site_categories_js(cls, data):
        """生成全站分类数据（含子分类），供前端运行时翻译导航/卡片"""
        cats = data.get("categories", {})
        out = {}
        for cid, ci in cats.items():
            out[cid] = {
                "name": ci.get("name", {}),
                "subcategories": ci.get("subcategories", []) or [],
            }
        return "const siteCategories = " + json.dumps(out, ensure_ascii=False) + ";"

    @classmethod
    def _category_meta_js(cls, cat):
        """生成当前分类页元数据（主图 + 子分类 + 名称），供前端渲染横幅与筛选"""
        meta = {
            "id": cat.get("id"),
            "name": cat.get("name", {}),
            "description": cat.get("description", {}),
            "hero": cat.get("hero", "") or "",
            "subcategories": cat.get("subcategories", []) or [],
        }
        return "const categoryMeta = " + json.dumps(meta, ensure_ascii=False) + ";"

    @classmethod
    def _replace(cls, filepath, new_content):
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        if cls.START not in text or cls.END not in text:
            raise ValueError(f"文件中缺少标记: {filepath}")
        before = text.split(cls.START)[0]
        after = text.split(cls.END)[1]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{before}{cls.START}\n{new_content}\n{cls.END}{after}")

    @classmethod
    def generate_index(cls, data):
        products = data.get("products", {})
        cats = data.get("categories", {})
        parts = []
        for cat_id in cats.keys():
            prods = products.get(cat_id, [])
            items = ",\n".join(cls._js_full(p) for p in prods)
            parts.append(f"    {cat_id}: [\n{items}\n    ]")
        content = "const products = {\n" + ",\n".join(parts) + "\n};"
        cls._replace(BASE_DIR / "index.html", content)

    @classmethod
    def generate_category_page(cls, data, cat_id):
        cats = data.get("categories", {})
        if cat_id not in cats:
            return
        cat = cats[cat_id]
        fname = cat.get("filename", f"{cat_id}.html")
        fpath = BASE_DIR / fname
        is_known = fname in {"clothing.html", "shoes.html", "bags.html"}
        if not fpath.exists():
            # 新建分类：以 clothing.html 为模板复制，再替换标题/导航
            src = BASE_DIR / "clothing.html"
            if not src.exists():
                return
            shutil.copyfile(src, fpath)
            # 复制自模板后一律重写页面元信息（标题/描述/横幅），避免沿用模板的 Clothing 文案
            cls._update_page_meta(fpath, cat)
        products = data.get("products", {}).get(cat_id, [])
        items = ",\n".join(cls._js_simple(p) for p in products)
        content = f"const products = [\n{items}\n];"
        cls._replace(fpath, content)
        cls._update_nav_in_file(fpath, fname, data)

    @classmethod
    def generate_product_detail(cls, data):
        products = data.get("products", {})
        cat_data = data.get("categories", {})
        parts = []
        for cat_id in cat_data.keys():
            prods = products.get(cat_id, [])
            items = ",\n".join(cls._js_extended(p, cat_data) for p in prods)
            parts.append(f"    {cat_id}: [\n{items}\n    ]")
        obj = "const products = {\n" + ",\n".join(parts) + "\n};"
        allcats = list(cat_data.keys())
        allp = "const allProducts = [" + ", ".join(f"...products.{c}" for c in allcats) + "];"
        cls._replace(BASE_DIR / "product-detail.html", f"{obj}\n{allp}")

    # ========== 导航 / 分类卡片 动态生成 ==========
    GRADS = [
        "linear-gradient(135deg,#fce4ec,#f8bbd0)",
        "linear-gradient(135deg,#f3e5f5,#e1bee7)",
        "linear-gradient(135deg,#fff3e0,#ffe0b2)",
        "linear-gradient(135deg,#e3f2fd,#bbdefb)",
        "linear-gradient(135deg,#e8f5e9,#c8e6c9)",
    ]

    @classmethod
    def _replace_block(cls, text, start, end, new):
        if start not in text or end not in text:
            return text
        before = text.split(start)[0]
        after = text.split(end)[1]
        return f"{before}{start}\n{new}\n{end}{after}"

    @classmethod
    def _nav_links_html(cls, current_page, data):
        cats = data.get("categories", {})
        lines = []
        home_cls = ' class="active"' if current_page == 'index' else ''
        lines.append('            <a href="index.html"%s data-key="navHome">Home</a>' % home_cls)
        for cid, ci in cats.items():
            fname = ci.get("filename", cid + ".html")
            active = ' class="active"' if current_page == fname else ''
            name = ci.get("name", {}).get("en", cid)
            subs = ci.get("subcategories", []) or []
            if subs:
                lines.append('            <div class="nav-item">')
                lines.append('                <a href="%s"%s data-cat="%s">%s</a>' % (fname, active, cid, name))
                lines.append('                <div class="nav-dropdown">')
                for s in subs:
                    sid = s.get("id", "")
                    sname = s.get("name", {}).get("en", sid)
                    lines.append('                    <a href="%s?sub=%s" data-subcat="%s:%s">%s</a>'
                                 % (fname, sid, cid, sid, sname))
                lines.append('                </div>')
                lines.append('            </div>')
            else:
                lines.append('            <a href="%s"%s data-cat="%s">%s</a>' % (fname, active, cid, name))
        return "\n".join(lines)

    @classmethod
    def _mobile_nav_html(cls, current_page, data):
        cats = data.get("categories", {})
        lines = []
        home_cls = ' class="active"' if current_page == 'index' else ''
        lines.append('            <a href="index.html"%s data-key="navHome">Home</a>' % home_cls)
        for cid, ci in cats.items():
            fname = ci.get("filename", cid + ".html")
            active = ' class="active"' if current_page == fname else ''
            name = ci.get("name", {}).get("en", cid)
            lines.append('            <a href="%s"%s data-cat="%s">%s</a>' % (fname, active, cid, name))
            for s in (ci.get("subcategories", []) or []):
                sid = s.get("id", "")
                sname = s.get("name", {}).get("en", sid)
                lines.append('            <a href="%s?sub=%s" class="sub-link" data-subcat="%s:%s">— %s</a>'
                             % (fname, sid, cid, sid, sname))
        return "\n".join(lines)

    @classmethod
    def _footer_shop_html(cls, data):
        cats = data.get("categories", {})
        lines = []
        for cid, ci in cats.items():
            fname = ci.get("filename", cid + ".html")
            name = ci.get("name", {}).get("en", cid)
            lines.append('            <a href="%s">%s</a><br>' % (fname, name))
        return "\n".join(lines)

    @classmethod
    def _cat_cards_html(cls, data):
        cats = data.get("categories", {})
        lines = []
        for i, (cid, ci) in enumerate(cats.items()):
            fname = ci.get("filename", cid + ".html")
            name = ci.get("name", {})
            en = name.get("en", cid)
            zh = name.get("zh", "")
            grad = cls.GRADS[i % len(cls.GRADS)]
            hero = ci.get("hero", "") or ""
            if hero:
                img_div = ('            <div class="cat-card-img" style="background-image:url(\'%s\')"></div>'
                           % hero)
            else:
                img_div = ('            <div class="cat-card-img" data-cat="%s" style="background:%s;'
                           'display:flex;align-items:center;justify-content:center;'
                           'font-size:2.4rem;font-weight:700;color:#888;">%s</div>'
                           % (cid, grad, en))
            lines.append(
                '        <div class="cat-card" onclick="location.href=\'%s\'">\n'
                '%s\n'
                '            <div class="cat-card-overlay">\n'
                '                <h3 data-cat="%s">%s</h3>\n'
                '                <p>%s</p>\n'
                '            </div>\n'
                '        </div>' % (fname, img_div, cid, en, zh)
            )
        return "\n".join(lines)

    @classmethod
    def _update_page_meta(cls, fpath, cat):
        text = fpath.read_text(encoding="utf-8")
        name = cat.get("name", {})
        en = name.get("en", fpath.stem)
        zh = name.get("zh", "")
        ms = name.get("ms", "")
        vi = name.get("vi", "")
        text = re.sub(r"<title>.*?</title>", "<title>%s — BajuStyle</title>" % en, text, count=1, flags=re.S)
        # 使用精确标记替换页面标题，避免 <p[^>]*> 正则将 SVG <path> 误识别为 <p>
        text = cls._replace_block(text, "<!-- @PAGE_TITLE_START -->", "<!-- @PAGE_TITLE_END -->",
                                  en)
        text = cls._replace_block(text, "<!-- @PAGE_SUBTITLE_START -->", "<!-- @PAGE_SUBTITLE_END -->",
                                  "%s · %s · %s" % (zh, ms, vi))
        text = re.sub(r'<meta name="description" content="[^"]*">',
                      '<meta name="description" content="Shop %s at BajuStyle. Premium fashion shipped worldwide from China to Malaysia, Singapore & Vietnam.">' % en,
                      text, count=1)
        fpath.write_text(text, encoding="utf-8")

    @classmethod
    def _update_nav_in_file(cls, fpath, current_page, data):
        text = fpath.read_text(encoding="utf-8")
        text = cls._replace_block(text, "<!-- @NAV_START -->", "<!-- @NAV_END -->", cls._nav_links_html(current_page, data))
        text = cls._replace_block(text, "<!-- @MOBILE_NAV_START -->", "<!-- @MOBILE_NAV_END -->", cls._mobile_nav_html(current_page, data))
        text = cls._replace_block(text, "<!-- @FOOTER_SHOP_START -->", "<!-- @FOOTER_SHOP_END -->", cls._footer_shop_html(data))
        if fpath.name == "index.html":
            text = cls._replace_block(text, "<!-- @CATGRID_START -->", "<!-- @CATGRID_END -->", cls._cat_cards_html(data))
        text = cls._replace_block(text, "<!-- @SITECATS_START -->", "<!-- @SITECATS_END -->", cls._site_categories_js(data))
        # 分类页写入 categoryMeta（index / product-detail 无）
        base = current_page[:-5] if current_page.endswith(".html") else current_page
        cat = data.get("categories", {}).get(base)
        if cat and current_page != "index":
            text = cls._replace_block(text, "<!-- @CATMETA_START -->", "<!-- @CATMETA_END -->", cls._category_meta_js(cat))
        fpath.write_text(text, encoding="utf-8")

    @classmethod
    def update_nav_all(cls, data):
        known = {
            "index.html": "index",
            "clothing.html": "clothing.html",
            "shoes.html": "shoes.html",
            "bags.html": "bags.html",
            "product-detail.html": "product-detail.html",
        }
        for fname, cur in known.items():
            fp = BASE_DIR / fname
            if fp.exists():
                cls._update_nav_in_file(fp, cur, data)
        known_fnames = set(known.keys())
        for cid, ci in data.get("categories", {}).items():
            f = ci.get("filename", cid + ".html")
            if f in known_fnames:
                continue
            fp = BASE_DIR / f
            if fp.exists():
                cls._update_nav_in_file(fp, f, data)

    @classmethod
    def regenerate_all(cls, data):
        cls.generate_index(data)
        for cat_id in data.get("categories", {}).keys():
            cls.generate_category_page(data, cat_id)
        cls.generate_product_detail(data)
        cls.update_nav_all(data)


# ============================================================
# Git 管理器
# ============================================================
class GitManager:
    def __init__(self):
        self.repo = str(BASE_DIR)

    def _run(self, cmd, timeout=30):
        try:
            r = subprocess.run(cmd, shell=True, cwd=self.repo,
                               capture_output=True, text=True, timeout=timeout)
            return r.returncode == 0, r.stdout + r.stderr
        except subprocess.TimeoutExpired:
            return False, "操作超时"
        except Exception as e:
            return False, str(e)

    def test_connection(self):
        """Test SSH connectivity to GitHub (port 22, works where HTTPS 443 may be blocked)"""
        ok, out = self._run('ssh -T -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new git@github.com 2>&1', timeout=15)
        return ok or "successfully authenticated" in out.lower()

    def get_status(self):
        ok, out = self._run("git status --porcelain")
        return out.strip() if ok else ""

    def commit_and_push(self, message, token=""):
        ok, out = self._run("git add -A 2>&1")
        if not ok:
            return False, f"git add 失败:\n{out}"
        ok, out = self._run(f'git commit -m "{message}" 2>&1')
        if not ok:
            lo = out.lower()
            if "nothing to commit" in lo or "nothing added to commit" in lo or "no changes added" in lo:
                return False, "没有变更需要提交"
            return False, f"git commit 失败:\n{out}"
        # SSH primary; HTTPS with token as fallback
        ok, out = self._run("git push origin main 2>&1", timeout=60)
        if ok:
            return True, f"推送成功 (SSH)!\n{out}"
        if token:
            push_url = f"https://{token}@github.com/zjlxd388/bajustyle.git"
            ok2, out2 = self._run(f"git push {push_url} main 2>&1", timeout=60)
            if ok2:
                return True, f"推送成功 (HTTPS)!\n{out2}"
            return False, f"git push 失败:\nSSH: {out}\nHTTPS: {out2}"
        return False, f"git push 失败 (SSH):\n{out}"


# ============================================================
# GUI 主程序
# ============================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("BajuStyle 网站管理器 — DY·高端服饰")
        self.root.geometry("1200x780")
        self.root.minsize(1000, 600)

        self.dm = DataManager()
        self.data = self.dm.load()
        self.gen = HTMLGenerator()
        self.git = GitManager()
        self.translator = Translator()

        self.selected_idx = None
        self._images = []  # 内部图片列表
        self.current_cat = tk.StringVar(value="clothing")
        self._cat_id_to_name = {}  # "clothing" → "衣服"
        self._cat_name_to_id = {}  # "衣服" → "clothing"
        self._subcat_ids = ['']     # 当前分类的子分类 id 列表（首个为空=默认）
        self._subcat_disp = ['无（默认）']  # 对应显示名
        self.subcat_var = tk.StringVar(value="无（默认）")
        self._build_cat_maps()
        self.github_token = tk.StringVar()
        self.github_user = tk.StringVar(value="zjlxd388")
        self.status_text = tk.StringVar(value="就绪 — 选择左侧商品开始编辑")

        self._load_token()
        self._build_ui()
        self._refresh_cats()
        self.refresh_list()

    # ========== Token 持久化 ==========
    def _token_file(self):
        return BASE_DIR / ".github_token"

    def _load_token(self):
        tf = self._token_file()
        if tf.exists():
            try:
                with open(tf, 'r') as f:
                    d = json.load(f)
                    self.github_token.set(d.get("token", ""))
                    self.github_user.set(d.get("user", "zjlxd388"))
            except:
                pass

    def _save_token(self):
        try:
            with open(self._token_file(), 'w') as f:
                json.dump({"user": self.github_user.get(), "token": self.github_token.get()}, f)
        except:
            pass

    # ==================== UI 搭建 ====================
    def _build_ui(self):
        # ---- 顶部 ----
        tb = ttk.Frame(self.root, padding=5)
        tb.pack(fill='x', padx=5, pady=(5, 0))
        ttk.Label(tb, text="🛠 BajuStyle 网站管理器",
                  font=('Microsoft YaHei', 14, 'bold')).pack(side='left')
        self.stats_label = ttk.Label(tb, text="", font=('Microsoft YaHei', 9))
        self.stats_label.pack(side='left', padx=20)
        ttk.Button(tb, text="🔄 重新生成 HTML", command=self._threaded_regenerate).pack(side='right', padx=3)
        ttk.Button(tb, text="💾 保存数据", command=self._save).pack(side='right', padx=3)
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', padx=5)

        # ---- 主体 ----
        main = ttk.Frame(self.root)
        main.pack(fill='both', expand=True, padx=5, pady=5)

        # ======== 左侧 ========
        left = ttk.Frame(main, width=340)
        left.pack(side='left', fill='both', expand=True)
        left.pack_propagate(False)

        cat_frame = ttk.LabelFrame(left, text="📂 分类", padding=5)
        cat_frame.pack(fill='x', pady=(0, 5))
        self.cat_btn_frame = ttk.Frame(cat_frame)
        self.cat_btn_frame.pack(fill='x')
        ttk.Button(cat_frame, text="➕ 新建分类", command=self._category_dialog).pack(anchor='w', pady=(4, 0))
        ttk.Button(cat_frame, text="✏️ 编辑分类", command=lambda: self._category_dialog(self.current_cat.get())).pack(anchor='w', pady=(2, 0))

        list_frame = ttk.LabelFrame(left, text="📦 商品列表", padding=5)
        list_frame.pack(fill='both', expand=True)

        # 固定行高以适配缩略图
        tree_style = ttk.Style()
        tree_style.configure('ProductList.Treeview', rowheight=48)

        cols = ('name', 'price')
        self.tree = ttk.Treeview(list_frame, columns=cols, show='tree headings',
                                  selectmode='browse', height=6, style='ProductList.Treeview')
        self.tree.heading('#0', text='封面'); self.tree.column('#0', width=52, anchor='center', stretch=False)
        self.tree.heading('name', text='商品名称'); self.tree.column('name', width=180, anchor='w')
        self.tree.heading('price', text='价格'); self.tree.column('price', width=60, anchor='center', stretch=False)
        self.tree.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        sb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        # 缩略图缓存（防止被 GC）
        self._thumb_cache = {}

        btn_row = ttk.Frame(left)
        btn_row.pack(fill='x', pady=(5, 0))
        ttk.Button(btn_row, text="➕ 添加", command=self._add_product).pack(side='left', padx=2)
        ttk.Button(btn_row, text="🗑 删除", command=self._delete_product).pack(side='left', padx=2)
        ttk.Button(btn_row, text="⬆", command=lambda: self._move(-1)).pack(side='left', padx=1)
        ttk.Button(btn_row, text="⬇", command=lambda: self._move(1)).pack(side='left', padx=1)

        # ======== 右侧：编辑区（可滚动）========
        right = ttk.Frame(main, width=500)
        right.pack(side='right', fill='both', expand=True, padx=(5, 0))
        right.pack_propagate(False)

        edit_canvas = tk.Canvas(right, highlightthickness=0)
        edit_scrollbar = ttk.Scrollbar(right, orient='vertical', command=edit_canvas.yview)
        edit_inner = ttk.Frame(edit_canvas)
        edit_inner.bind("<Configure>", lambda e: edit_canvas.configure(scrollregion=edit_canvas.bbox("all")))
        edit_canvas.create_window((0, 0), window=edit_inner, anchor='nw', width=480)
        edit_canvas.configure(yscrollcommand=edit_scrollbar.set)
        edit_canvas.pack(side='left', fill='both', expand=True)
        edit_scrollbar.pack(side='right', fill='y')

        def _on_mousewheel(event):
            edit_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        edit_canvas.bind("<Enter>", lambda e: edit_canvas.bind_all("<MouseWheel>", _on_mousewheel))
        edit_canvas.bind("<Leave>", lambda e: edit_canvas.unbind_all("<MouseWheel>"))

        edit_frame = ttk.LabelFrame(edit_inner, text="✏️ 商品编辑", padding=10)
        edit_frame.pack(fill='both', expand=True)

        # ===== 多图管理区 =====
        ttk.Label(edit_frame, text="📷 商品图片（第一张为封面）:",
                  font=('Microsoft YaHei', 10, 'bold')).pack(anchor='w', pady=(0, 4))

        # 图片列表 + 按钮
        img_list_frame = ttk.Frame(edit_frame)
        img_list_frame.pack(fill='x', pady=(0, 8))

        self.img_listbox = tk.Listbox(img_list_frame, height=4, font=('Microsoft YaHei', 9),
                                       selectmode='extended', exportselection=False)
        self.img_listbox.pack(side='left', fill='x', expand=True)
        img_sb = ttk.Scrollbar(img_list_frame, orient='vertical', command=self.img_listbox.yview)
        img_sb.pack(side='right', fill='y')
        self.img_listbox.configure(yscrollcommand=img_sb.set)

        img_btn_grid = ttk.Frame(edit_frame)
        img_btn_grid.pack(fill='x', pady=(0, 10))
        ttk.Button(img_btn_grid, text="📁 批量添加图片",
                   command=self._add_images).pack(side='left', padx=2)
        ttk.Button(img_btn_grid, text="🗑 移除选中",
                   command=self._remove_image).pack(side='left', padx=2)
        ttk.Button(img_btn_grid, text="👑 设为封面",
                   command=self._set_cover).pack(side='left', padx=2)
        ttk.Button(img_btn_grid, text="⬆", command=lambda: self._move_image(-1)).pack(side='left', padx=1)
        ttk.Button(img_btn_grid, text="⬇", command=lambda: self._move_image(1)).pack(side='left', padx=1)
        ttk.Label(img_btn_grid, text="  👑 = 封面图",
                  font=('Microsoft YaHei', 8), foreground='#999').pack(side='left', padx=8)

        # ===== 分类 + 操作按钮（移到原 emoji 位置）=====
        cat_act_frame = ttk.Frame(edit_frame)
        cat_act_frame.pack(fill='x', pady=(4, 10))
        ttk.Label(cat_act_frame, text="📂 所属分类:",
                  font=('Microsoft YaHei', 10)).pack(side='left')
        self.edit_cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(cat_act_frame, textvariable=self.edit_cat_var,
                                       state='readonly', width=12, font=('Microsoft YaHei', 10))
        self.cat_combo.pack(side='left', padx=4)
        self.cat_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_subcat_combo())
        ttk.Label(cat_act_frame, text="子分类:", font=('Microsoft YaHei', 9)).pack(side='left', padx=(8, 0))
        self.subcat_combo = ttk.Combobox(cat_act_frame, textvariable=self.subcat_var,
                                         state='readonly', width=12, font=('Microsoft YaHei', 9))
        self.subcat_combo.pack(side='left', padx=2)
        ttk.Button(cat_act_frame, text="🗑 删除",
                   command=self._delete_product).pack(side='right', padx=2)
        ttk.Button(cat_act_frame, text="💾 保存",
                   command=self._save_product).pack(side='right', padx=2)
        ttk.Button(cat_act_frame, text="🔄 清空",
                   command=self._reset_form).pack(side='right', padx=2)
        ttk.Button(cat_act_frame, text="🆕 新建",
                   command=self._add_product).pack(side='right', padx=2)

        # ===== 商品名称（四语）+ 翻译按钮 =====
        name_header = ttk.Frame(edit_frame)
        name_header.pack(fill='x')
        ttk.Label(name_header, text="📝 商品名称（四种语言）:",
                  font=('Microsoft YaHei', 10, 'bold')).pack(side='left')
        ttk.Button(name_header, text="🌐 一键翻译名称",
                   command=self._translate_names).pack(side='right')

        self.name_vars = {}
        labels = [("英文名 (English):", "name"), ("中文名 (中文):", "nameZh"),
                   ("马来文 (Bahasa Melayu):", "nameMs"), ("越南文 (Tiếng Việt):", "nameVi")]
        for lbl, key in labels:
            ttk.Label(edit_frame, text=f"   {lbl}").pack(anchor='w')
            v = tk.StringVar(); self.name_vars[key] = v
            ttk.Entry(edit_frame, textvariable=v, width=48).pack(fill='x', pady=(2, 6))

        # ===== 价格（CNY 格式）=====
        ttk.Label(edit_frame, text="💰 价格（人民币，留空 = 显示「微信询价」）:",
                  font=('Microsoft YaHei', 10)).pack(anchor='w', pady=(2, 2))
        price_frame = ttk.Frame(edit_frame)
        price_frame.pack(anchor='w', fill='x', pady=(2, 10))
        ttk.Label(price_frame, text="CNY ¥",
                  font=('Microsoft YaHei', 11, 'bold'), foreground='#c00').pack(side='left')
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(price_frame, textvariable=self.price_var, width=12,
                                      font=('Microsoft YaHei', 12))
        self.price_entry.pack(side='left', padx=3)
        ttk.Label(price_frame, text=".00",
                  font=('Microsoft YaHei', 12)).pack(side='left')
        ttk.Label(price_frame, text="  只填数字即可",
                  font=('Microsoft YaHei', 8), foreground='#999').pack(side='left', padx=8)
        # 失去焦点时自动格式化
        self.price_entry.bind('<FocusOut>', self._format_price)
        self.price_entry.bind('<FocusIn>', self._unformat_price)

        # ===== 商品描述（四语标签页）=====
        desc_header = ttk.Frame(edit_frame)
        desc_header.pack(fill='x')
        ttk.Label(desc_header, text="📋 商品描述（四种语言）:",
                  font=('Microsoft YaHei', 10, 'bold')).pack(side='left')
        ttk.Button(desc_header, text="🌐 一键翻译描述",
                   command=self._translate_desc).pack(side='right')

        self.desc_notebook = ttk.Notebook(edit_frame, height=100)
        self.desc_texts = {}  # key → Text widget
        for lang_key, lang_label in [('zh', ' 中文 '), ('en', ' English '),
                                       ('ms', ' BM '), ('vi', ' Việt ')]:
            tab = ttk.Frame(self.desc_notebook)
            text_widget = tk.Text(tab, width=46, height=4, font=('Microsoft YaHei', 9),
                                  wrap='word', relief='flat', borderwidth=0)
            text_widget.pack(fill='both', expand=True, padx=3, pady=3)
            self.desc_texts[lang_key] = text_widget
            self.desc_notebook.add(tab, text=lang_label)
        self.desc_notebook.pack(fill='x', pady=(2, 10))

        # ======== 底部部署区 ========
        bot = ttk.Frame(self.root)
        bot.pack(fill='x', padx=5, pady=(0, 5))

        dep = ttk.LabelFrame(bot, text="🚀 一键部署到网站", padding=8)
        dep.pack(fill='x')

        dr = ttk.Frame(dep); dr.pack(fill='x')
        ttk.Label(dr, text="GitHub 用户名:").pack(side='left')
        ttk.Entry(dr, textvariable=self.github_user, width=14).pack(side='left', padx=3)
        ttk.Label(dr, text="Token(可选):").pack(side='left', padx=(8, 0))
        self.token_entry = ttk.Entry(dr, textvariable=self.github_token, width=32, show='*')
        self.token_entry.pack(side='left', padx=3)
        ttk.Button(dr, text="🔍 测试连接", command=self._test_github).pack(side='left', padx=3)
        ttk.Button(dr, text="🚀 部署上线", command=self._threaded_deploy).pack(side='left', padx=3)
        ttk.Button(dr, text="📥 从网站导入", command=self._import_from_website).pack(side='left', padx=3)
        ttk.Button(dr, text="👁 显示", command=lambda: self._toggle_token()).pack(side='left')

        tip_text = ("💡 优先使用 SSH 推送，Token 为备选（HTTPS 被封锁时 SSH 仍可工作）| "
                     "Token 获取: github.com → Settings → Developer settings → PAT → 勾选 repo")
        ttk.Label(dep, text=tip_text, font=('Microsoft YaHei', 8), foreground='#999').pack(anchor='w', pady=(4, 0))

        ttk.Label(bot, textvariable=self.status_text, anchor='w',
                  font=('Microsoft YaHei', 9)).pack(fill='x', pady=(3, 0))

    def _toggle_token(self):
        self.token_entry.configure(show='' if self.token_entry.cget('show') == '*' else '*')

    # ==================== 多图管理 ====================
    def _refresh_image_list(self):
        """从 self._images 刷新列表显示"""
        self.img_listbox.delete(0, 'end')
        for i, img_path in enumerate(self._images):
            prefix = "👑 " if i == 0 else "   "
            name = Path(img_path).name if img_path else "(空)"
            self.img_listbox.insert('end', f"{prefix}{name}")

    def _add_images(self):
        """批量添加图片"""
        paths = filedialog.askopenfilenames(
            title="选择商品图片（可多选）",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.webp"), ("所有文件", "*.*")]
        )
        if not paths:
            return

        imported = []
        for path in paths:
            src = Path(path)
            dst_name = src.name
            dst = IMAGES_DIR / dst_name
            if dst.exists():
                dst_name = f"{src.stem}_{int(time.time() * 1000) % 100000}{src.suffix}"
                dst = IMAGES_DIR / dst_name
            shutil.copy2(src, dst)
            imported.append(f"images/{dst_name}")

        self._images.extend(imported)
        self._refresh_image_list()
        self.status_text.set(f"📷 已导入 {len(imported)} 张图片，共 {len(self._images)} 张")

    def _remove_image(self):
        """移除选中的图片"""
        sel = self.img_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择要移除的图片")
            return
        # 从后往前删除
        for idx in sorted(sel, reverse=True):
            if idx < len(self._images):
                self._images.pop(idx)
        self._refresh_image_list()
        self.status_text.set(f"🗑 已移除，剩余 {len(self._images)} 张图片")

    def _set_cover(self):
        """将选中图片设为封面（移到第一位）"""
        sel = self.img_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先选择要设为封面的图片")
            return
        idx = sel[0]
        if 0 <= idx < len(self._images):
            img = self._images.pop(idx)
            self._images.insert(0, img)
        self._refresh_image_list()
        # 保持第一项选中
        self.img_listbox.selection_set(0)
        self.status_text.set("👑 封面图已更新")

    def _move_image(self, direction):
        """移动图片顺序"""
        sel = self.img_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        ni = idx + direction
        if 0 <= ni < len(self._images):
            self._images[idx], self._images[ni] = self._images[ni], self._images[idx]
            self._refresh_image_list()
            self.img_listbox.selection_set(ni)

    # ==================== 价格格式化 ====================
    def _format_price(self, event=None):
        raw = self.price_var.get().strip()
        if not raw:
            return
        raw = re.sub(r'[^\d.]', '', raw)
        if not raw:
            self.price_var.set('')
            return
        try:
            amount = float(raw)
            self.price_var.set("CNY {:,.2f}".format(amount))
        except ValueError:
            self.price_var.set(raw)

    def _unformat_price(self, event=None):
        raw = self.price_var.get().strip()
        if raw.startswith('CNY'):
            raw = re.sub(r'[^\d.]', '', raw)
            try:
                num = float(raw)
                if num == int(num):
                    self.price_var.set(str(int(num)))
                else:
                    self.price_var.set(str(num))
            except ValueError:
                pass

    def _price_for_storage(self):
        raw = self.price_var.get().strip()
        if not raw:
            return ''
        raw = re.sub(r'[^\d.]', '', raw)
        if not raw:
            return ''
        try:
            amount = float(raw)
            return "CNY {:,.2f}".format(amount)
        except ValueError:
            return raw

    def _price_for_display(self, price_str):
        if not price_str:
            self.price_var.set('')
            return
        num = re.sub(r'[^\d.]', '', str(price_str))
        if num:
            try:
                amount = float(num)
                if amount == int(amount):
                    self.price_var.set(str(int(amount)))
                else:
                    self.price_var.set(str(amount))
            except ValueError:
                self.price_var.set(num)
    def _translate_names(self):
        """翻译商品名称：中文 → EN, MS, VI"""
        zh_name = self.name_vars['nameZh'].get().strip()
        if not zh_name:
            en_name = self.name_vars['name'].get().strip()
            if not en_name:
                messagebox.showinfo("提示", "请先在「中文名」输入框填写商品名称，再点翻译")
                return
            zh_name = en_name

        self.status_text.set("🌐 正在翻译商品名称...")

        def run():
            result, error = self.translator.translate(zh_name, ['en', 'ms', 'vi'])
            self.root.after(0, lambda: self._apply_name_translation(result, error))

        threading.Thread(target=run, daemon=True).start()

    def _apply_name_translation(self, result, error):
        """应用名称翻译结果"""
        if error:
            self.status_text.set(f"❌ {error}")
            messagebox.showerror("翻译失败", error)
            return

        if result.get('en'):
            self.name_vars['name'].set(result['en'])
        if result.get('ms'):
            self.name_vars['nameMs'].set(result['ms'])
        if result.get('vi'):
            self.name_vars['nameVi'].set(result['vi'])

        self.status_text.set("✅ 名称翻译完成! 请检查并保存")

    def _translate_desc(self):
        """翻译商品描述 — 中文 → EN/MS/VI，填充到对应标签页"""
        desc_zh = self.desc_texts['zh'].get('1.0', 'end-1c').strip()
        if not desc_zh:
            messagebox.showinfo("提示", "请先在「中文」标签页填写描述，再点翻译")
            return

        self.status_text.set("🌐 正在翻译商品描述...")

        def run():
            result, error = self.translator.translate(desc_zh, ['en', 'ms', 'vi'])
            self.root.after(0, lambda: self._apply_desc_translation(result, error))

        threading.Thread(target=run, daemon=True).start()

    def _apply_desc_translation(self, result, error):
        """将翻译结果填入对应语言标签页"""
        if error:
            self.status_text.set(f"❌ {error}")
            messagebox.showerror("翻译失败", error)
            return

        lang_map = {'en': 'en', 'ms': 'ms', 'vi': 'vi'}
        for key, lang in lang_map.items():
            if result.get(key):
                w = self.desc_texts[lang]
                w.delete('1.0', 'end')
                w.insert('1.0', result[key])

        # 自动切换到英文标签页方便校对
        self.desc_notebook.select(1)
        self.status_text.set("✅ 描述翻译完成! 请切换到各语言标签页校对后保存")

    # ==================== 分类 ====================
    def _build_cat_maps(self):
        self._cat_id_to_name.clear()
        self._cat_name_to_id.clear()
        for cid, ci in self.data.get("categories", {}).items():
            zh = ci.get("name", {}).get("zh", cid)
            self._cat_id_to_name[cid] = zh
            self._cat_name_to_id[zh] = cid

    def _refresh_cats(self):
        self._build_cat_maps()
        for w in self.cat_btn_frame.winfo_children():
            w.destroy()
        for cid, ci in self.data.get("categories", {}).items():
            zh = ci.get("name", {}).get("zh", cid)
            ttk.Radiobutton(self.cat_btn_frame, text=zh,
                            variable=self.current_cat, value=cid,
                            command=self.refresh_list).pack(anchor='w', pady=1)
        zh_names = [self._cat_id_to_name.get(c, c) for c in self.data.get("categories", {}).keys()]
        self.cat_combo['values'] = zh_names
        if zh_names:
            self.cat_combo.set(zh_names[0])
        self._refresh_subcat_combo()

    def _refresh_subcat_combo(self):
        """根据商品表单当前选中的分类刷新「子分类」下拉框（显示中文名，存 id）。"""
        ev = getattr(self, 'edit_cat_var', None)
        if ev is not None and ev.get():
            cid = self._cat_name_to_id.get(ev.get(), self.current_cat.get())
        else:
            cid = self.current_cat.get()
        subs = self.data.get("categories", {}).get(cid, {}).get("subcategories", []) or []
        self._subcat_ids = [''] + [s.get("id", "") for s in subs]
        disp = ['无（默认）'] + [s.get("name", {}).get("zh", s.get("id", "")) for s in subs]
        self._subcat_disp = disp
        if getattr(self, "subcat_combo", None) is not None:
            self.subcat_combo["values"] = disp
            if self.subcat_var.get() not in disp:
                self.subcat_var.set("无（默认）")

    # ==================== 商品列表 ====================
    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        self._thumb_cache.clear()
        cat = self.current_cat.get()
        prods = self.data.get("products", {}).get(cat, [])
        for i, p in enumerate(prods):
            price = p.get('price', '') or '询价'
            zh_name = p.get('nameZh', '') or p.get('name', '')
            # 生成缩略图（50x50），兼容空列表
            imgs = p.get('images', [])
            first_img = imgs[0] if imgs else p.get('img', '')
            thumb = self._make_thumb(first_img, size=(40, 40))
            self.tree.insert('', 'end', iid=str(i),
                             image=thumb,
                             values=(zh_name, price))
        self._reset_form()
        self._update_stats()

    def _make_thumb(self, img_path, size=(90, 90)):
        """生成缩略图 PhotoImage"""
        if not img_path:
            return ''
        full = BASE_DIR / img_path
        if not full.exists():
            return ''
        try:
            img = Image.open(full)
            img.thumbnail(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._thumb_cache[img_path] = photo
            return photo
        except Exception:
            return ''

    def _update_stats(self):
        total = self.dm.total_products()
        wid = self.data.get('wechat_id', 'GDFK17888')
        has_api = "✅" if self.translator.api_key else "⚠️ 未配置"
        self.stats_label.config(text=f"| 微信: {wid} | 商品: {total} 件 | 翻译API: {has_api}")

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        cat = self.current_cat.get()
        prods = self.data.get("products", {}).get(cat, [])
        if idx < len(prods):
            self.selected_idx = idx
            self._load_form(prods[idx])

    def _load_form(self, p):
        for k in ['name', 'nameZh', 'nameMs', 'nameVi']:
            self.name_vars[k].set(p.get(k, ''))
        self._price_for_display(p.get('price', ''))
        # 分类下拉显示中文名
        cat_id = p.get('cat', self.current_cat.get())
        cat_zh = self._cat_id_to_name.get(cat_id, cat_id)
        self.edit_cat_var.set(cat_zh)

        # 子分类回填
        self._refresh_subcat_combo()
        p_sub = p.get('subcat', '')
        if p_sub and p_sub in self._subcat_ids:
            self.subcat_var.set(self._subcat_disp[self._subcat_ids.index(p_sub)])
        else:
            self.subcat_var.set('无（默认）')

        # 加载描述（兼容旧格式 string → 新格式 dict）
        desc = p.get('desc', '')
        if isinstance(desc, str):
            desc = {'zh': desc, 'en': '', 'ms': '', 'vi': ''}
        for lang in ('zh', 'en', 'ms', 'vi'):
            w = self.desc_texts[lang]
            w.delete('1.0', 'end')
            w.insert('1.0', desc.get(lang, ''))

        # 加载图片列表到内部变量
        self._images = list(p.get('images', []))
        if not self._images and p.get('img'):
            self._images = [p['img']]
        self._refresh_image_list()

    def _reset_form(self):
        self.selected_idx = None
        self._images = []
        for v in self.name_vars.values():
            v.set('')
        self._price_for_display('')
        for w in self.desc_texts.values():
            w.delete('1.0', 'end')
        self.img_listbox.delete(0, 'end')

    # ==================== CRUD ====================
    def _collect_product_data(self):
        """从表单收集商品数据"""
        cover = self._images[0] if self._images else ""
        desc_dict = {}
        for lang in ('zh', 'en', 'ms', 'vi'):
            txt = self.desc_texts[lang].get('1.0', 'end-1c').strip()
            desc_dict[lang] = txt

        return {
            "img": cover,
            "images": list(self._images),
            "name": self.name_vars['name'].get(),
            "nameZh": self.name_vars['nameZh'].get(),
            "nameMs": self.name_vars['nameMs'].get(),
            "nameVi": self.name_vars['nameVi'].get(),
            "price": self._price_for_storage(),
            "desc": desc_dict,
            "cat": self._cat_name_to_id.get(self.edit_cat_var.get(), self.current_cat.get()),
            "subcat": self._subcat_ids[self._subcat_disp.index(self.subcat_var.get())]
                      if self.subcat_var.get() in self._subcat_disp else ""
        }

    def _add_product(self):
        """新建空白商品"""
        cat = self.current_cat.get()
        if cat not in self.data.get("products", {}):
            messagebox.showerror("错误", "分类 '{}' 不存在，请先创建分类".format(cat))
            return
        nid = self.dm.get_next_id(cat)
        # 创建空白模板，不使用表单中的旧数据
        np = {
            "id": nid,
            "img": "",
            "images": [],
            "emoji": "📦",
            "name": "New Product",
            "nameZh": "新品",
            "nameMs": "Produk Baru",
            "nameVi": "Sản Phẩm Mới",
            "price": "",
            "desc": {"zh": "", "en": "", "ms": "", "vi": ""},
            "cat": cat,
            "subcat": ""
        }
        self.data["products"][cat].append(np)
        self.dm.save()
        self.refresh_list()
        children = self.tree.get_children()
        if children:
            last = children[-1]
            self.tree.selection_set(last)
            self.tree.focus(last)
            self._on_select(None)
        self.status_text.set(f"✅ 已添加: {np['name']} ({nid}) | 图片: {len(np['images'])} 张")

    def _save_product(self):
        if self.selected_idx is None:
            messagebox.showinfo("提示", "请先在左侧列表中选择一个商品")
            return
        cat = self.current_cat.get()
        prods = self.data.get("products", {}).get(cat, [])
        idx = self.selected_idx
        if idx >= len(prods):
            return

        p = prods[idx]
        new_data = self._collect_product_data()
        for k, v in new_data.items():
            p[k] = v

        # 如果改了分类
        new_cat = new_data["cat"]
        if new_cat != cat and new_cat in self.data.get("products", {}):
            prods.pop(idx)
            self.data["products"][new_cat].append(p)

        self.dm.save()
        self.refresh_list()
        self.status_text.set(f"✅ 已保存: {p['name']} | 图片: {len(p.get('images', []))} 张")

    def _delete_product(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在左侧商品列表中选择要删除的商品")
            return
        idx = int(sel[0])
        cat = self.current_cat.get()
        prods = self.data.get("products", {}).get(cat, [])
        if idx >= len(prods):
            return
        p = prods[idx]
        name_to_show = p.get('nameZh', '') or p.get('name', '')
        if not messagebox.askyesno("确认删除", "确定删除「{}」吗？\n此操作不可撤销。".format(name_to_show)):
            return
        prods.pop(idx)
        self.dm.save()
        self.refresh_list()
        self.status_text.set("🗑 已删除: {}".format(name_to_show))
        self.status_text.set(f"🗑 已删除: {p['name']}")

    def _move(self, direction):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        cat = self.current_cat.get()
        prods = self.data.get("products", {}).get(cat, [])
        ni = idx + direction
        if 0 <= ni < len(prods):
            prods[idx], prods[ni] = prods[ni], prods[idx]
            self.dm.save()
            self.refresh_list()
            self.tree.selection_set(str(ni))
            self.tree.focus(str(ni))

    # ==================== 分类 ====================
    def _category_dialog(self, cid=None):
        """新建或编辑分类。cid=None 新建；cid 给定则编辑现有分类（保留 filename 与已有商品）。"""
        edit_mode = cid is not None and cid in self.data.get("categories", {})
        if edit_mode:
            cat = self.data["categories"][cid]
            cur_names = cat.get("name", {})
            cur_hero = cat.get("hero", "") or ""
            cur_subs = [dict(s) for s in (cat.get("subcategories", []) or [])]
            new_cid = cid
        else:
            cat = None
            cur_names = {}
            cur_hero = ""
            cur_subs = []
            new_cid = None
        id_var = tk.StringVar()

        dlg = tk.Toplevel(self.root)
        dlg.title("编辑分类" if edit_mode else "新建分类")
        dlg.geometry("460x620")
        dlg.transient(self.root); dlg.grab_set()

        # ---- 分类 ID ----
        if edit_mode:
            ttk.Label(dlg, text=f"分类 ID：{cid}（不可修改）", font=('Microsoft YaHei', 10, 'bold')).pack(anchor='w', padx=15, pady=(10, 2))
        else:
            ttk.Label(dlg, text="分类 ID（英文简写，如 clothing/shoes）：", font=('Microsoft YaHei', 10)).pack(anchor='w', padx=15, pady=(10, 2))
            ttk.Entry(dlg, textvariable=id_var, width=30).pack(padx=15)

        # ---- 四语名称 ----
        nvars = {}
        for lbl, key in [("中文名:", "zh"), ("英文名:", "en"), ("马来文:", "ms"), ("越南文:", "vi")]:
            ttk.Label(dlg, text=lbl, font=('Microsoft YaHei', 10)).pack(anchor='w', padx=15, pady=(8, 2))
            v = tk.StringVar(value=cur_names.get(key, "")); nvars[key] = v
            ttk.Entry(dlg, textvariable=v, width=34).pack(padx=15)

        # ---- 主图 ----
        ttk.Label(dlg, text="🖼 分类页主图（图片路径，如 images/xxx.jpg，留空=纯色背景）：", font=('Microsoft YaHei', 10)).pack(anchor='w', padx=15, pady=(8, 2))
        hero_frame = ttk.Frame(dlg); hero_frame.pack(fill='x', padx=15)
        hero_var = tk.StringVar(value=cur_hero)
        ttk.Entry(hero_frame, textvariable=hero_var, width=28).pack(side='left', fill='x', expand=True)
        def _browse_hero():
            p = filedialog.askopenfilename(title="选择分类主图", filetypes=[("图片", "*.jpg *.jpeg *.png *.webp"), ("所有", "*.*")])
            if p:
                rel = Path(p)
                dst = IMAGES_DIR / rel.name
                if not dst.exists():
                    shutil.copy2(p, dst)
                hero_var.set("images/" + rel.name)
        ttk.Button(hero_frame, text="📁 浏览", command=_browse_hero).pack(side='left', padx=4)

        # ---- 子分类 ----
        ttk.Label(dlg, text="🏷 子分类（如 短袖/长袖/长裤/短裤，可选）：", font=('Microsoft YaHei', 10, 'bold')).pack(anchor='w', padx=15, pady=(10, 2))
        sub_form = ttk.Frame(dlg); sub_form.pack(fill='x', padx=15)
        sub_id_var = tk.StringVar()
        ttk.Label(sub_form, text="ID").grid(row=0, column=0, padx=(0, 2))
        ttk.Entry(sub_form, textvariable=sub_id_var, width=8).grid(row=0, column=1, padx=2)
        sub_nvars = {}
        c = 2
        for lbl, key in [("中", "zh"), ("英", "en"), ("马", "ms"), ("越", "vi")]:
            ttk.Label(sub_form, text=lbl).grid(row=0, column=c, padx=1); c += 1
            v = tk.StringVar(); sub_nvars[key] = v
            ttk.Entry(sub_form, textvariable=v, width=7).grid(row=0, column=c, padx=1); c += 1

        dlg.subs = list(cur_subs)
        subs_listbox = tk.Listbox(dlg, height=4, font=('Microsoft YaHei', 9), exportselection=False)
        subs_listbox.pack(fill='x', padx=15, pady=(4, 0))
        def _render_subs():
            subs_listbox.delete(0, 'end')
            for s in dlg.subs:
                nm = s.get('name', {}).get('zh', '') or s.get('id', '')
                subs_listbox.insert('end', f"{s.get('id', '')} : {nm}")
        _render_subs()
        def _add_sub():
            sid = sub_id_var.get().strip().lower().replace(' ', '_')
            if not sid:
                messagebox.showerror("错误", "请输入子分类 ID"); return
            if any(s.get('id') == sid for s in dlg.subs):
                messagebox.showerror("错误", f"子分类 ID「{sid}」已存在"); return
            zh = sub_nvars['zh'].get().strip() or sid
            dlg.subs.append({"id": sid, "name": {
                "en": sub_nvars['en'].get().strip() or zh,
                "zh": zh,
                "ms": sub_nvars['ms'].get().strip() or zh,
                "vi": sub_nvars['vi'].get().strip() or zh,
            }})
            sub_id_var.set('')
            for k in sub_nvars: sub_nvars[k].set('')
            _render_subs()
        def _del_sub():
            sel = subs_listbox.curselection()
            if not sel: return
            dlg.subs.pop(sel[0]); _render_subs()
        sub_btn_frame = ttk.Frame(dlg)
        sub_btn_frame.pack(anchor='w', padx=15, pady=(2, 0))
        ttk.Button(sub_btn_frame, text="➕ 添加子分类", command=_add_sub).pack(side='left', padx=(0, 4))
        sub_trans_btn = ttk.Button(sub_btn_frame, text="🌐 翻译子分类", command=lambda: _translate_sub())
        sub_trans_btn.pack(side='left', padx=4)
        sub_all_btn = ttk.Button(sub_btn_frame, text="🌐全部翻译", command=lambda: _translate_all_subs())
        sub_all_btn.pack(side='left', padx=4)
        ttk.Button(dlg, text="🗑 删除选中子分类", command=_del_sub).pack(anchor='w', padx=15, pady=(2, 4))

        sub_tip = tk.StringVar()
        ttk.Label(dlg, textvariable=sub_tip, font=('Microsoft YaHei', 9), foreground='#1a7f37').pack(anchor='w', padx=15)

        def _translate_sub():
            zh = sub_nvars['zh'].get().strip()
            if not zh:
                sub_tip.set("⚠️ 请先在「中」栏填写子分类中文名再翻译"); return
            sub_trans_btn.config(state='disabled', text="🌐 翻译中...")
            sub_tip.set("🌐 正在翻译（中→英/马来/越）...")
            def run():
                result, error = self.translator.translate(zh, ['en', 'ms', 'vi'])
                self.root.after(0, lambda: _apply_sub_translation(result, error))
            threading.Thread(target=run, daemon=True).start()
        def _apply_sub_translation(result, error):
            sub_trans_btn.config(state='normal', text="🌐 翻译子分类")
            if error:
                sub_tip.set("❌ " + error); return
            if result.get('en'): sub_nvars['en'].set(result['en'])
            if result.get('ms'): sub_nvars['ms'].set(result['ms'])
            if result.get('vi'): sub_nvars['vi'].set(result['vi'])
            sub_tip.set("✅ 已翻译填充，可点「添加子分类」")
        def _translate_all_subs():
            if not dlg.subs:
                sub_tip.set("⚠️ 还没有已添加的子分类"); return
            sub_all_btn.config(state='disabled', text="🌐 翻译中...")
            sub_tip.set("🌐 正在翻译全部已添加子分类...")
            def run():
                updated = []
                for s in dlg.subs:
                    zh = s.get('name', {}).get('zh', '') or s.get('id', '')
                    result, error = self.translator.translate(zh, ['en', 'ms', 'vi'])
                    nm = dict(s.get('name', {}))
                    if not error and result:
                        nm['en'] = result.get('en') or nm.get('en') or zh
                        nm['ms'] = result.get('ms') or nm.get('ms') or zh
                        nm['vi'] = result.get('vi') or nm.get('vi') or zh
                    else:
                        nm.setdefault('en', zh); nm.setdefault('ms', zh); nm.setdefault('vi', zh)
                    updated.append({"id": s.get('id'), "name": nm})
                self.root.after(0, lambda: _apply_all_subs(updated))
            threading.Thread(target=run, daemon=True).start()
        def _apply_all_subs(updated):
            dlg.subs = updated
            _render_subs()
            sub_all_btn.config(state='normal', text="🌐全部翻译")
            sub_tip.set(f"✅ 已翻译 {len(updated)} 个子分类")

        # ---- 一键翻译 ----
        tip = tk.StringVar()
        def _translate_cat():
            zh = nvars['zh'].get().strip()
            if not zh:
                tip.set("⚠️ 请先在「中文名」填写名称再翻译"); return
            btn.config(state='disabled', text="🌐 翻译中...")
            tip.set("🌐 正在翻译（中→英/马来/越）...")
            def run():
                result, error = self.translator.translate(zh, ['en', 'ms', 'vi'])
                self.root.after(0, lambda: _apply_cat_translation(result, error))
            threading.Thread(target=run, daemon=True).start()
        def _apply_cat_translation(result, error):
            btn.config(state='normal', text="🌐 一键翻译（中→英/马来/越）")
            if error:
                tip.set("❌ " + error); return
            if result.get('en'): nvars['en'].set(result['en'])
            if result.get('ms'): nvars['ms'].set(result['ms'])
            if result.get('vi'): nvars['vi'].set(result['vi'])
            tip.set("✅ 已翻译填充，请核对后点「确认」")
        btn = ttk.Button(dlg, text="🌐 一键翻译（中→英/马来/越）", command=_translate_cat)
        btn.pack(pady=(4, 0))
        ttk.Label(dlg, textvariable=tip, font=('Microsoft YaHei', 9), foreground='#555').pack(padx=15, pady=(2, 0))

        # ---- 确认 ----
        def _confirm():
            if not edit_mode:
                nc = id_var.get().strip().lower()
                if not nc:
                    messagebox.showerror("错误", "请输入分类 ID"); return
                if nc in self.data.get("categories", {}):
                    messagebox.showerror("错误", "该分类已存在"); return
                new_cid = nc
            en = nvars['en'].get() or (cid if edit_mode else new_cid)
            name = {"en": en, "zh": nvars['zh'].get() or en,
                    "ms": nvars['ms'].get() or en, "vi": nvars['vi'].get() or en}
            hero = hero_var.get().strip()
            subs = [dict(s) for s in dlg.subs]
            try:
                if edit_mode:
                    cat["name"] = name
                    cat["hero"] = hero
                    cat["subcategories"] = subs
                    target_cid = cid
                else:
                    target_cid = new_cid
                    self.data["categories"][new_cid] = {
                        "id": new_cid, "name": name,
                        "description": {"en": "", "zh": "", "ms": "", "vi": ""},
                        "hero": hero, "subcategories": subs, "filename": f"{new_cid}.html"}
                    self.data["products"][new_cid] = []
                self.dm.save()
                self.gen.generate_category_page(self.data, target_cid)
                self.gen.update_nav_all(self.data)
                self.gen.generate_index(self.data)
                self.gen.generate_product_detail(self.data)
            except Exception as e:
                self.status_text.set(f"⚠️ 分类已保存，但生成页面失败: {e}")
                messagebox.showerror("生成失败", str(e))
                return
            self._refresh_cats()
            if not edit_mode:
                self.current_cat.set(target_cid)
            self.refresh_list()
            dlg.destroy()
            self.status_text.set(f"✅ 已保存分类「{target_cid}」（子分类 {len(subs)} 个），请点「部署」上线")

        ttk.Button(dlg, text="✅ 确认保存", command=_confirm).pack(pady=12)

    # ==================== 保存 ====================
    def _save(self):
        self.dm.save()
        self.status_text.set("💾 数据已保存")

    # ==================== HTML 生成 ====================
    def _do_regenerate(self):
        try:
            self.gen.regenerate_all(self.data)
            return True, "5 个 HTML 文件已重新生成"
        except Exception as e:
            return False, str(e)

    def _import_from_website(self):
        """从 HTML 文件中导入商品数据回 products.json"""
        if not messagebox.askyesno("导入确认",
            "将从以下文件导入商品数据:\n\n"
            "  index.html (全部商品)\n"
            "  clothing.html, shoes.html, bags.html\n"
            "  product-detail.html\n\n"
            "已存在的商品 ID 会跳过，不会重复导入。\n确认继续?"):
            return

        imported = 0
        skipped = 0
        for hfile in HTML_FILES:
            fpath = BASE_DIR / hfile
            if not fpath.exists():
                continue
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    text = f.read()
                if self.gen.START not in text or self.gen.END not in text:
                    continue
                # 提取标记之间的 JS 代码
                js_code = text.split(self.gen.START)[1].split(self.gen.END)[0]

                # 解析 JS 对象/数组 → Python
                products = self._parse_js_products(js_code)
                for p in products:
                    pid = p.get('id', '')
                    cat = p.get('cat', '')
                    if not cat or not pid:
                        continue
                    if cat not in self.data.get('products', {}):
                        self.data['products'][cat] = []
                    # 检查是否重复
                    existing_ids = [ep['id'] for ep in self.data['products'][cat]]
                    if pid in existing_ids:
                        skipped += 1
                        continue
                    # 适配字段
                    desc = p.get('desc', '')
                    if isinstance(desc, str):
                        desc = {'zh': desc, 'en': '', 'ms': '', 'vi': ''}
                    p['desc'] = desc
                    if 'images' not in p:
                        p['images'] = [p.get('img', '')] if p.get('img') else []
                    self.data['products'][cat].append(p)
                    imported += 1
            except Exception as e:
                self.status_text.set("导入 {} 失败: {}".format(hfile, e))
                continue

        self.dm.save()
        self.refresh_list()
        self.status_text.set("📥 导入完成: {} 个新品, 跳过 {} 个重复".format(imported, skipped))
        messagebox.showinfo("导入完成",
            "导入 {} 个新品\n跳过 {} 个重复（ID 已存在）".format(imported, skipped))

    def _parse_js_products(self, js_code):
        """解析 HTML 中的 JS 产品数据 → Python list of dicts"""
        results = []
        # 去掉 const products = 等前缀
        js_code = re.sub(r'^(const|var|let)\s+\w+\s*=\s*', '', js_code.strip())
        js_code = js_code.rstrip(';').strip()

        # 收集所有对象 {...}
        depth = 0; start = None
        for i, ch in enumerate(js_code):
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start is not None:
                    obj_str = js_code[start:i+1]
                    try:
                        obj = self._js_obj_to_dict(obj_str)
                        results.append(obj)
                    except:
                        pass
                    start = None
        return results

    @staticmethod
    def _js_obj_to_dict(js_obj):
        """将 JS 对象字符串转为 Python dict（处理无引号 key）"""
        # 给 key 加引号:  id: → "id":
        fixed = re.sub(r"([{,])\s*(\w+)\s*:", r'\1"\2":', js_obj)
        # 单引号字符串 → 双引号（简单情况）
        fixed = re.sub(r"'([^']*)'", r'"\1"', fixed)
        # 移除尾部逗号
        fixed = re.sub(r',\s*}', '}', fixed)
        fixed = re.sub(r',\s*]', ']', fixed)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return {}

    def _threaded_regenerate(self):
        def run():
            self.status_text.set("🔄 正在生成 HTML...")
            ok, msg = self._do_regenerate()
            if ok:
                self.root.after(0, lambda: self.status_text.set(f"✅ {msg}"))
                self.root.after(0, lambda: messagebox.showinfo("完成", msg))
            else:
                self.root.after(0, lambda: self.status_text.set(f"❌ {msg}"))
                self.root.after(0, lambda: messagebox.showerror("失败", msg))
        threading.Thread(target=run, daemon=True).start()

    # ==================== 部署 ====================
    def _test_github(self):
        self.status_text.set("🔍 测试 GitHub 连接 (SSH)...")
        def run():
            ok = self.git.test_connection()
            if ok:
                self.root.after(0, lambda: self.status_text.set("✅ GitHub 连接成功 (SSH)"))
                self.root.after(0, lambda: messagebox.showinfo("成功", "GitHub SSH 连接成功!"))
            else:
                self.root.after(0, lambda: self.status_text.set("❌ 连接失败"))
                self.root.after(0, lambda: messagebox.showerror("失败",
                    "无法连接 GitHub\n\nSSH 端口 22 可能被封锁，\n请尝试配置 HTTPS Token 后重试。"))
        threading.Thread(target=run, daemon=True).start()

    def _do_deploy(self):
        ok, msg = self._do_regenerate()
        if not ok:
            return False, msg
        ts = time.strftime("%Y-%m-%d %H:%M")
        token = self.github_token.get().strip()
        return self.git.commit_and_push(f"更新商品 ({ts})", token)

    def _threaded_deploy(self):
        if not messagebox.askyesno("确认部署",
            "即将执行:\n\n"
            "  1. 重新生成全部 5 个 HTML 文件\n"
            "  2. Git commit + push 到 GitHub\n"
            "  3. Cloudflare Pages 自动部署\n\n"
            "确认继续?"):
            return
        self.status_text.set("🚀 部署中...")
        def run():
            ok, msg = self._do_deploy()
            if ok:
                self.root.after(0, lambda: self.status_text.set("🎉 部署成功!"))
                self.root.after(0, lambda: messagebox.showinfo("成功",
                    "网站已更新! 🎉\n\n"
                    "Cloudflare Pages 1-2 分钟自动上线。\n"
                    "访问 www.bajustyle.com 查看。"))
            else:
                self.root.after(0, lambda: self.status_text.set(f"❌ {msg}"))
                self.root.after(0, lambda: messagebox.showerror("失败", msg))
        threading.Thread(target=run, daemon=True).start()


def main():
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except:
        pass
    default_font = ('Microsoft YaHei', 9)
    root.option_add('*Font', default_font)
    style.configure('.', font=default_font)
    style.configure('TLabelframe', bordercolor='#d0d0d0')
    style.configure('TLabelframe.Label', font=('Microsoft YaHei', 10, 'bold'), foreground='#555')

    App(root)

    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")
    root.mainloop()


if __name__ == '__main__':
    main()
