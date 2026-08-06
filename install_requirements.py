# AI模型切换器 - 安装和使用说明

## 📦 依赖安装

在运行程序前，需要安装依赖库：

```bash
pip install requests
pip install pyinstaller
```

或者一次性安装所有依赖：

```bash
pip install requests pyinstaller
```

## 🚀 运行程序

### 方法1：直接运行Python文件

```bash
cd D:\BajuStyle
python model_switcher.py
```

### 方法2：打包成EXE文件

```bash
# 安装依赖
pip install requests pyinstaller

# 打包成EXE
pyinstaller --onefile --windowed --name "AI模型切换器" model_switcher.py
```

打包后，EXE文件会在 `dist` 文件夹中。

## 📖 使用说明

### 1. 配置API Key

#### 智谱AI (BigModel)
1. 访问：https://open.bigmodel.cn/
2. 注册并获取API Key
3. 在程序中输入API Key和API URL
4. 选择模型（glm-4、glm-4-plus、glm-4-air、glm-4-flash）

#### DeepSeek
1. 访问：https://platform.deepseek.com/
2. 注册并获取API Key
3. 在程序中输入API Key和API URL
4. 选择模型（deepseek-chat、deepseek-reasoner）

### 2. 选择模型

在程序右侧的"选择要测试的模型"下拉框中选择：
- 智谱AI - glm-4
- DeepSeek - deepseek-chat
- DeepSeek - deepseek-reasoner

### 3. 测试连接

点击"🚀 测试连接"按钮，测试API是否能正常连接。

### 4. 发送请求

1. 在左侧输入测试内容
2. 点击"🚀 发送请求"按钮
3. 查看右侧的响应结果

### 5. 保存配置

点击"💾 保存配置"按钮，将API Key和设置保存到 config.json 文件中，下次启动时会自动加载。

## 🎨 功能特点

✅ **可视化界面** - 友好的图形用户界面
✅ **支持两种模型** - 智谱AI和DeepSeek
✅ **API Key管理** - 安全保存和加载API Key
✅ **模型切换** - 轻松切换不同模型
✅ **实时测试** - 测试连接和发送请求
✅ **多模型选择** - 每个模型提供多个选项
✅ **配置保存** - 自动保存配置到本地文件

## ⚠️ 注意事项

1. **API Key安全** - 不要将API Key分享给他人
2. **费用说明** - 使用AI API会产生费用，请注意查看账单
3. **网络要求** - 需要稳定的网络连接
4. **API额度** - 确保您的API有足够的额度

## 🔧 配置文件说明

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

## 📞 常见问题

### Q1: 程序打不开？
A: 确保已安装Python和必要的依赖库。

### Q2: 提示API Key错误？
A: 检查API Key是否正确输入，确保没有多余的空格。

### Q3: 提示网络错误？
A: 检查网络连接，确保可以访问AI API服务。

### Q4: 配置保存失败？
A: 确保程序有写入文件的权限。

### Q5: 如何更换模型？
A: 在程序中重新选择模型，然后点击"切换模型"按钮。

## 🎉 开始使用

1. 安装依赖：`pip install requests pyinstaller`
2. 运行程序：`python model_switcher.py`
3. 输入API Key并配置
4. 开始测试和切换模型！

## 📞 支持

如有问题，请检查：
- Python版本是否正确
- 依赖库是否已安装
- API Key是否有效
- 网络连接是否正常

祝您使用愉快！🚀
