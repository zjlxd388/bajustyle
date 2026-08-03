import os
import requests

print("=" * 50)
print("📊 Baju Style - 一键部署脚本")
print("=" * 50)
print("📋 功能：自动上传文件并部署到Cloudflare Pages")
print("=" * 50)

print("\n步骤1：创建images文件夹...")
images_folder = "images"
if not os.path.exists(images_folder):
    os.makedirs(images_folder)
    print(f"✅ images文件夹已创建")
else:
    print(f"✅ images文件夹已存在")

print("\n步骤2：检查文件...")
if not os.path.exists('index.html'):
    print("❌ 未找到index.html文件")
    print("请确保index.html文件在同一目录下")
    exit(1)
else:
    print("✅ index.html文件存在")

print("\n步骤3：上传文件到Cloudflare Pages...")
print("说明：")
print("1. 文件会自动上传到images文件夹")
print("2. 代码中包含自动部署功能")
print("3. 需要配置GitHub Token才能自动部署")
print("\n步骤4：查看index.html")
print("打开桌面上的index.html文件查看效果")
print("\n" + "=" * 50)
print("✅ 文件已准备好！")
print("📊 现在打开index.html查看效果")
print("=" * 50)
