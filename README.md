# AI_Assistant
一键部署本地 AI 助手（Ollama + Gradio）;One‑click deployment for a local AI assistant (Ollama + Gradio).
本地AI助手整合包 完整使用+初始化指南
轻舟 AI・LightShip —— 轻舟渡万境，一智载千灵。
One Ship, All Souls. One AI, All Minds.
一个极简、便携的本地 AI 基础框架，解压即用，模型自备。====================================================
本工具提供本地运行的聊天界面，支持多模态图片识别、记忆对话、在线AI入口及提示词模板。

通过网盘分享的文件：本地AI部署
链接: https://pan.baidu.com/s/1OTsi50VMkwVc_znh5uMpLQ?pwd=6688 提取码: 6688

最先做的是下载我的AI_Assistant的webUI包，解压。最好是非C盘根目录,路径必须纯英文，不能有中文、空格、特殊符号的固态高速来硬盘；

再到官网下载便携包：https://github.com/ollama/ollama/releases

🚀正确的初始化操作
这是使用整合包的前提，务必先完成以下操作，避免权限、路径、模型存储等问题：
1️⃣ 解压位置要清爽
•	把你新下载的 `ollama-windows-amd64.zip` 解压到 纯英文目录AI_Assistant，比如 `G:\Ollama\AI_Assistant ` 或 `D:\AI_Assistant`。
•	千万不要解压到 `C:\Users\你的用户名\` 下面，那里权限坑太多，容易出现运行失败。
2️⃣ 设置环境变量（绕过C盘陷阱）
打开「环境变量」设置（右键「此电脑」→属性→高级系统设置→环境变量），在「系统变量」里新建，如：
•	变量名：`OLLAMA_MODELS`
•	变量值：`G:\Ollama\models`（或你希望存放模型的任意位置，必须纯英文，建议设置为 `D:\AI_Assistant\models`，与整合包模型目录统一）
作用：让 Ollama 把模型文件放到你指定的盘，从此 C 盘再也不会被大模型撑爆！
3️⃣ 验证安装
开一个 CMD 窗口，进入解压目录（比如 `D:\AI_Assistant`），执行：
ollama -v
如果显示版本号（比如 `0.17.7`），说明便携版Ollama已经就绪。
4️⃣ 启动服务
打开启动器 _Public release.bat，选3，只打开Ollama 服务；
ollama serve
看到 `Listening on 127.0.0.1:11434` 就说明服务正常运行了。这个窗口不要关，它是 AI 的“大脑”，关闭后聊天界面无法连接服务。

5️⃣ 模型下载：
新开一个 CMD 窗口
然后到https://ollama.com/search，选择适合你的模型；
操作命令如下：先ctrl+C再到CMD窗口里右击即可粘贴！
查看版本命令： ollama -v

列出本地模型命令：ollama list

下载相关模型命令：ollama pull translategemma:4b

CMD里运行模型命令：ollama run qwen3.5:0.8b

删除模型命令：ollama rm qwen3.5:0.8b

✅ 初始化检查清单
•	[x] Ollama 解压到纯英文目录
•	[x] 设置了 `OLLAMA_MODELS` 环境变量
•	[x] 执行 `ollama -v` 能正常显示版本
•	[x] 执行 `ollama serve` 能正常监听端口 
•	[x] 整合包里的 `启动助手.bat` 和 `ollama.exe` 在同一目录
•	[x]下载模型；

一、文件结构
------------
D:\AI_Assistant（推荐目录，与Ollama解压目录一致）
│   ollama.exe                  Ollama 主程序（已替换为最新便携版）
│   vc_redist.x64.exe            Visual C++ 运行库（如需）
│   下载模型说明.txt              模型下载指引
│   启动服务.bat                  仅启动 Ollama 服务的脚本
│   启动助手.bat                  多功能菜单启动器（推荐使用）
│
├─core                           核心脚本目录
│   ├─ai_logo.ico                浏览器标签页图标
│   ├─ai_logo.png                页面顶部 Logo
│   ├─ai_logo_large.png          备用大 Logo（未使用）
│   ├─chat_Ai.py                 有记忆版聊天界面
│   ├─chat_Ai_no.py              无记忆版聊天界面
│   └─memory                     记忆文件存储目录
│
├─models                         模型文件存放目录（GGUF 或 Ollama 模型，与 OLLAMA_MODELS 环境变量对应）
├─python_embeded                 嵌入式 Python 环境（含 Gradio 等依赖）
├─lib                             其他依赖库（一般无需关心）
└─logs                           日志文件（如有）

二、快速开始（初始化完成后）
------------
1. 确保已通过 Ollama 下载了至少一个模型（如 qwen3.5:0.8b）。若未下载，请参考“下载模型说明.txt”，或在 CMD 中执行 `ollama pull 模型名` 下载。
2. 双击根目录下的 `启动助手.bat`，出现菜单：
   [1] 启动 Ollama 服务 + 有记忆版聊天界面
   [2] 启动 Ollama 服务 + 无记忆版聊天界面
   [3] 仅启动 Ollama 服务（不打开界面）
   [4] 退出
3. 输入对应数字后按回车：
   - 选择 1 或 2 后，会先在新窗口启动 Ollama 服务，稍后自动打开浏览器进入聊天界面。
   - 如果服务已启动（手动执行过 `ollama serve`），请勿重复启动，可直接选 3 仅运行界面（需手动运行脚本）。
4. 首次打开界面时，请检查右上角状态栏显示“Ollama服务运行正常”，否则请检查服务是否启动。

三、聊天界面使用
----------------
左侧主区域：对话历史、输入框、发送/停止按钮。
右侧边栏：
   - 模型设置：选择已下载的模型、调整温度、最大生成长度。
   - 图片上传：仅多模态模型（如qwen3.5:4b qwen3.5:9b, qwen3-vl:8b）支持图片识别，上传后模型可“看图说话”。
   - 检查服务：手动刷新服务状态。
   - 清空对话：清除当前聊天记录和记忆（有记忆版同时清空记忆文件）。

四、在线AI入口（第二个标签页）
-----------------------------
点击按钮可直接在默认浏览器中打开常用 AI 网站（如 DeepL、DeepSeek、Kimi 等）。
下方提供多种预置提示词模板，方便复制后到网站使用，特别适合字幕翻译、ASR 校对、长文本总结等任务。

五、自定义设置
--------------
1. 模型列表配置（下载模型后必做！）
✨ 重要提醒：下载完模型，记得同步一下代码配置！
下载模型后，脚本里默认的模型列表可能跟你下载的不完全一样。如果不改，界面里可能会显示你根本没下载的模型，选错就会报 404 哦！
解决办法超简单——两步走：
① 打开 `core` 文件夹，找到 `chat_Ai.py` 和 `chat_Ai_no.py`（有记忆和无记忆两个脚本，都改一下更保险）。
② 找到 `AVAILABLE_MODELS` 这个列表（大概在文件开头），它看起来像这样：
AVAILABLE_MODELS = [
    ("qwen3.5:0.8b (小模型)", "qwen3.5:0.8b"),
    ("qwen3.5:4b-q8_0 (多模态, 推荐)", "qwen3.5:4b-q8_0"),
    ("qwen3.5:9b (多模态Q4_K_M)", "qwen3.5:9b"),
    ...
]
你只需要做三件事：
•	删除 你实际没下载的模型条目（比如你没下 4b 版本，就删掉那一行）。
•	添加 你自己额外下载的模型（比如 `deepseek-r1:7b`），格式照着写就行：`("显示名字", "实际模型名")`。
•	调整顺序，把你最常用的模型放到最前面，这样默认就会选中它。
举个栗子：
假设你只下载了 `qwen3.5:0.8b` 和 `translategemma:4b`，那么列表可以精简成：
python
AVAILABLE_MODELS = [
    ("qwen3.5:0.8b (小模型)", "qwen3.5:0.8b"),
    ("translategemma:4b (翻译专用)", "translategemma:4b"),
]
改完记得保存文件，然后重启脚本（选 1 或 2 重新打开界面），新的模型列表就生效啦！
这一步虽然小，但能帮你避免很多莫名其妙的报错，聪明人都不会跳过哦～
2. 调整记忆长度（仅对有记忆版）
在 `chat_Ai.py` 中找到 `AsyncMemoryManager` 初始化参数，修改 `max_history`（默认10）和 `get_recent_memories` 中的 count（默认3）。
3. 更换 Logo
将新的图片文件（推荐 PNG 格式）命名为 `ai_logo.png` 并替换 `core` 目录下的原文件，同时可替换 `ai_logo.ico` 作为浏览器标签图标。

六、常见问题
------------
Q: 启动界面后显示“连接失败”？
A: 请确保 Ollama 服务已运行（可查看任务管理器有无 ollama.exe 进程）。若未启动，请运行 `启动服务.bat` 或通过菜单选项启动。
Q: 选择模型后提示 404 Not Found？
A: 说明 Ollama 中没有该模型，请先使用 `ollama pull 模型名` 下载模型。可通过 `ollama list` 查看已安装模型；若已下载，检查 `AVAILABLE_MODELS` 列表是否配置正确。
Q: 生成很慢或卡在“正在生成”？
A: 可能是显存不足导致回退到 CPU 运行，可尝试：
   - 使用更小的模型（如 4b 或 0.8b）。
   - 在脚本中降低 `num_ctx` 值（默认 2048）。
   - 关闭其他占用显存的程序。
   - 确保启动 Ollama 时设置了 GPU 层数（如 `set OLLAMA_NUM_GPU=35` 再启动服务）。
Q: 端口被占用？
A: 脚本会自动尝试 7863、7961、7861、7862、7960 等多个端口，直到成功。如果仍失败，请手动修改脚本中的 `ports_to_try` 列表或关闭占用端口的程序；Ollama 服务默认端口 11434，若被占用，需关闭占用进程。
Q: 记忆版保存的记忆文件在哪里？
A: 位于 `core\memory\chat_memory.json`，可用文本编辑器查看或删除。
Q: C盘被模型文件撑爆？
A: 检查 `OLLAMA_MODELS` 环境变量是否设置正确，确保模型文件存放在你指定的非C盘目录；若已设置，重新启动 Ollama 服务生效。

七、免责与版权
--------------
本工具仅用于个人学习与视频剪辑使用，禁止用于商业用途及侵权行为。
软件包本身不提供任何模型文件，模型需用户自行从官方渠道获取，并遵守其许可证。
作者不对因使用本软件造成的任何损失负责。
更新及问题反馈请关注 B 站 up 主：光影的故事2018
主页：https://space.bilibili.com/381518712
祝使用愉快！😊
|
