# 🤖 AI模型切换器

支持智谱AI和DeepSeek两个大模型的可视化切换工具。

## ✨ 功能特点

- 🎨 **可视化GUI界面** - 友好的图形用户界面
- 🔑 **API Key管理** - 安全保存和加载API Key
- 🔄 **模型切换** - 轻松切换不同AI模型
- 🚀 **实时测试** - 测试连接和发送请求
- 💾 **配置保存** - 自动保存配置到本地文件
- 🌐 **多模型支持** - 智谱AI和DeepSeek

## 📋 支持的模型

### 智谱AI (BigModel)
- `glm-4` - 主力模型
- `glm-4-plus` - 增强版
- `glm-4-air` - 轻量版
- `glm-4-flash` - 快速响应版

### DeepSeek
- `deepseek-chat` - 对话模型
- `deepseek-reasoner` - 推理模型

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests pyinstaller
```

### 2. 运行程序

```bash
python model_switcher.py
```

### 3. 配置API Key

#### 智谱AI配置
1. 访问 https://open.bigmodel.cn/
2. 注册并获取API Key
3. 在程序中输入API Key和API URL
4. 选择模型

#### DeepSeek配置
1. 访问 https://platform.deepseek.com/
2. 注册并获取API Key
3. 在程序中输入API Key和API URL
4. 选择模型

### 4. 开始使用

1. 在"选择要测试的模型"下拉框中选择模型
2. 输入测试内容
3. 点击"🚀 发送请求"
4. 查看响应结果

## 📦 打包成EXE

### 方法1：使用打包脚本（推荐）

```bash
python build_exe.py
```

### 方法2：手动打包

```bash
pyinstaller --onefile --windowed --name "AI模型切换器" model_switcher.py
```

打包完成后，EXE文件位于 `dist` 文件夹中。

## 🎯 使用流程

```
启动程序
    ↓
选择模型（智谱AI或DeepSeek）
    ↓
输入测试内容
    ↓
发送请求
    ↓
查看响应结果
    ↓
保存配置（可选）
```

## 📖 界面说明

### 左侧：API配置区域
- 智谱AI API Key和URL输入
- DeepSeek API Key和URL输入
- 模型选择下拉框
- 切换模型按钮
- 保存配置按钮

### 右侧：对话/测试区域
- 模型选择下拉框
- 测试连接按钮
- 对话输入框
- 发送请求按钮
- 响应结果显示区
- 清空按钮

## ⚠️ 注意事项

1. **API Key安全** - 不要将API Key分享给他人
2. **费用说明** - 使用AI API会产生费用，请注意查看账单
3. **网络要求** - 需要稳定的网络连接
4. **API额度** - 确保您的API有足够的额度
5. **文件权限** - 首次运行可能需要管理员权限来创建配置文件

## 🔧 配置文件

程序会自动生成 `config.json` 文件，格式如下：

```json
{
    "zhipu": {
        "api_key": "您的智谱AI API Key",
        "api_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "model": "glm-4"
    },
    "deepseek": {
        "api_key": "您的DeepSeek API Key",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "model": "deepseek-chat"
    }
}
```

## ❓ 常见问题

### Q: 程序打不开？
A: 检查Python版本是否为3.6+，是否已安装requests和pyinstaller。

### Q: 提示API Key错误？
A: 检查API Key是否正确，确保没有多余的空格。

### Q: 提示网络错误？
A: 检查网络连接，确保可以访问AI API服务。

### Q: 如何更换模型？
A: 在程序中重新选择模型，点击"切换模型"按钮。

### Q: 配置保存失败？
A: 确保程序有写入文件的权限，检查config.json文件是否存在。

## 📊 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Linux
- **Python**: 3.6 或更高版本
- **内存**: 至少 512MB 可用内存
- **网络**: 稳定的互联网连接

## 🎉 开始使用

1. 安装依赖: `pip install requests pyinstaller`
2. 运行程序: `python model_switcher.py`
3. 配置API Key
4. 开始测试和切换模型！

## 📞 技术支持

如有问题，请检查：
- Python版本和依赖库是否正确
- API Key是否有效
- 网络连接是否正常

祝您使用愉快！🚀

---

**版本**: 1.0.0
**更新日期**: 2026-08-07
**作者**: Claude Code
