import os
import requests
import json
from pathlib import Path

print("=" * 70)
print("🚀 GitHub 自动上传脚本 - Baju Style")
print("=" * 70)

# GitHub 配置
GITHUB_TOKEN = input("请输入您的 GitHub Token (PAT): ").strip()
GITHUB_USERNAME = input("请输入您的 GitHub 用户名: ").strip()
REPO_NAME = "bajustyle"
REPO_DESC = "Baju Style - Fashion Singapore Malaysia"

print("\n" + "=" * 70)
print("📋 配置信息:")
print("=" * 70)
print(f"GitHub 用户名: {GITHUB_USERNAME}")
print(f"仓库名称: {REPO_NAME}")
print(f"仓库描述: {REPO_DESC}")
print("=" * 70)

# API 端点
BASE_URL = "https://api.github.com"
REPO_URL = f"{BASE_URL}/repos/{GITHUB_USERNAME}/{REPO_NAME}"

# 请求头
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 检查 GitHub Token 是否有效
print("\n🔍 检查 GitHub Token...")
try:
    response = requests.get("https://api.github.com/user", headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"✅ Token 有效！用户: {user_info['login']}")
    else:
        print(f"❌ Token 无效！错误代码: {response.status_code}")
        print(f"   错误信息: {response.json().get('message', 'Unknown error')}")
        exit(1)
except Exception as e:
    print(f"❌ 连接 GitHub 失败: {e}")
    exit(1)

# 检查仓库是否存在
print(f"\n🔍 检查仓库 {REPO_NAME} 是否存在...")
try:
    response = requests.get(REPO_URL, headers=headers)
    if response.status_code == 200:
        repo_info = response.json()
        print(f"✅ 仓库已存在！")
        print(f"   仓库描述: {repo_info.get('description', 'N/A')}")
    else:
        print(f"⚠️  仓库不存在，正在创建...")
        print(f"   仓库名: {REPO_NAME}")
        print(f"   仓库描述: {REPO_DESC}")
except Exception as e:
    print(f"❌ 检查仓库失败: {e}")
    exit(1)

# 如果仓库不存在，创建仓库
if response.status_code != 200:
    try:
        create_repo_url = f"{BASE_URL}/user/repos"
        repo_data = {
            "name": REPO_NAME,
            "description": REPO_DESC,
            "auto_init": False,
            "private": False  # 设置为 False 公开仓库，True 私有仓库
        }
        response = requests.post(create_repo_url, headers=headers, json=repo_data)
        if response.status_code == 201:
            print(f"✅ 仓库创建成功！")
            repo_info = response.json()
        else:
            print(f"❌ 创建仓库失败！错误代码: {response.status_code}")
            print(f"   错误信息: {response.json().get('message', 'Unknown error')}")
            exit(1)
    except Exception as e:
        print(f"❌ 创建仓库失败: {e}")
        exit(1)

# 上传文件函数
def upload_file(file_path, repo_path, message, branch="main"):
    """上传单个文件到 GitHub"""
    print(f"\n📤 上传文件: {file_path}")

    # 读取文件内容
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        # 编码为 Base64
        base64_content = base64.b64encode(content).decode('utf-8')
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False

    # 检查文件是否已存在
    check_url = f"{REPO_URL}/contents/{repo_path}"
    try:
        check_response = requests.get(check_url, headers=headers)
        if check_response.status_code == 200:
            sha = check_response.json().get('sha')
            print(f"   文件已存在，更新中...")
        else:
            sha = None
            print(f"   文件不存在，创建新文件...")
    except Exception as e:
        print(f"⚠️  检查文件失败: {e}")
        sha = None

    # 创建或更新文件
    upload_url = f"{REPO_URL}/contents/{repo_path}"
    data = {
        "message": message,
        "content": base64_content,
        "branch": branch
    }

    if sha:
        data["sha"] = sha

    try:
        response = requests.put(upload_url, headers=headers, json=data)

        if response.status_code == 200 or response.status_code == 201:
            print(f"   ✅ 文件上传成功！")
            return True
        else:
            print(f"   ❌ 文件上传失败！")
            print(f"   错误代码: {response.status_code}")
            print(f"   错误信息: {response.json().get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ❌ 上传失败: {e}")
        return False

# 导入 base64
import base64

# 上传主文件
print("\n" + "=" * 70)
print("📤 开始上传文件...")
print("=" * 70)

# 上传 index.html
success = upload_file(
    file_path="index.html",
    repo_path="index.html",
    message="Add index.html - 主页模板",
    branch="main"
)

if success:
    print(f"\n✅ index.html 上传成功！")
else:
    print(f"\n❌ index.html 上传失败！")
    exit(1)

# 创建 README.md
readme_content = """# 🎨 Baju Style - Fashion Singapore Malaysia

## 📋 文件说明

- `index.html` - 主页（多语言）
- `images/` - 图片文件夹

## 🚀 快速开始

1. 在浏览器中打开 `index.html` 查看效果
2. 多语言切换：中文、英文、马来语、越南语
3. 响应式设计，支持手机和电脑

## 📱 多语言支持

- 中文（zh-CN）
- 英文（en-US）
- 马来语（ms-MY）
- 越南语（vi-VN）

## 📞 联系方式

微信：bajustyle
"""

upload_file(
    file_path="README.md",
    repo_path="README.md",
    message="Add README.md - 使用说明",
    branch="main"
)

# 上传 images 文件夹（包含多个文件）
images_folder = "images"
if os.path.exists(images_folder):
    print(f"\n📤 上传 images 文件夹...")
    image_files = ["product1.jpg", "product2.jpg", "product3.jpg", "product4.jpg"]

    for img_file in image_files:
        img_path = os.path.join(images_folder, img_file)
        if os.path.exists(img_path):
            upload_file(
                file_path=img_path,
                repo_path=f"images/{img_file}",
                message=f"Add image: {img_file}",
                branch="main"
            )
        else:
            print(f"   ⚠️  图片文件不存在: {img_file}")

# 完成信息
print("\n" + "=" * 70)
print("🎉 上传完成！")
print("=" * 70)
print(f"\n✅ GitHub 仓库: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
print(f"\n📋 下一步：")
print(f"   1. 访问 Cloudflare Pages: https://pages.cloudflare.com/")
print(f"   2. 创建项目并连接到 GitHub")
print(f"   3. 选择仓库: {GITHUB_USERNAME}/{REPO_NAME}")
print(f"   4. 点击 Deploy")
print(f"\n📱 网站将在 1-2 分钟后上线！")
print("=" * 70)
