import os
import shutil

print("=" * 70)
print("📁 移动文件到 D 盘")
print("=" * 70)

# 源目录（桌面）
source_dir = os.path.expanduser("~/Desktop")

# 目标目录（D 盘）
dest_dir = r"D:\BajuStyle"

# 需要移动的文件列表
files_to_move = [
    "index.html",
    "deploy.py",
    "github_upload.py",
    "cloudflare_deploy.py",
    "README.md",
    "DEPLOY_GUIDE.md",
    "QUICK_START.md",
    "DEPLOY_CHECKLIST.md",
    "images_guide.txt"
]

# 文件夹列表
folders_to_move = [
    "images"
]

print(f"\n源目录: {source_dir}")
print(f"目标目录: {dest_dir}")
print("\n准备移动的文件:")
for f in files_to_move:
    print(f"  - {f}")

print("\n准备移动的文件夹:")
for f in folders_to_move:
    print(f"  - {f}")

# 创建目标目录
print(f"\n✅ 创建目标目录: {dest_dir}")
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# 移动文件
print("\n📤 移动文件...")
success_count = 0
for file_name in files_to_move:
    src_path = os.path.join(source_dir, file_name)
    dest_path = os.path.join(dest_dir, file_name)

    if os.path.exists(src_path):
        try:
            shutil.move(src_path, dest_path)
            print(f"  ✅ {file_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {file_name} - 失败: {e}")
    else:
        print(f"  ⚠️  {file_name} - 不存在")

# 移动文件夹
print("\n📤 移动文件夹...")
folder_success_count = 0
for folder_name in folders_to_move:
    src_path = os.path.join(source_dir, folder_name)
    dest_path = os.path.join(dest_dir, folder_name)

    if os.path.exists(src_path):
        try:
            shutil.move(src_path, dest_path)
            print(f"  ✅ {folder_name}/")
            folder_success_count += 1
        except Exception as e:
            print(f"  ❌ {folder_name}/ - 失败: {e}")
    else:
        print(f"  ⚠️  {folder_name}/ - 不存在")

# 完成
print("\n" + "=" * 70)
print(f"🎉 移动完成！")
print("=" * 70)
print(f"✅ 成功移动文件: {success_count}/{len(files_to_move)}")
print(f"✅ 成功移动文件夹: {folder_success_count}/{len(folders_to_move)}")
print(f"\n📁 文件夹位置: {dest_dir}")
print(f"\n📋 下一步：")
print(f"   cd {dest_dir}")
print(f"   python github_upload.py")
print(f"   python cloudflare_deploy.py")
print("=" * 70)
