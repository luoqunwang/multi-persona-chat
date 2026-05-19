# 🎭 多人格 AI 聊天室

一个 AI 课的 final project: 用户可以选择多个 AI 人格(苏格拉底、爱因斯坦、鲁迅...),围绕一个话题展开讨论,用户也能随时插话参与。

## 项目阶段

- **V1 (第 1-2 周)**: 终端版 → 网站版基础聊天室 ⬅️ 当前阶段
- **V1.5 (第 3 周)**: UI 美化、自定义人格、对话导出
- **V2 (第 4-5 周,选做)**: 加入说服力评分系统(微调 BERT)

## 技术栈

- **后端**: Python + FastAPI + Anthropic API
- **前端**: HTML + CSS + JavaScript (V1 不上 React,先简单)
- **AI 模型**: Claude (Haiku 用于测试, Sonnet/Opus 用于最终演示)

## 🚀 第一天: 跑通终端版

### 1. 在 VS Code 里打开项目
```bash
cd multi-persona-chat
code .
```

### 2. 安装推荐扩展
VS Code 会自动提示, 或者手动装这几个:
- Python (微软官方)
- Pylance
- Jupyter (后期训练模型用)
- Thunder Client (后期测试 API 用)

### 3. 创建虚拟环境
打开 VS Code 终端 (`Ctrl+` `):
```bash
python -m venv venv
```

激活虚拟环境:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

成功的话终端最前面会出现 `(venv)`。

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 配置 API Key
```bash
# Windows
copy .env.example .env
# Mac/Linux
cp .env.example .env
```

然后打开 `.env` 文件, 填入你的 Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

🔑 申请 API key:  https://console.anthropic.com/

⚠️ `.env` 文件已经在 `.gitignore` 里, 绝对不会被提交到 GitHub, 放心。

### 6. 跑起来!
```bash
cd backend
python terminal_chat.py
```

你应该会看到:
```
🎭 多人格 AI 聊天室 (终端版)
可用人格:
  1. 🏛️ 苏格拉底
  2. 🧠 爱因斯坦
  3. ✍️ 鲁迅

请输入讨论话题:
```

### 7. 试试这些操作
- 输入话题, 比如: "AI 会取代人类吗?"
- 输入 `a` 让所有人格轮流发言一次
- 输入 `1` 让苏格拉底单独发言
- 输入任意文字插话, 然后输入 `2` 让爱因斯坦回应你
- 输入 `q` 退出

## 项目结构
```
multi-persona-chat/
├── backend/
│   ├── personas.py          # 人格定义 (system prompts)
│   ├── chat_engine.py       # 对话引擎核心
│   ├── terminal_chat.py     # 终端版入口 (V1 阶段)
│   └── main.py              # FastAPI 入口 (下一步要写)
├── frontend/                # 网页前端 (下一步要写)
├── notebooks/               # V2 训练评分模型用
├── requirements.txt
├── .env.example
└── .gitignore
```

## 下一步 (跑通终端版之后)

1. ✅ 终端能正常对话
2. ⬜ 加 FastAPI 后端, 暴露 `/chat` 接口
3. ⬜ 写前端 HTML 页面
4. ⬜ 接前后端
5. ⬜ 加流式输出(打字机效果)
6. ⬜ 部署 + 写报告

## 常见问题

**Q: 报错 `ANTHROPIC_API_KEY` 找不到?**
A: 确认 `.env` 在项目根目录,内容是 `ANTHROPIC_API_KEY=sk-ant-xxx` 这种格式,没有引号没有空格。

**Q: 人格说话不像?**
A: 改 `personas.py` 里的 system_prompt,多加几个具体例子。Prompt engineering 本身就是 V1 阶段最重要的实验内容。

**Q: API 调用花钱吗?**
A: Claude Haiku 很便宜 (大概 1 美元能聊几千轮),开发期完全够用。Anthropic 新账号通常有免费额度。
