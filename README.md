# 🎨 Baju Style 网站搭建指南

## 📋 文件说明

### 桌面上的文件：

1. **index.html** - 主页（多语言）
2. **deploy.py** - 部署脚本
3. **README.md** - 本说明文件
4. **images/** - 图片文件夹

---

## 🚀 快速开始

### 第1步：打开主页

1. 打开文件资源管理器
2. 找到桌面
3. 双击 **index.html**
4. 网站会在浏览器中打开

---

### 第2步：查看效果

在浏览器中，您可以：

✅ 查看首页
✅ 点击右上角语言按钮切换语言：
   - 中文
   - English
   - Bahasa Melayu（马来语）
   - Tiếng Việt（越南语）

✅ 查看产品展示
✅ 查看联系方式
✅ 查看响应式设计（在手机上查看效果）

---

### 第3步：自定义内容

**修改文字内容：**

1. 右键点击 **index.html**
2. 选择"打开方式" → "记事本"或"VS Code"
3. 找到对应的文字
4. 修改文字
5. 保存文件
6. 刷新浏览器

**示例：**

找到这一行：
```html
<p id="hero-title">Welcome to Baju Style</p>
```

修改为：
```html
<p id="hero-title">欢迎来到Baju Style</p>
```

---

### 第4步：更换图片

**方法1：使用您的图片**

1. 把图片放到 `images` 文件夹
2. 重命名为 `product1.jpg`, `product2.jpg`, `product3.jpg`, `product4.jpg`
3. 打开 `index.html`
4. 修改图片路径：

```html
<img src="images/product1.jpg" alt="Fashion Item 1">
```

**方法2：使用示例图片**

代码中已经包含自动加载示例图片，使用的是Unsplash：

```html
<img src="images/product1.jpg" alt="Fashion Item 1" onerror="this.src='https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=400&h=400&fit=crop'">
```

如果找不到本地图片，会自动加载示例图片。

---

### 第5步：部署到Cloudflare Pages

#### 步骤1：创建GitHub仓库

1. 访问：https://github.com/new
2. Repository name：`bajustyle`
3. 选择"Public"或"Private"
4. 勾选"Add a README file"
5. 点击"Create repository"

#### 步骤2：上传文件到GitHub

**上传 index.html：**

1. 点击"uploading an existing file"
2. 选择桌面上的 `index.html` 文件
3. 点击"Commit changes"

**上传 images 文件夹：**

1. 点击"uploading an existing file"
2. 选择桌面上的 `images` 文件夹
3. 点击"Commit changes"

#### 步骤3：连接Cloudflare Pages

1. 访问：https://pages.cloudflare.com/
2. 点击"Create a project"
3. 选择"Connect to Git"
4. 选择GitHub账户
5. 选择仓库：`user/bajustyle`（替换为您的用户名）
6. 点击"Continue"

#### 步骤4：配置域名

1. 点击"Add custom domain"
2. 输入您的域名：例如 `bajustyle.com`
3. 点击"Add domain"
4. 复制Cloudflare给的IP地址
5. 去域名注册商（如Dynadot）配置DNS：
   - Host: `@`
   - Type: `A`
   - Value: `[Cloudflare给的IP]`
6. 点击"Save Changes"
7. 等待30-60分钟DNS生效

#### 步骤5：自动部署

Cloudflare Pages会自动检测到GitHub更新，自动开始部署：

1. 等待1-2分钟
2. 访问：https://bajustyle.com
3. 网站部署完成！

---

## 📱 多语言功能

### 当前支持的语言

✅ 中文（zh-CN）
✅ 英文（en-US）
✅ 马来语（ms-MY）
✅ 越南语（vi-VN）

### 如何添加新语言

**在HTML代码中添加语言按钮：**

```html
<button onclick="switchLanguage('es-ES')" data-lang="es-ES">Español</button>
```

**在JavaScript中添加内容：**

```javascript
const content = {
    'zh-CN': { ... },
    'en-US': { ... },
    'es-ES': {
        tagline: 'Moda y Estilo en Singapura y Malasia',
        heroTitle: 'Bienvenido a Baju Style',
        heroDescription: 'Tu tienda de moda número uno en Malasia y Singapura',
        exploreBtn: 'Explorar Nuestra Colección',
        aboutTitle: 'Sobre Nosotros',
        aboutDescription: 'Ofrecemos las últimas tendencias de moda y estilos. Nuestra tienda online ofrece una amplia variedad de ropa, zapatos y accesorios.',
        productsTitle: 'Colecciones Recientes',
        productsSubtitle: 'Nuestros Artículos Populares',
        'product-1-title': 'Vestido Moderno',
        'product-1-price': 'RM 150 - SGD 35',
        'product-2-title': 'Camiseta Casual',
        'product-2-price': 'RM 50 - SGD 12',
        'product-3-title': 'Blusa Elegante',
        'product-3-price': 'RM 120 - SGD 28',
        'product-4-title': 'Jeans Estiloso',
        'product-4-price': 'RM 180 - SGD 42',
        contactTitle: 'Contáctanos',
        addressText: '123 Calle de Moda, Singapura 123456, Malasia',
        emailText: 'hello@bajustyle.com',
        phoneText: '+60 12 345 6789 (Malasia)',
        wechatText: 'WeChat: bajustyle (ID: bajustyle)',
        footerText: 'Moda Malasia Singapura'
    },
    // ... 更多语言
};
```

---

## 🎨 自定义样式

### 修改颜色

在 `<style>` 标签中找到颜色代码：

```css
/* 颜色 */
header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

