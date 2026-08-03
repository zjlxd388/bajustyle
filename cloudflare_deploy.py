import os
import requests

print("=" * 70)
print("☁️  Cloudflare Pages 自动部署脚本")
print("=" * 70)

# Cloudflare Pages 部署信息
CLOUDFLARE_API_TOKEN = input("请输入您的 Cloudflare API Token: ").strip()
ACCOUNT_ID = input("请输入您的 Cloudflare Account ID: ").strip()
PROJECT_NAME = "bajustyle"  # Cloudflare 项目名称
GITHUB_REPO = input("请输入 GitHub 仓库 (格式: username/repo): ").strip()

print("\n" + "=" * 70)
print("📋 配置信息:")
print("=" * 70)
print(f"Account ID: {ACCOUNT_ID}")
print(f"项目名称: {PROJECT_NAME}")
print(f"GitHub 仓库: {GITHUB_REPO}")
print("=" * 70)

# API 端点
BASE_URL = "https://api.cloudflare.com/client/v4"
PROJECT_URL = f"{BASE_URL}/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}"

# 请求头
headers = {
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json"
}

# 步骤1：检查项目是否已存在
print("\n🔍 检查 Cloudflare Pages 项目...")
try:
    response = requests.get(PROJECT_URL, headers=headers)

    if response.status_code == 200:
        project_info = response.json()
        print(f"✅ 项目已存在！")
        print(f"   项目名称: {project_info['result']['name']}")
        print(f"   状态: {project_info['result']['deployment_status']}")
    else:
        print(f"⚠️  项目不存在，正在创建...")
        print(f"   项目名称: {PROJECT_NAME}")
        print(f"   GitHub 仓库: {GITHUB_REPO}")
except Exception as e:
    print(f"❌ 检查项目失败: {e}")
    exit(1)

# 如果项目不存在，创建项目
if response.status_code != 200:
    try:
        create_url = f"{BASE_URL}/accounts/{ACCOUNT_ID}/pages/projects"
        project_data = {
            "name": PROJECT_NAME,
            "source": {
                "type": "github",
                "config": {
                    "owner": GITHUB_REPO.split('/')[0],
                    "repo_name": GITHUB_REPO.split('/')[1],
                    "production_branch": "main",
                    "pr_comments_enabled": True
                }
            },
            "build_config": {
                "root_directory": "/",
                "framework": null
            }
        }

        response = requests.post(create_url, headers=headers, json=project_data)

        if response.status_code == 200 or response.status_code == 201:
            print(f"✅ Cloudflare Pages 项目创建成功！")
            project_info = response.json()['result']
        else:
            print(f"❌ 创建项目失败！")
            print(f"   错误代码: {response.status_code}")
            print(f"   错误信息: {response.json()}")
            exit(1)

    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        exit(1)

# 步骤2：获取构建配置
print("\n🚀 获取部署信息...")
try:
    build_info_url = f"{BASE_URL}/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/builds"
    response = requests.get(build_info_url, headers=headers)

    if response.status_code == 200:
        builds = response.json()['result']
        if builds:
            print(f"✅ 项目已配置部署！")
            print(f"   构建配置: {builds[0]['build_config']}")
        else:
            print(f"⚠️  项目未配置部署，需要手动配置...")
    else:
        print(f"⚠️  获取部署信息失败，可能需要手动配置")
except Exception as e:
    print(f"⚠️  获取部署信息失败: {e}")

# 步骤3：验证项目
print("\n🔍 验证项目配置...")
try:
    response = requests.get(PROJECT_URL, headers=headers)
    if response.status_code == 200:
        project_info = response.json()['result']
        print(f"✅ 项目验证成功！")
        print(f"   网站地址: {project_info['url']}")
        print(f"   生产分支: {project_info['production_branch']}")
    else:
        print(f"❌ 项目验证失败")
except Exception as e:
    print(f"❌ 验证失败: {e}")

# 完成
print("\n" + "=" * 70)
print("🎉 Cloudflare Pages 配置完成！")
print("=" * 70)
print(f"\n✅ GitHub 仓库: https://github.com/{GITHUB_REPO}")
print(f"✅ 项目名称: {PROJECT_NAME}")
print(f"✅ 部署状态: 自动部署")
print(f"\n📋 下一步：")
print(f"   1. 访问 Cloudflare Pages Dashboard: https://dash.cloudflare.com/")
print(f"   2. 查看 {PROJECT_NAME} 项目的部署状态")
print(f"   3. 等待 1-2 分钟完成自动部署")
print(f"   4. 访问网站地址查看效果")
print(f"\n📱 Cloudflare 会自动检测 GitHub 更新并部署！")
print("=" * 70)
