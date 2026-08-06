#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型切换器 - 支持智谱AI和DeepSeek
可视化 GUI 应用程序
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json

class ModelSwitcher:
    def __init__(self, root):
        self.root = root
        self.root.title("模型切换器 - AI模型切换工具")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        # 样式配置
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 配置颜色
        self.colors = {
            'bg': '#f5f5f5',
            'card_bg': '#ffffff',
            'primary': '#667eea',
            'primary_dark': '#764ba2',
            'text': '#333333',
            'text_light': '#666666',
            'border': '#e0e0e0',
            'wechat': '#07c160',
            'api_success': '#52c41a',
            'api_error': '#ff4d4f'
        }

        self.style.configure('Card.TFrame', background=self.colors['card_bg'])
        self.style.configure('Title.TLabel', font=('Microsoft YaHei', 18, 'bold'))
        self.style.configure('Label.TLabel', font=('Microsoft YaHei', 10))

        self.setup_ui()

    def setup_ui(self):
        """设置用户界面"""
        # 顶部标题
        title_frame = ttk.Frame(self.root, style='Card.TFrame')
        title_frame.pack(fill='x', padx=20, pady=20)

        ttk.Label(
            title_frame,
            text="🤖 AI模型切换器",
            style='Title.TLabel'
        ).pack()

        ttk.Label(
            title_frame,
            text="支持智谱AI和DeepSeek两个大模型切换",
            style='Label.TLabel'
        ).pack()

        # 主内容区域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # 左侧：API 配置区域
        config_frame = ttk.Frame(main_frame)
        config_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        self.setup_api_config(config_frame)

        # 右侧：聊天/测试区域
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(side='right', fill='both', expand=True)

        self.setup_chat_area(chat_frame)

    def setup_api_config(self, parent):
        """设置API配置区域"""
        # 标题
        ttk.Label(
            parent,
            text="🔑 API 配置",
            font=('Microsoft YaHei', 12, 'bold')
        ).pack(anchor='w', pady=(0, 15))

        # 智谱AI配置
        zhipu_frame = self.create_api_section(parent, "智谱AI (BigModel)", "zhipu")
        self.zhipu_api_key = tk.StringVar()
        self.zhipu_api_url = tk.StringVar(value="https://open.bigmodel.cn/api/paas/v4/chat/completions")

        ttk.Label(zhipu_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=5)
        zhipu_key_entry = ttk.Entry(zhipu_frame, textvariable=self.zhipu_api_key, width=40)
        zhipu_key_entry.grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(zhipu_frame, text="API URL:").grid(row=1, column=0, sticky='w', pady=5)
        zhipu_url_entry = ttk.Entry(zhipu_frame, textvariable=self.zhipu_api_url, width=40)
        zhipu_url_entry.grid(row=1, column=1, sticky='ew', pady=5)

        # 智谱AI模型选择
        ttk.Label(zhipu_frame, text="选择模型:").grid(row=2, column=0, sticky='w', pady=(10, 5))
        self.zhipu_model = tk.StringVar(value="glm-4")
        zhipu_model_combo = ttk.Combobox(
            zhipu_frame,
            textvariable=self.zhipu_model,
            values=["glm-4", "glm-4-plus", "glm-4-air", "glm-4-flash"],
            state='readonly',
            width=37
        )
        zhipu_model_combo.grid(row=2, column=1, sticky='ew', pady=(10, 5))

        # DeepSeek配置
        deepseek_frame = self.create_api_section(parent, "DeepSeek", "deepseek")
        self.deepseek_api_key = tk.StringVar()
        self.deepseek_api_url = tk.StringVar(value="https://api.deepseek.com/v1/chat/completions")

        ttk.Label(deepseek_frame, text="API Key:").grid(row=0, column=0, sticky='w', pady=5)
        deepseek_key_entry = ttk.Entry(deepseek_frame, textvariable=self.deepseek_api_key, width=40)
        deepseek_key_entry.grid(row=0, column=1, sticky='ew', pady=5)

        ttk.Label(deepseek_frame, text="API URL:").grid(row=1, column=0, sticky='w', pady=5)
        deepseek_url_entry = ttk.Entry(deepseek_frame, textvariable=self.deepseek_api_url, width=40)
        deepseek_url_entry.grid(row=1, column=1, sticky='ew', pady=5)

        # DeepSeek模型选择
        ttk.Label(deepseek_frame, text="选择模型:").grid(row=2, column=0, sticky='w', pady=(10, 5))
        self.deepseek_model = tk.StringVar(value="deepseek-chat")
        deepseek_model_combo = ttk.Combobox(
            deepseek_frame,
            textvariable=self.deepseek_model,
            values=["deepseek-chat", "deepseek-reasoner"],
            state='readonly',
            width=37
        )
        deepseek_model_combo.grid(row=2, column=1, sticky='ew', pady=(10, 5))

        # 当前选中的模型显示
        model_info_frame = ttk.Frame(parent)
        model_info_frame.pack(fill='x', pady=20)
        ttk.Label(
            model_info_frame,
            text="📌 当前使用: 未选择",
            font=('Microsoft YaHei', 11, 'bold'),
            foreground=self.colors['text_light']
        ).pack()

        # 切换按钮
        switch_btn_frame = ttk.Frame(parent)
        switch_btn_frame.pack(fill='x', pady=10)

        ttk.Button(
            switch_btn_frame,
            text="🔄 切换模型",
            command=self.switch_model,
            style='Primary.TButton'
        ).pack(side='left', padx=(0, 10))

        self.save_btn = ttk.Button(
            switch_btn_frame,
            text="💾 保存配置",
            command=self.save_config
        )
        self.save_btn.pack(side='left')

        # 加载已保存的配置
        self.load_config()

    def create_api_section(self, parent, title, prefix):
        """创建API配置部分"""
        frame = ttk.LabelFrame(parent, text=title, padding=10)
        frame.pack(fill='x', pady=(0, 10))
        return frame

    def setup_chat_area(self, parent):
        """设置聊天/测试区域"""
        # 选择模型按钮
        select_frame = ttk.Frame(parent)
        select_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(
            select_frame,
            text="选择要测试的模型:",
            font=('Microsoft YaHei', 10)
        ).pack(side='left')

        self.model_name = tk.StringVar()
        self.model_name.set("未选择")

        model_btn = ttk.Combobox(
            select_frame,
            textvariable=self.model_name,
            values=["智谱AI - glm-4", "DeepSeek - deepseek-chat", "DeepSeek - deepseek-reasoner"],
            state='readonly',
            width=35
        )
        model_btn.pack(side='left', padx=10)
        model_btn.bind('<<ComboboxSelected>>', self.on_model_selected)

        # 测试按钮
        test_btn = ttk.Button(
            select_frame,
            text="🚀 测试连接",
            command=self.test_connection,
            style='Primary.TButton'
        )
        test_btn.pack(side='right')

        # 对话区域
        chat_container = ttk.Frame(parent)
        chat_container.pack(fill='both', expand=True, pady=(0, 10))

        # 输入区域
        input_frame = ttk.LabelFrame(chat_container, text="💬 对话/测试", padding=10)
        input_frame.pack(fill='x', pady=(0, 10))

        # 添加说明标签
        ttk.Label(input_frame, text="请输入测试内容:", font=('Microsoft YaHei', 9)).pack(anchor='w', pady=(0, 5))

        # 使用Entry输入
        self.message_entry = ttk.Entry(input_frame, font=('Microsoft YaHei', 10), width=50)
        self.message_entry.pack(fill='x', pady=(0, 10))
        self.message_entry.insert(0, "请输入您想测试的内容...")

        # 按钮
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(fill='x', pady=10)

        send_btn = ttk.Button(
            btn_frame,
            text="🚀 发送请求",
            command=self.send_request,
            style='Primary.TButton'
        )
        send_btn.pack(side='left', padx=(0, 10))

        clear_btn = ttk.Button(
            btn_frame,
            text="🗑️ 清空",
            command=self.clear_chat
        )
        clear_btn.pack(side='left')

        # 响应显示区域
        response_frame = ttk.LabelFrame(chat_container, text="📤 响应结果", padding=10)
        response_frame.pack(fill='both', expand=True)

        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            height=15,
            font=('Microsoft YaHei', 10),
            wrap='word'
        )
        self.response_text.pack(fill='both', expand=True)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")

        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        )
        status_bar.pack(fill='x', side='bottom')

    def on_model_selected(self, event):
        """模型选择变化"""
        self.update_model_display()

    def update_model_display(self):
        """更新模型显示"""
        model_name = self.model_name.get()
        if model_name == "智谱AI - glm-4":
            self.status_var.set(f"📌 当前使用: 智谱AI - {self.zhipu_model.get()}")
        elif model_name == "DeepSeek - deepseek-chat":
            self.status_var.set(f"📌 当前使用: DeepSeek - {self.deepseek_model.get()}")
        elif model_name == "DeepSeek - deepseek-reasoner":
            self.status_var.set(f"📌 当前使用: DeepSeek - {self.deepseek_model.get()}")

    def switch_model(self):
        """切换模型"""
        model_choice = self.model_name.get()

        if model_choice == "智谱AI - glm-4":
            if not self.zhipu_api_key.get():
                messagebox.showwarning("警告", "请先输入智谱AI的API Key!")
                return
            self.status_var.set(f"✅ 已切换到智谱AI - {self.zhipu_model.get()}")
            messagebox.showinfo("成功", f"已切换到智谱AI - {self.zhipu_model.get()}\n\n请输入测试内容并发送请求。")

        elif model_choice == "DeepSeek - deepseek-chat":
            if not self.deepseek_api_key.get():
                messagebox.showwarning("警告", "请先输入DeepSeek的API Key!")
                return
            self.status_var.set(f"✅ 已切换到DeepSeek - {self.deepseek_model.get()}")
            messagebox.showinfo("成功", f"已切换到DeepSeek - {self.deepseek_model.get()}\n\n请输入测试内容并发送请求。")

        elif model_choice == "DeepSeek - deepseek-reasoner":
            if not self.deepseek_api_key.get():
                messagebox.showwarning("警告", "请先输入DeepSeek的API Key!")
                return
            self.status_var.set(f"✅ 已切换到DeepSeek - {self.deepseek_model.get()}")
            messagebox.showinfo("成功", f"已切换到DeepSeek - {self.deepseek_model.get()}\n\n请输入测试内容并发送请求。")

    def save_config(self):
        """保存配置到文件"""
        config = {
            'zhipu': {
                'api_key': self.zhipu_api_key.get(),
                'api_url': self.zhipu_api_url.get(),
                'model': self.zhipu_model.get()
            },
            'deepseek': {
                'api_key': self.deepseek_api_key.get(),
                'api_url': self.deepseek_api_url.get(),
                'model': self.deepseek_model.get()
            }
        }

        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("成功", "配置已保存到 config.json")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")

    def load_config(self):
        """从文件加载配置"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)

            if 'zhipu' in config and config['zhipu']['api_key']:
                self.zhipu_api_key.set(config['zhipu']['api_key'])
                self.zhipu_api_url.set(config['zhipu']['api_url'])
                self.zhipu_model.set(config['zhipu']['model'])

            if 'deepseek' in config and config['deepseek']['api_key']:
                self.deepseek_api_key.set(config['deepseek']['api_key'])
                self.deepseek_api_url.set(config['deepseek']['api_url'])
                self.deepseek_model.set(config['deepseek']['model'])

        except FileNotFoundError:
            pass  # 没有配置文件，使用默认值

    def test_connection(self):
        """测试API连接"""
        model_choice = self.model_name.get()
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, f"🔄 测试 {model_choice} 的连接...\n")

        if model_choice == "智谱AI - glm-4":
            api_key = self.zhipu_api_key.get()
            model = self.zhipu_model.get()
            api_url = self.zhipu_api_url.get()

            if not api_key:
                self.response_text.insert(tk.END, f"❌ 错误: 请先输入智谱AI的API Key\n", 'error')
                return

            try:
                response = requests.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "你好，请回复OK"}],
                        "stream": False
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    self.response_text.insert(tk.END, f"✅ 连接成功！\n\n{content}\n", 'success')
                else:
                    self.response_text.insert(tk.END, f"❌ 连接失败\n状态码: {response.status_code}\n{response.text}\n", 'error')

            except Exception as e:
                self.response_text.insert(tk.END, f"❌ 请求失败\n{str(e)}\n", 'error')

        elif model_choice == "DeepSeek - deepseek-chat" or model_choice == "DeepSeek - deepseek-reasoner":
            api_key = self.deepseek_api_key.get()
            model = self.deepseek_model.get()
            api_url = self.deepseek_api_url.get()

            if not api_key:
                self.response_text.insert(tk.END, f"❌ 错误: 请先输入DeepSeek的API Key\n", 'error')
                return

            try:
                response = requests.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "你好，请回复OK"}],
                        "stream": False
                    },
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    self.response_text.insert(tk.END, f"✅ 连接成功！\n\n{content}\n", 'success')
                else:
                    self.response_text.insert(tk.END, f"❌ 连接失败\n状态码: {response.status_code}\n{response.text}\n", 'error')

            except Exception as e:
                self.response_text.insert(tk.END, f"❌ 请求失败\n{str(e)}\n", 'error')

        else:
            self.response_text.insert(tk.END, "❌ 请先选择一个模型\n", 'error')

    def send_request(self):
        """发送API请求"""
        model_choice = self.model_name.get()

        if model_choice == "智谱AI - glm-4":
            api_key = self.zhipu_api_key.get()
            model = self.zhipu_model.get()
            api_url = self.zhipu_api_url.get()
            user_message = self.message_var.get()

            if not api_key or not user_message:
                messagebox.showwarning("警告", "请先选择模型并输入测试内容!")
                return

            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, f"🤖 发送请求到智谱AI - {model}...\n\n")

            try:
                response = requests.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": user_message}],
                        "stream": False
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    self.response_text.insert(tk.END, f"✅ 响应成功！\n\n{content}\n", 'success')
                else:
                    self.response_text.insert(tk.END, f"❌ 请求失败\n状态码: {response.status_code}\n{response.text}\n", 'error')

            except Exception as e:
                self.response_text.insert(tk.END, f"❌ 请求失败\n{str(e)}\n", 'error')

        elif model_choice == "DeepSeek - deepseek-chat" or model_choice == "DeepSeek - deepseek-reasoner":
            api_key = self.deepseek_api_key.get()
            model = self.deepseek_model.get()
            api_url = self.deepseek_api_url.get()
            user_message = self.message_var.get()

            if not api_key or not user_message:
                messagebox.showwarning("警告", "请先选择模型并输入测试内容!")
                return

            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, f"🤖 发送请求到DeepSeek - {model}...\n\n")

            try:
                response = requests.post(
                    api_url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": user_message}],
                        "stream": False
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    self.response_text.insert(tk.END, f"✅ 响应成功！\n\n{content}\n", 'success')
                else:
                    self.response_text.insert(tk.END, f"❌ 请求失败\n状态码: {response.status_code}\n{response.text}\n", 'error')

            except Exception as e:
                self.response_text.insert(tk.END, f"❌ 请求失败\n{str(e)}\n", 'error')

        else:
            self.response_text.insert(tk.END, "❌ 请先选择一个模型\n", 'error')

    def clear_chat(self):
        """清空对话"""
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(tk.END, "对话已清空\n")

def main():
    """主函数"""
    root = tk.Tk()
    app = ModelSwitcher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