修改颜色：

- `#667eea` → 您想要的颜色
- `#764ba2` → 您想要的颜色

### 修改字体

找到字体设置：

```css
body {
    font-family: 'Arial', sans-serif;
}
```

修改为：

```css
body {
    font-family: 'Microsoft YaHei', 'Arial', sans-serif;
}
```

---

## 📱 响应式设计

网站已经包含响应式设计，在以下设备上查看效果：

✅ 桌面电脑
✅ 笔记本电脑
✅ 平板电脑（iPad）
✅ 智能手机（iPhone、Android）

### 在手机上查看

**方法1：手机直接打开**

1. 把 `index.html` 复制到手机
2. 用手机浏览器打开

**方法2：浏览器响应式模式**

1. 在电脑上打开
2. 按F12，点击"响应式模式"
3. 查看移动端效果

---

## 📞 联系方式

### 微信引流

在页面底部添加微信：

```html
<div class="contact-item">
    <svg viewBox="0 0 24 24">
        <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 01.213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 00.167-.054l1.903-1.114a.864.864 0 01.717-.098 10.16 10.16 0 001.937.187c.276 0 .543-.027.811-.05-.857-2.578.157-5.457 2.303-7.224 1.064-.875 2.36-1.345 3.668-1.345 1.098 0 2.156.323 3.07.923a.629.629 0 00.533.098l1.815-.344a.528.528 0 01.678.355.629.629 0 01-.188.784l-1.517 1.242a9.058 9.058 0 01-3.033 1.517 10.966 10.966 0 01-2.922.334c-.313 0-.617-.027-.923-.054.578-2.297.296-4.727-.782-6.868-1.445-2.547-4.023-4.148-6.937-4.148-1.148 0-2.276.277-3.345.823a.635.635 0 01-.732.054zM6.643 19.516a.63.63 0 01-.49.234.636.636 0 01-.634-.635V15.57c0-.35.28-.634.634-.634.351 0 .635.28.635.634v3.718c0 .28-.28.49-.49.634z"/>
    </svg>
    <span>微信：bajustyle</span>
</div>
```

---

## ❓ 常见问题

### Q1: 打开index.html后看不到图片？

**A:** 检查 `images` 文件夹是否存在，确保图片文件名正确（product1.jpg, product2.jpg等）。

### Q2: 如何修改颜色？

**A:** 在 `index.html` 的 `<style>` 标签中找到颜色代码并修改。

### Q3: 如何添加更多产品？

**A:** 在 `index.html` 中的 `<div class="products-grid">` 部分添加更多 `<div class="product-card">` 块。

### Q4: 如何部署到互联网？

**A:** 按照上面的"第5步：部署到Cloudflare Pages"说明操作。

### Q5: 多语言切换不工作？

**A:** 检查JavaScript代码是否完整，确保包含所有语言内容。

### Q6: 微信引流按钮不显示？

**A:** 确保SVG图标代码完整，检查微信ID是否正确。

---

## 📞 需要帮助？

如果遇到问题：

1. 检查文件是否在同一目录
2. 用记事本或VS Code打开文件
3. 查看是否有错误提示
4. 检查文件是否完整

---

## ✅ 完成检查清单

- [ ] 打开index.html查看效果
- [ ] 测试多语言切换
- [ ] 测试响应式设计
- [ ] 修改部分内容测试
- [ ] 备份原始文件
- [ ] 准备图片文件
- [ ] 创建GitHub仓库
- [ ] 上传文件到GitHub
- [ ] 连接Cloudflare Pages
- [ ] 配置自定义域名
- [ ] 等待DNS生效
- [ ] 测试线上网站

---

## 📊 总结

✅ **index.html** - 主页（多语言）
✅ **images/** - 图片存储
✅ **deploy.py** - 部署脚本
✅ **完全免费**
✅ **一键部署**

---

## 🎉 祝您搭建顺利！

如有问题，请检查：
1. 文件是否在同一目录
2. 文件格式是否正确
3. 浏览器控制台是否有错误

**祝您搭建顺利！** 🚀
