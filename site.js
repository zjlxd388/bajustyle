/* ============================================================
   BajuStyle — 动态引擎 site.js
   职责：
   1. 运行时多语言翻译（data-key 静态文本 + data-cat/data-subcat 动态分类名）
   2. 分类页主图横幅渲染（categoryMeta）
   3. 子分类筛选（renderSubcatFilter / renderCategoryGrid）
   4. 首页新品/热销渲染（renderHome，动态，不写死索引）
   5. 微信弹窗 / 二维码缩放 / 复制 / 移动菜单 等共享能力
   自动 wrap 页面自带 switchLanguage，兼容首页/分类页/详情页。
   ============================================================ */
(function () {
    'use strict';

    var SUPPORTED = ['en', 'zh', 'ms', 'vi'];

    // ---- 共享翻译字典（供 data-key 静态文本）----
    var CONTENT = {
        en: {
            navHome: 'Home', navClothing: 'Clothing', navShoes: 'Shoes', navBags: 'Bags',
            heroSubtitle: 'DY Premium Fashion — Ships Worldwide',
            heroBtn: 'Explore Collection',
            shopByCat: 'Shop by', catClothing: 'Clothing', catClothingDesc: 'Dresses, Tops & Bottoms',
            catShoes: 'Shoes', catShoesDesc: 'Heels, Flats & Sandals',
            catBags: 'Bags', catBagsDesc: 'Handbags & Accessories',
            newArrivals: 'New', bestSellers: 'Best',
            allProducts: 'All Products',
            contactPrice: 'Contact for Price', viewDetails: 'View Details',
            filterAll: 'All', emptyHint: 'No products yet. Contact us on WeChat to see more styles.',
            footerBrand: 'DY · Premium Fashion',
            footerDesc: 'DY (高端服饰) — Premium women\'s fashion boutique. Trendy clothing, shoes, and bags shipped worldwide from China to Malaysia, Singapore, Vietnam & beyond.',
            footerShop: 'Shop', footerHelp: 'Help', footerFAQ: 'FAQ', footerSize: 'Size Guide',
            footerShipping: 'Shipping Info', footerContact: 'Contact Us',
            footerContactTitle: 'Contact via WeChat',
            footerQrAdd: 'Add WeChat', footerQrCatalog: 'More Styles',
            footerWechatBtn: 'Chat Now',
            wechatBtn: 'WeChat', langHint: '🌐 Switch Language / 切换语言',
            topBar: 'Free Delivery across Malaysia & Singapore — Shipped Worldwide from China 🌍',
            youMayLike: 'You May Also Like',
            inquireWechat: 'Inquire on WeChat', detailDescDefault: 'High-quality fashion piece designed for the modern woman.',
            modalBrand: 'DY Premium Fashion', modalTitle: 'High-End Fashion',
            modalSub: 'Add WeChat to browse full catalog & place orders',
            modalQr1Label: 'Add WeChat', modalQr1Hint: 'Scan to add me',
            modalQr2Label: 'More Styles', modalQr2Hint: 'Scan to view catalog',
            modalCopy: 'Copy', modalFoot: 'Worldwide Shipping · Ships from China 🌍'
        },
        zh: {
            navHome: '首页', navClothing: '衣服', navShoes: '鞋子', navBags: '包包',
            heroSubtitle: 'DY 高端服饰 — 全球发货',
            heroBtn: '探索系列',
            shopByCat: '按分类', catClothing: '衣服', catClothingDesc: '连衣裙、上衣、裤子',
            catShoes: '鞋子', catShoesDesc: '高跟鞋、平底鞋、凉鞋',
            catBags: '包包', catBagsDesc: '手提包及配饰',
            newArrivals: '新品', bestSellers: '畅销',
            allProducts: '全部商品',
            contactPrice: '微信询价', viewDetails: '查看详情',
            filterAll: '全部', emptyHint: '暂无商品，微信联系我们查看更多款式。',
            footerBrand: 'DY · 高端服饰',
            footerDesc: 'DY（高端服饰）— 优质女装精品店。从中国发货至马来西亚、新加坡、越南及全球，主营时尚服装、鞋子和包包。',
            footerShop: '购物', footerHelp: '帮助', footerFAQ: '常见问题', footerSize: '尺码指南',
            footerShipping: '配送信息', footerContact: '联系我们',
            footerContactTitle: '微信联系',
            footerQrAdd: '加微信', footerQrCatalog: '款式更全',
            footerWechatBtn: '立即聊天',
            wechatBtn: '微信', langHint: '🌐 切换语言 / Switch Language',
            topBar: '马来西亚 & 新加坡全境包邮 — 中国直邮全球 🌍',
            youMayLike: '猜你喜欢',
            inquireWechat: '微信咨询', detailDescDefault: '为现代女性设计的高品质时尚单品。',
            modalBrand: 'DY 高端服饰', modalTitle: '高端服饰（可发全球）',
            modalSub: '添加微信，浏览全部款式并下单',
            modalQr1Label: '添加微信', modalQr1Hint: '扫一扫加我',
            modalQr2Label: '款式更齐全', modalQr2Hint: '扫一扫看相册',
            modalCopy: '复制', modalFoot: '全球发货 · 中国直邮 🌍'
        },
        ms: {
            navHome: 'Utama', navClothing: 'Pakaian', navShoes: 'Kasut', navBags: 'Beg',
            heroSubtitle: 'DY Fesyen Premium — Dihantar ke Seluruh Dunia',
            heroBtn: 'Terokai Koleksi',
            shopByCat: 'Beli Mengikut', catClothing: 'Pakaian', catClothingDesc: 'Gaun, Atasan & Bawahan',
            catShoes: 'Kasut', catShoesDesc: 'Tumit, Flat & Sandal',
            catBags: 'Beg', catBagsDesc: 'Beg Tangan & Aksesori',
            newArrivals: 'Baru', bestSellers: 'Terlaris',
            allProducts: 'Semua Produk',
            contactPrice: 'Hubungi untuk Harga', viewDetails: 'Lihat Butiran',
            filterAll: 'Semua', emptyHint: 'Tiada produk buat masa ini. Hubungi kami di WeChat untuk lebih banyak gaya.',
            footerBrand: 'DY · Fesyen Premium',
            footerDesc: 'DY (Fesyen Premium) — Butik fesyen wanita premium. Pakaian, kasut dan beg trendy dihantar dari China ke Malaysia, Singapura, Vietnam & seluruh dunia.',
            footerShop: 'Beli', footerHelp: 'Bantuan', footerFAQ: 'Soalan Lazim', footerSize: 'Panduan Saiz',
            footerShipping: 'Maklumat Penghantaran', footerContact: 'Hubungi Kami',
            footerContactTitle: 'Hubungi via WeChat',
            footerQrAdd: 'Tambah WeChat', footerQrCatalog: 'Lebih Gaya',
            footerWechatBtn: 'Sembang Sekarang',
            wechatBtn: 'WeChat', langHint: '🌐 Tukar Bahasa / Switch Language',
            topBar: 'Penghantaran Percuma ke seluruh Malaysia & Singapura — Dihantar ke seluruh dunia dari China 🌍',
            youMayLike: 'Anda Mungkin Suka',
            inquireWechat: 'Tanya di WeChat', detailDescDefault: 'Pakaian berkualiti tinggi untuk wanita moden.',
            modalBrand: 'DY Fesyen Premium', modalTitle: 'Fesyen Premium',
            modalSub: 'Tambah WeChat untuk lihat katalog penuh & buat pesanan',
            modalQr1Label: 'Tambah WeChat', modalQr1Hint: 'Imbas untuk tambah saya',
            modalQr2Label: 'Lebih Gaya', modalQr2Hint: 'Imbas untuk lihat katalog',
            modalCopy: 'Salin', modalFoot: 'Dihantar ke Seluruh Dunia · Dari China 🌍'
        },
        vi: {
            navHome: 'Trang Chủ', navClothing: 'Quần Áo', navShoes: 'Giày', navBags: 'Túi Xách',
            heroSubtitle: 'DY Thời Trang Cao Cấp — Giao Hàng Toàn Cầu',
            heroBtn: 'Khám Phá Bộ Sưu Tập',
            shopByCat: 'Mua Theo', catClothing: 'Quần Áo', catClothingDesc: 'Đầm, Áo & Quần',
            catShoes: 'Giày', catShoesDesc: 'Cao Gót, Búp Bê & Dép',
            catBags: 'Túi Xách', catBagsDesc: 'Túi Xách & Phụ Kiện',
            newArrivals: 'Mới', bestSellers: 'Bán Chạy',
            allProducts: 'Tất Cả Sản Phẩm',
            contactPrice: 'Liên Hệ Để Biết Giá', viewDetails: 'Xem Chi Tiết',
            filterAll: 'Tất cả', emptyHint: 'Chưa có sản phẩm. Liên hệ WeChat để xem thêm mẫu.',
            footerBrand: 'DY · Thời Trang Cao Cấp',
            footerDesc: 'DY (Thời trang cao cấp) — Boutique thời trang nữ cao cấp. Quần áo, giày dép và túi xách thời trang giao từ Trung Quốc đến Malaysia, Singapore, Việt Nam & toàn cầu.',
            footerShop: 'Mua Sắm', footerHelp: 'Trợ Giúp', footerFAQ: 'Câu Hỏi Thường Gặp', footerSize: 'Hướng Dẫn Size',
            footerShipping: 'Thông Tin Giao Hàng', footerContact: 'Liên Hệ',
            footerContactTitle: 'Liên Hệ qua WeChat',
            footerQrAdd: 'Thêm WeChat', footerQrCatalog: 'Thêm Mẫu',
            footerWechatBtn: 'Chat Ngay',
            wechatBtn: 'WeChat', langHint: '🌐 Chuyển Ngôn Ngữ / Switch Language',
            topBar: 'Giao Hàng Miễn Phí toàn Malaysia & Singapore — Giao hàng toàn cầu từ Trung Quốc 🌍',
            youMayLike: 'Có Thể Bạn Thích',
            inquireWechat: 'Hỏi qua WeChat', detailDescDefault: 'Sản phẩm thời trang chất lượng cao dành cho phụ nữ hiện đại.',
            modalBrand: 'DY Thời Trang Cao Cấp', modalTitle: 'Thời Trang Cao Cấp',
            modalSub: 'Thêm WeChat để xem toàn bộ catalog & đặt hàng',
            modalQr1Label: 'Thêm WeChat', modalQr1Hint: 'Quét để thêm tôi',
            modalQr2Label: 'Thêm Mẫu', modalQr2Hint: 'Quét để xem catalog',
            modalCopy: 'Sao chép', modalFoot: 'Giao Hàng Toàn Cầu · Từ Trung Quốc 🌍'
        }
    };

    function pick(obj, lang) {
        if (!obj) return '';
        return obj[lang] || obj.en || '';
    }
    function nameOf(p, lang) {
        var o = { en: p.name, zh: p.nameZh, ms: p.nameMs, vi: p.nameVi };
        return pick(o, lang) || p.name || '';
    }

    var BajuSite = {
        content: CONTENT,
        selectedSub: '',
        WECHAT_ID: (typeof WECHAT_ID !== 'undefined') ? WECHAT_ID : 'GDFK17888',

        init: function () {
            var self = this;
            var lang = this.currentLang();

            // 兼容页面自带 switchLanguage（详情页）：wrap 后追加动态渲染
            if (window.switchLanguage && !window.__bajuWrapped) {
                var orig = window.switchLanguage;
                window.switchLanguage = function (l) { orig(l); self.afterSwitch(l); };
                window.__bajuWrapped = true;
            }

            // 语言按钮
            document.querySelectorAll('.lang-btn').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    if (window.switchLanguage) window.switchLanguage(btn.dataset.lang);
                    else self.switchTo(btn.dataset.lang);
                });
            });
            // 移动菜单链接点击后关闭
            document.querySelectorAll('.mobile-menu a').forEach(function (link) {
                link.addEventListener('click', function () { self.closeMobileMenu(); });
            });

            if (window.switchLanguage) window.switchLanguage(lang);
            else this.switchTo(lang);
        },

        currentLang: function () {
            var p = new URLSearchParams(window.location.search);
            var l = p.get('lang') || localStorage.getItem('preferred-language') || 'en';
            return SUPPORTED.indexOf(l) >= 0 ? l : 'en';
        },

        // 无页面 switchLanguage 时（首页/分类页）自行完成全部切换
        switchTo: function (lang) {
            this.translateStatic(lang);
            var url = new URL(window.location.href);
            url.searchParams.set('lang', lang);
            window.history.replaceState({}, '', url);
            this.setActiveLangBtn(lang);
            try { localStorage.setItem('preferred-language', lang); } catch (e) {}
            this.afterSwitch(lang);
        },

        setActiveLangBtn: function (lang) {
            document.querySelectorAll('.lang-btn').forEach(function (b) {
                b.classList.toggle('active', b.dataset.lang === lang);
            });
        },

        translateStatic: function (lang) {
            var t = CONTENT[lang] || CONTENT.en;
            document.querySelectorAll('[data-key]').forEach(function (el) {
                if (t[el.dataset.key]) el.textContent = t[el.dataset.key];
            });
        },

        // 动态分类名翻译（导航 data-cat / 子分类 data-subcat）
        translateDynamic: function (lang) {
            var sc = (typeof siteCategories !== 'undefined') ? siteCategories : null;
            if (!sc) return;
            document.querySelectorAll('[data-cat]').forEach(function (el) {
                var c = sc[el.dataset.cat];
                if (c && c.name) el.textContent = pick(c.name, lang);
            });
            document.querySelectorAll('[data-subcat]').forEach(function (el) {
                var parts = (el.dataset.subcat || '').split(':');
                var c = sc[parts[0]];
                if (!c) return;
                var s = (c.subcategories || []).filter(function (x) { return x.id === parts[1]; })[0];
                if (s) el.textContent = pick(s.name, lang);
            });
        },

        afterSwitch: function (lang) {
            this.translateDynamic(lang);
            if (typeof products !== 'undefined' && Array.isArray(products)) {
                // 分类页
                this.renderBanner(lang);
                this.renderSubcatFilter(lang);
                this.renderCategoryGrid(lang, this.selectedSub);
            } else if (typeof products !== 'undefined') {
                // 首页：products 为对象
                this.renderHome(lang);
            }
        },

        renderBanner: function (lang) {
            if (typeof categoryMeta === 'undefined') return;
            var m = categoryMeta;
            var banner = document.getElementById('pageBanner');
            if (banner) {
                if (m.hero) {
                    banner.style.setProperty('--banner-img', "url('" + m.hero + "')");
                    banner.classList.add('has-hero');
                } else {
                    banner.style.removeProperty('--banner-img');
                    banner.classList.remove('has-hero');
                }
            }
            var t = document.getElementById('pageTitleText');
            if (t) t.textContent = pick(m.name, lang);
            var s = document.getElementById('pageSubtitleText');
            if (s) s.textContent = pick(m.description, lang);
        },

        renderSubcatFilter: function (lang) {
            if (typeof categoryMeta === 'undefined') return;
            var subs = (categoryMeta.subcategories || []);
            var bar = document.getElementById('subcatFilter');
            if (!bar) return;
            var self = this;
            if (!subs.length) { bar.innerHTML = ''; this.selectedSub = ''; return; }
            var html = '<button class="subcat-btn active" data-sub="">' + (CONTENT[lang] || CONTENT.en).filterAll + '</button>';
            html += subs.map(function (s) {
                return '<button class="subcat-btn" data-sub="' + s.id + '">' + pick(s.name, lang) + '</button>';
            }).join('');
            bar.innerHTML = html;
            bar.querySelectorAll('.subcat-btn').forEach(function (b) {
                b.addEventListener('click', function () {
                    self.selectedSub = b.dataset.sub;
                    bar.querySelectorAll('.subcat-btn').forEach(function (x) { x.classList.remove('active'); });
                    b.classList.add('active');
                    self.renderCategoryGrid(lang, self.selectedSub);
                });
            });
        },

        renderCategoryGrid: function (lang, sub) {
            var grid = document.getElementById('productGrid');
            if (!grid || typeof products === 'undefined') return;
            var list = products;
            if (sub) list = products.filter(function (p) { return (p.subcat || '') === sub; });
            var self = this;
            var t = CONTENT[lang] || CONTENT.en;
            grid.innerHTML = list.length
                ? list.map(function (p) { return self.cardHtml(p, lang); }).join('')
                : '<p class="empty-hint">' + t.emptyHint + '</p>';
        },

        renderHome: function (lang) {
            if (typeof products === 'undefined') return;
            var flat = [];
            Object.keys(products).forEach(function (k) {
                (products[k] || []).forEach(function (p) { flat.push(p); });
            });
            var self = this;
            var ng = document.getElementById('newArrivalsGrid');
            var bg = document.getElementById('bestSellersGrid');
            if (ng) ng.innerHTML = flat.slice(0, 8).map(function (p) { return self.cardHtml(p, lang); }).join('');
            if (bg) bg.innerHTML = flat.slice(8, 16).map(function (p) { return self.cardHtml(p, lang); }).join('');
        },

        cardHtml: function (p, lang) {
            var name = nameOf(p, lang);
            var t = CONTENT[lang] || CONTENT.en;
            var price = p.price
                ? '<div class="product-card-price">' + p.price + '</div>'
                : '<div class="product-card-price">' + t.contactPrice + '</div>';
            var media = p.img
                ? '<span class="fallback-emoji">' + (p.emoji || '') + '</span><img src="' + p.img + '" alt="' + name + '" loading="lazy" onerror="this.remove()">'
                : '<span class="fallback-emoji">' + (p.emoji || '') + '</span>';
            return '<div class="product-card" onclick="location.href=\'product-detail.html?id=' + p.id + '\'">' +
                '<div class="product-card-img">' + media + '</div>' +
                '<div class="product-card-info">' +
                '<div class="product-card-name">' + name + '</div>' +
                price +
                '<span class="view-btn">' + t.viewDetails + '</span>' +
                '</div></div>';
        },

        /* ===== 微信弹窗 / 二维码 / 复制 / 移动菜单（共享）===== */
        openWechatModal: function () {
            var m = document.getElementById('wechatModal');
            if (m) m.classList.add('show');
            document.body.style.overflow = 'hidden';
        },
        closeWechatModal: function () {
            if (window.resetQrZoom) window.resetQrZoom();
            var m = document.getElementById('wechatModal');
            if (m) m.classList.remove('show');
            document.body.style.overflow = '';
        },
        copyWechatId: function (el) {
            var id = (el && el.dataset && el.dataset.id) || this.WECHAT_ID;
            var self = this;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(id).then(function () { self.showCopySuccess(el); })
                    .catch(function () { self.fallbackCopy(id, el); });
            } else { self.fallbackCopy(id, el); }
        },
        fallbackCopy: function (text, el) {
            var ta = document.createElement('textarea');
            ta.value = text; ta.style.position = 'fixed'; ta.style.left = '-9999px';
            document.body.appendChild(ta); ta.select();
            try { document.execCommand('copy'); this.showCopySuccess(el); } catch (e) {}
            document.body.removeChild(ta);
        },
        showCopySuccess: function (el) {
            if (!el) return;
            var orig = el.textContent;
            el.textContent = 'Copied ✓';
            el.style.color = 'var(--wechat)';
            setTimeout(function () { el.textContent = orig; el.style.color = ''; }, 1500);
        },
        toggleQrZoom: function (img) {
            if (!img) return;
            if (img.classList.contains('zoomed')) img.classList.remove('zoomed');
            else {
                document.querySelectorAll('.wechat-modal-qr-img.zoomed').forEach(function (e) { e.classList.remove('zoomed'); });
                img.classList.add('zoomed');
            }
        },
        resetQrZoom: function () {
            document.querySelectorAll('.wechat-modal-qr-img.zoomed').forEach(function (e) { e.classList.remove('zoomed'); });
        },
        toggleMobileMenu: function () {
            var m = document.getElementById('mobileMenu');
            if (m) m.classList.toggle('open');
        },
        closeMobileMenu: function () {
            var m = document.getElementById('mobileMenu');
            if (m) m.classList.remove('open');
        }
    };

    // 暴露全局，供 HTML onclick="openWechatModal()" 等内联调用
    window.BajuSite = BajuSite;
    window.openWechatModal = BajuSite.openWechatModal;
    window.closeWechatModal = BajuSite.closeWechatModal;
    window.copyWechatId = BajuSite.copyWechatId;
    window.toggleQrZoom = BajuSite.toggleQrZoom;
    window.resetQrZoom = BajuSite.resetQrZoom;
    window.toggleMobileMenu = BajuSite.toggleMobileMenu;

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            if (document.querySelector('.wechat-modal-qr-img.zoomed')) BajuSite.resetQrZoom();
            else BajuSite.closeWechatModal();
        }
    });

    if (document.readyState !== 'loading') BajuSite.init();
    else document.addEventListener('DOMContentLoaded', function () { BajuSite.init(); });
})();
