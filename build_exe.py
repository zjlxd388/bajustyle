#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将模型切换器打包成EXE文件
"""

import os
import subprocess
import sys

def build_exe():
    """打包程序为EXE"""

    print("=" * 50)
    print("AI Model Switcher - Build Tool")
    print("=" * 50)

    # 检查是否安装了PyInstaller
    try:
        import PyInstaller
    except ImportError:
        print("\n[ERROR] PyInstaller not installed")
        print("Installing PyInstaller...\n")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 打包命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",              # 打包成单个EXE文件
        "--windowed",             # 无控制台窗口
        "--name", "AI Model Switcher",  # EXE文件名
        "--icon=None",            # 图标（可选）
        "--add-data", "config.json;.",  # 包含配置文件模板
        "--clean",                # 清理临时文件
        "model_switcher.py"
    ]

    print("[INFO] Starting build...\n")
    print("Command:", " ".join(cmd))
    print("\n[WAIT] Building, this may take 1-2 minutes...\n")

    # 执行打包命令
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("[SUCCESS] Build Successful!")
        print("=" * 50)
        print("\n[FILE] EXE Location: dist\\AI Model Switcher.exe")
        print("\n[USAGE]:")
        print("1. Copy dist\\AI Model Switcher.exe to any location")
        print("2. Double-click to run")
        print("\n[TIPS]:")
        print("- First run needs API Key configuration")
        print("- Configuration saves to config.json in the same directory")
        print("- Need internet connection to use AI models")
    else:
        print("\n" + "=" * 50)
        print("[ERROR] Build Failed")
        print("=" * 50)
        print("\nPlease check error message, ensure:")
        print("1. Python is properly installed")
        print("2. All dependencies are installed")
        print("3. model_switcher.py file exists")
        return False

    return True

if __name__ == "__main__":
    success = build_exe()
    input("\nPress any key to exit...")
