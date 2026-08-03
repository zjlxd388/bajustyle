# ⚡ 快速开始指南

## 🎯 最快部署方式（30分钟完成）

---

## 📁 桌面文件清单

```
C:\Users\Administrator\Desktop

├── 📄 index.html                    # 网站主页
├── 📄 github_upload.py              # GitHub 上传脚本 ⭐
├── 📄 cloudflare_deploy.py          # Cloudflare 配置脚本 ⭐
├── 📄 README.md                     # 使用说明
├── 📄 DEPLOY_GUIDE.md               # 完整部署指南
├── 📄 images_guide.txt              # 图片准备指南
├── 📁 images/                       # 图片文件夹（需要添加图片）
```

---

## 🚀 三步部署

### 第1步：准备图片（10分钟）⚠️ 可选

**如果暂时没有产品图片：**
- 不需要图片也能部署
- 网站会自动加载 Unsplash 示例图片

**如果有产品图片：**
1. 把图片放入 `images/` 文件夹
2. 重命名为 `product1.jpg`, `product2.jpg`, `product3.jpg`, `product4.jpg`

---

### 第2步：上传到 GitHub（10分钟）⭐ 使用脚本

**1. 获取 GitHub Token**
```
https://github.com/settings/tokens
→ 点击 "Generate new token (classic)"
→ 勾选所有权限
→ 复制 Token
```

**2. 运行上传脚本**
```bash
cd C:\Users\Administrator\Desktop
python github_upload.py
```

**3. 输入信息**
```
GitHub Token: (粘贴您的 Token)
GitHub 用户名: (您的 GitHub 用户名)
```

**4. 等待完成**
- 脚本会自动创建仓库
- 自动上传所有文件

---

### 第3步：配置 Cloudflare Pages（10分钟）⭐ 使用脚本

**1. 获取 Cloudflare Token**
```
https://dash.cloudflare.com/profile/api-tokens
→ 点击 "Create Token"
→ 选择 "Create Custom Token"
→ 勾选 "Cloudflare Pages: Edit"
→ 复制 Token
```

**2. 获取 Account ID**
```
https://dash.cloudflare.com/
→ 查看 Account ID（顶部）
→ 复制 Account ID
```

**3. 运行配置脚本**
```bash
cd C:\Users\Administrator\Desktop
python cloudflare_deploy.py
```

**4. 输入信息**
```
Cloudflare API Token: (粘贴您的 Token)
Account ID: (粘贴您的 Account ID)
GitHub 仓库: (用户名/bajustyle)
```

**5. 等待完成**
- 脚本会自动创建项目
- 自动连接 GitHub

---

## ✅ 部署完成

### 访问网站

**Cloudflare 提供的地址：**
```
https://bajustyle.pages.dev
```

**或您的自定义域名：**
```
https://bajustyle.com
```

---

## 🧪 测试网站

打开浏览器，访问网站，测试：

- ✅ 多语言切换（点击右上角按钮）
- ✅ 产品展示（4个产品卡片）
- ✅ 响应式设计（F12 → 响应式模式）
- ✅ 微信引流信息显示

---

## 📊 如果遇到问题

### 问题1：脚本运行失败

**检查：**
1. 是否安装了 Python
2. 是否安装了 requests 库：`pip install requests`
3. 网络是否正常

### 问题2：Token 无效

**解决：**
1. 重新生成 Token
2. 确保勾选了所有权限
3. Token 已复制正确

### 问题3：网站无法访问

**解决：**
1. 等待 2-3 分钟（DNS 传播需要时间）
2. 检查 Cloudflare Pages 项目状态
3. 查看部署日志

---

## 📞 需要帮助？

### 查看详细文档

- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** - 完整部署指南
- **[README.md](README.md)** - 使用说明
- **[images_guide.txt](images_guide.txt)** - 图片准备指南

### 常见问题

查看 **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** 的故障排除部分

---

## 🎉 完成！

**30分钟内完成部署！**

### 重要提醒

1. ⚠️ 定期备份代码到 GitHub
2. ⚠️ 更新产品图片时重新上传
3. ⚠️ 监控网站访问量

---

**祝您部署顺利！** 🚀
