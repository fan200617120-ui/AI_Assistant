# AI_Assistant

一键部署本地 AI 助手（Ollama + Gradio）  
One‑click deployment for a local AI assistant (Ollama + Gradio).

---

## 本地 AI 助手整合包 完整使用 + 初始化指南

**轻舟 AI · LightShip**  
轻舟渡万境，一智载千灵。  
One Ship, All Souls. One AI, All Minds.

一个极简、便携的本地 AI 基础框架，解压即用，模型自备。

---

本工具提供本地运行的聊天界面，支持多模态图片识别、记忆对话、在线 AI 入口及提示词模板。

![Chat UI 界面展示](https://github.com/fan200617120-ui/AI_Assistant/blob/main/chat_ui.png)

---

## 下载整合包

通过网盘分享的文件：本地 AI 部署  
链接: https://pan.baidu.com/s/1OTsi50VMkwVc_znh5uMpLQ?pwd=6688  
提取码: `6688`

---

## 安装准备

1. 下载 `AI_Assistant` WebUI 包并解压，建议放在**非 C 盘根目录**
2. 路径必须为**纯英文**，不可包含中文、空格或特殊符号
3. 下载 Ollama 便携版：  
   https://github.com/ollama/ollama/releases

---

## 🚀 正确初始化操作（必看）

### 1. 解压位置要清爽
- 将 `ollama-windows-amd64.zip` 解压到纯英文目录，例如：
  - `G:\Ollama\AI_Assistant`
  - `D:\AI_Assistant`
- **不要解压到 `C:\Users\` 下**，容易出现权限问题

### 2. 设置环境变量（防止 C 盘爆炸）
右键「此电脑」→ 属性 → 高级系统设置 → 环境变量  
在「系统变量」中新建：

- **变量名**：`OLLAMA_MODELS`
- **变量值**：`D:\AI_Assistant\models`（任意非 C 盘英文路径）

作用：强制 Ollama 将模型存放在你指定的位置。

### 3. 验证安装
打开 CMD，进入解压目录执行：
```bash
ollama -v
```
显示版本号即成功。

### 4. 启动服务
运行 `_Public release.bat`，选择 **3 仅启动 Ollama 服务**
```bash
ollama serve
```
看到 `Listening on 127.0.0.1:11434` 表示服务正常，**窗口不要关闭**。

### 5. 模型下载（新开一个 CMD）
Ollama 模型库：https://ollama.com/search

常用命令：
```bash
ollama -v                     # 查看版本
ollama list                   # 查看已安装模型
ollama pull qwen3.5:0.8b      # 下载模型
ollama run qwen3.5:0.8b       # 运行模型
ollama rm qwen3.5:0.8b        # 删除模型
```

---

## ✅ 初始化检查清单
- [x] Ollama 已解压到纯英文目录
- [x] 已设置 `OLLAMA_MODELS` 环境变量
- [x] `ollama -v` 正常显示版本
- [x] `ollama serve` 正常监听 11434 端口
- [x] `启动助手.bat` 与 `ollama.exe` 在同一目录
- [x] 已下载至少一个模型

---

## 文件结构

```
D:\AI_Assistant
│   ollama.exe
│   vc_redist.x64.exe
│   下载模型说明.txt
│   启动服务.bat
│   启动助手.bat
│
├── core/                # 核心脚本
├── models/              # 模型存放目录
├── python_embeded/      # 嵌入式 Python
├── lib/
└── logs/
```

---

## 快速开始

1. 确保已用 `ollama pull` 下载模型
2. 双击 `启动助手.bat`
3. 菜单说明：
   - [1] 启动服务 + 有记忆聊天界面
   - [2] 启动服务 + 无记忆聊天界面
   - [3] 仅启动 Ollama 服务
   - [4] 退出
4. 等待自动打开浏览器界面

---

## 聊天界面使用

- 左侧：对话区、输入框、发送/停止
- 右侧：
  - 模型选择、温度、最大生成长度
  - 图片上传（仅多模态模型支持）
  - 服务状态检查
  - 清空对话与记忆

支持多模态模型示例：  
`qwen3.5:4b`、`qwen3.5:9b`、`qwen3-vl:8b`

---

## 在线 AI 入口

内置常用 AI 快捷入口：
- DeepL
- DeepSeek
- Kimi
等

内置提示词模板，适合翻译、校对、总结、字幕处理等场景。

---

## 自定义设置

### 1. 修改模型列表（下载后必改）
打开：
- `core/chat_Ai.py`
- `core/chat_Ai_no.py`

找到 `AVAILABLE_MODELS`，按自己下载的模型修改：
```python
AVAILABLE_MODELS = [
    ("qwen3.5:0.8b (小模型)", "qwen3.5:0.8b"),
    ("translategemma:4b (翻译专用)", "translategemma:4b"),
]
```
保存后重启脚本生效。

### 2. 调整记忆长度（仅记忆版）
在 `chat_Ai.py` 中修改：
- `max_history`
- `get_recent_memories(count=...)`

### 3. 更换 Logo
替换 `core/ai_logo.png` 和 `ai_logo.ico` 即可。

---

## 常见问题

**Q: 显示“连接失败”**
A: 检查 Ollama 服务是否启动，确保 `ollama serve` 在运行。

**Q: 提示 404 Not Found**
A: 模型未下载，或 `AVAILABLE_MODELS` 配置与实际不符。

**Q: 生成很慢 / 卡住**
A: 显存不足 fallback 到 CPU，可：
- 使用更小模型（0.8b / 4b）
- 降低 `num_ctx`
- 关闭其他占用显存程序

**Q: 端口被占用**
A: 工具会自动尝试多个端口，仍失败则关闭占用程序。

**Q: C 盘爆炸**
A: 检查 `OLLAMA_MODELS` 环境变量是否设置并重启服务。

**Q: 记忆文件在哪**
A: `core/memory/chat_memory.json`

---

## 免责与版权

本工具仅用于**个人学习与视频剪辑**，禁止商业用途及侵权行为。
软件本身不提供任何模型，模型需自行下载并遵守对应许可证。

作者不对使用造成的任何损失负责。

更新及问题反馈请关注 B 站 UP 主：**光影的故事2018**  
主页：https://space.bilibili.com/381518712

祝使用愉快！😊
