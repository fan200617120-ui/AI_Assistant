#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
chat_Ai.py - 正式版
聊天（有记忆，基于 /api/generate）+ 在线AI入口 + 页脚 + Logo
移植自 ai_director.py 的思考过程解析器
Copyright 2026 光影的故事2018
"""

import sys
import os
SCRIPT_DIR = os.path.dirname(__file__)
sys.path.insert(0, SCRIPT_DIR)

import gradio as gr
import requests
import json
import time
import re
import base64
import threading
import webbrowser
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# ==================== 模型配置 ====================
AVAILABLE_MODELS = [
    ("qwen3.5:4b (通用/多模态)", "qwen3.5:4b"),
    ("qwen3.5-9b-ud:latest (通用)", "qwen3.5-9b-ud:latest"),
    ("qwen3.5:9b (通用/多模态)", "qwen3.5:9b"),
    ("qwen3-vl:8b (多模态视觉)", "qwen3-vl:8b"),
    ("translategemma:4b (翻译专用)", "translategemma:4b"),
    ("deepseek-r1-8b-q5 (深度推理)", "deepseek-r1-8b-q5"),
]

IMAGE_SUPPORTED_MODELS = {"qwen3.5:4b", "qwen3.5:9b", "qwen3-vl:8b"}
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
# =================================================

# ---------- 记忆管理器 ----------
class AsyncMemoryManager:
    def __init__(self, memory_file="memory/chat_memory.json", max_history=10):
        self.memory_file = os.path.join(SCRIPT_DIR, memory_file)
        self.max_history = max_history
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.memories = self._load_memories()

    def _ensure_directory(self):
        directory = os.path.dirname(self.memory_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _load_memories(self):
        self._ensure_directory()
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("memories", [])
            except:
                return []
        return []

    def _save_memories_sync(self):
        with self._lock:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({"memories": self.memories}, f, ensure_ascii=False, indent=2)

    def add_memory(self, user_msg, ai_msg):
        memory = {
            "user": user_msg[:500],
            "ai": ai_msg[:500],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": time.time()
        }
        with self._lock:
            self.memories.append(memory)
            if len(self.memories) > self.max_history:
                self.memories = self.memories[-self.max_history:]
        self._executor.submit(self._save_memories_sync)

    def get_recent_memories(self, count=3):
        with self._lock:
            return self.memories[-count:] if self.memories else []

    def clear_memory(self):
        with self._lock:
            self.memories = []
        self._executor.submit(self._save_memories_sync)

memory_manager = AsyncMemoryManager()

# ---------- 全局标志 ----------
current_streaming = False
stop_flag = False

# ---------- 在线AI网站 URL ----------
URLS = {
    "DeepL": "https://www.deepl.com/zh",
    "有道翻译": "https://fanyi.youdao.com/",
    "豆包": "https://www.doubao.com/",
    "通义千问": "https://www.qianwen.com/",
    "DeepSeek": "https://www.deepseek.com/",
    "ChatGLM": "https://chatglm.cn",
    "Kimi": "https://kimi.moonshot.cn/",
    "腾讯元宝": "https://yuanbao.tencent.com/",
}

# ---------- 预置提示词 ----------
PROMPTS = {
    "SRT字幕翻译(保留时间码)": """你是一个专业的字幕翻译专家。请将以下SRT字幕内容翻译成中文。
要求：
1. 严格保留原文的时间轴格式 (例如: 00:00:01,000 --> 00:00:03,000)。
2. 保持字幕序号不变。
3. 翻译要自然流畅，适合口语表达，注意联系上下文语境。
4. 对于专有名词或专业术语，请保持一致性。
5. 直接输出翻译后的SRT内容，不要包含解释。

原文内容：
""",
    "语义断句与合并(ASR优化)": """你是专业字幕精修师。
我将给你ASR识别的带时间戳字幕，可能是碎句、断句错误、错别字。
请按以下规则处理：

1. 按语义合并碎句，不要在一句话中间切开。
2. 每条字幕中文字数 ≤ 20 字。
3. 合并多条时，开始时间=第一条，结束时间=最后一条。
4. 自动修正ASR错别字、同音字错误。
5. 去掉口语冗余词：那个、就是、然后、嘛、啊等。
6. 输出严格标准SRT格式，不要任何解释、不要JSON。

输入内容：
""",
    "短视频极速版(10字以内)": """你是短视频字幕专家。
规则：
1. 每一条字幕 ≤ 12 个字。
2. 必须按语义断句,不许硬切词、不许乱时序。
3. 短句、有力、适合短视频节奏。
4. 自动合并、自动拆分过长句。
5. 保留时间码，输出标准SRT。

输入内容：
""",
    "双语字幕版(中英对照)": """你是专业字幕翻译。
规则：
1. 保留原时间轴。
2. 中文在上，英文在下。
3. 语言自然口语化，不生硬。
4. 输出标准SRT。

输入内容：
""",
    "双语字幕生成(中英对照)": """请将以下文本翻译成中文，并生成中英双语对照格式。
格式要求：
第一行：原文
第二行：译文
(空行分隔不同段落)

请处理以下内容：
""",
    "文本润色与校对": """请对以下文本进行润色和校对。
要求：
1. 修正错别字和标点符号错误。
2. 优化语句通顺度，使其更符合中文阅读习惯。
3. 保持原意不变，不增加或删减关键信息。
4. 如果没有错误，请原样输出。

待处理文本：
""",
    "长文本总结(适合Kimi/元宝)": """请阅读以下长文本，并进行总结。
要求：
1. 提炼出核心观点和关键信息。
2. 使用条理清晰的列表形式输出。
3. 语言简洁明了。

文本内容：
""",
    "ASR校对与纠错(专业版)": """你是一个专业的校对员。以下是 ASR 语音识别的原始结果，可能包含错别字。
请根据上下文修正错别字，并输出修正后的纯文本内容。

要求：
1. 重点修正同音字错误。
2. 保持原意，不要大幅改写。
3. 输出修正后的文本即可。

原文内容：
"""
}

def open_url(url):
    webbrowser.open(url)
    return f"✅ 已打开 {url}，请查看浏览器"

def update_prompt(prompt_name):
    return PROMPTS.get(prompt_name, "")

# ---------- 图片编码 ----------
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print(f"图片编码失败: {e}")
        return None

# ---------- 构建带记忆的提示词 ----------
def build_prompt_with_memory(message, model):
    current_date = datetime.now().strftime("%Y年%m月%d日")
    recent = memory_manager.get_recent_memories(3)
    context = f"今天是 {current_date}。\n\n"
    if recent:
        context += "以下是最近的对话记忆，请参考以保持连贯性：\n\n"
        for mem in recent:
            context += f"用户：{mem['user']}\n助手：{mem['ai']}\n\n"
    if "translate" in model:
        context += f"用户要求翻译以下内容（请直接给出翻译结果，不要添加解释）：\n{message}\n翻译："
    else:
        context += f"用户的新消息：{message}\n助手："
    return context

# ========== 思考解析器 ==========
def _extract_thought_content(thoughts: str) -> str:
    if not thoughts:
        return ""
    thought_content = re.sub(r'<think>|</think>', '', thoughts)
    return thought_content.strip()

def format_thoughts_with_collapsible(thoughts: str) -> str:
    thought_content = _extract_thought_content(thoughts)
    if not thought_content:
        return ""
    lines = thought_content.split('\n')
    formatted_lines = []
    for line in lines:
        if line.strip():
            formatted_lines.append(f"<em>{line}</em>")
        else:
            formatted_lines.append("<br>")
    formatted_content = "<br>".join(formatted_lines)
    return f'''
    <details class="thoughts-details">
        <summary><strong>[设计思考过程]</strong>（点击展开/折叠）</summary>
        <div class="thoughts-content">
            {formatted_content}
        </div>
    </details>
    '''

def format_thoughts_streaming(thoughts: str) -> str:
    thought_content = _extract_thought_content(thoughts)
    if not thought_content:
        return ""
    lines = thought_content.split('\n')
    formatted = "<strong>设计思考过程：</strong><br><br>"
    for i, line in enumerate(lines):
        line = line.strip()
        if line:
            if line.startswith(('首先', '第一', '1.', '- ')):
                formatted += f"<em>1. {line}</em><br>"
            elif line.startswith(('其次', '第二', '然后', '2.')):
                formatted += f"<em>2. {line}</em><br>"
            elif line.startswith(('最后', '第三', '最终', '3.')):
                formatted += f"<em>3. {line}</em><br>"
            elif line.startswith(('所以', '因此', '结论', '总结')):
                formatted += f"<em>总结：{line}</em><br>"
            else:
                formatted += f"<em>• {line}</em><br>"
    return formatted

class StreamResponseParser:
    def __init__(self):
        self.current_thought = ""
        self.current_answer = ""
        self.in_think_tag = False
        self.think_complete = False
        self.has_think_tag = False
        self.start_time = time.time()

    def parse_chunk(self, chunk: str) -> dict:
        result = {
            "thought": "",
            "answer": "",
            "status": "thinking" if not self.think_complete else "answering"
        }
        if not chunk:
            return result

        if '<think>' in chunk or '</think>' in chunk:
            self.has_think_tag = True

        if not self.in_think_tag and '<think>' in chunk:
            self.in_think_tag = True
            parts = chunk.split('<think>', 1)
            if len(parts) > 1:
                chunk = parts[1]
            else:
                chunk = ""

        elif not self.in_think_tag and '</think>' in chunk:
            parts = chunk.split('</think>', 1)
            if len(parts) > 1:
                think_part = parts[0]
                answer_part = parts[1]
                self.current_thought += think_part
                self.think_complete = True
                result["thought"] = self.current_thought
                if answer_part.strip():
                    self.current_answer += answer_part
                    result["answer"] = answer_part
                return result
            else:
                self.current_thought += chunk
                result["thought"] = self.current_thought
                return result

        if self.in_think_tag and '</think>' in chunk:
            parts = chunk.split('</think>', 1)
            think_part = parts[0]
            answer_part = parts[1] if len(parts) > 1 else ""
            self.current_thought += think_part
            self.in_think_tag = False
            self.think_complete = True
            result["thought"] = self.current_thought
            result["status"] = "answering"
            if answer_part.strip():
                self.current_answer += answer_part
                result["answer"] = answer_part
        elif self.in_think_tag:
            self.current_thought += chunk
            result["thought"] = self.current_thought
        elif self.think_complete:
            self.current_answer += chunk
            result["answer"] = chunk
            result["status"] = "answering"
        else:
            self.current_thought += chunk
            result["thought"] = self.current_thought

        return result

    def finalize(self):
        if not self.has_think_tag and self.current_thought:
            self.current_answer = self.current_thought
            self.current_thought = ""
            self.think_complete = True
        return self.current_answer, self.current_thought

    def reset(self):
        self.current_thought = ""
        self.current_answer = ""
        self.in_think_tag = False
        self.think_complete = False
        self.has_think_tag = False
        self.start_time = time.time()

    def get_final_response(self) -> str:
        return self.current_answer.strip()

    def get_processing_time(self) -> str:
        end_time = time.time()
        duration = end_time - self.start_time
        if duration < 60:
            return f"耗时：{duration:.1f}秒"
        else:
            minutes = int(duration // 60)
            seconds = duration % 60
            return f"耗时：{minutes}分{seconds:.1f}秒"
# ===================================================

# ---------- 流式响应（使用移植的解析器）----------
def stream_response(message, image, model, temp, tokens, history):
    global current_streaming, stop_flag

    # 忽略不支持图片的模型上传的图片
    if image is not None and model not in IMAGE_SUPPORTED_MODELS:
        print(f"警告：模型 {model} 不支持图片识别，已忽略上传的图片。")
        image = None

    # 构建包含记忆的完整提示词
    full_prompt = build_prompt_with_memory(message, model)

    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": True,
        "options": {"temperature": temp, "num_predict": tokens}
    }
    if image is not None:
        image_b64 = encode_image_to_base64(image)
        if image_b64:
            payload["images"] = [image_b64]

    start_time = time.time()
    full_reply = ""
    parser = StreamResponseParser()
    timestamp = time.strftime('%H:%M:%S')
    user_content = f"[{timestamp}] 用户：{message}" + (" [附图片]" if image else "")

    updated_history = history + [{"role": "user", "content": user_content}]
    updated_history.append({"role": "assistant", "content": f"[{timestamp}] {model}：正在生成..."})
    yield updated_history, f"模型 [{model}] 正在生成..."

    try:
        stop_flag = False
        current_streaming = True
        response = requests.post(url, json=payload, stream=True, timeout=180)
        response.raise_for_status()

        for line in response.iter_lines():
            if stop_flag:
                current_streaming = False
                updated_history.pop()
                updated_history.append({"role": "assistant", "content": f"[{timestamp}] {model}：{full_reply}\n\n[已手动停止]"})
                yield updated_history, "生成已停止"
                return

            if line:
                try:
                    line_str = line.decode('utf-8')
                    if line_str.strip():
                        data = json.loads(line_str)
                        if 'response' in data:
                            chunk = data['response']
                            full_reply += chunk
                            # 实时更新历史框，显示原始累积回复
                            updated_history[-1] = {"role": "assistant", "content": f"[{timestamp}] {model}：{full_reply}█"}
                            yield updated_history, f"模型 [{model}] 正在生成..."
                except:
                    continue

        current_streaming = False
        end_time = time.time()
        time_cost = end_time - start_time

        # 判断是否为 qwen3.5 系列（直接显示原始回复）
        if "qwen3.5" in model:
            final_content = f"[{timestamp}] {model}：\n{full_reply}\n\n[耗时：{time_cost:.2f}秒]"
        else:
            # 使用解析器处理（针对 deepseek 等有 <think> 标签的模型）
            parser.finalize()
            thought_content = parser.current_thought
            answer_content = parser.current_answer

            # 如果没有捕获到回答，则尝试从原始回复中提取（fallback）
            if not answer_content and full_reply:
                answer_content = full_reply

            final_content = f"[{timestamp}] {model}："
            if thought_content and thought_content.strip():
                thought_html = format_thoughts_with_collapsible(thought_content)
                final_content += f"\n\n{thought_html}\n\n"
            if answer_content and answer_content.strip():
                final_content += answer_content
            else:
                final_content += full_reply if full_reply else "（模型未生成有效回复）"
            final_content += f"\n\n[耗时：{time_cost:.2f}秒]"

        updated_history[-1] = {"role": "assistant", "content": final_content}
        # 保存记忆
        memory_manager.add_memory(message, full_reply)
        yield updated_history, f"生成完成，耗时：{time_cost:.2f}秒"

    except requests.exceptions.ConnectionError:
        current_streaming = False
        updated_history[-1] = {"role": "assistant", "content": f"[{timestamp}] {model}：连接失败：请确保已运行 ollama serve"}
        yield updated_history, "连接失败"
    except Exception as e:
        current_streaming = False
        updated_history[-1] = {"role": "assistant", "content": f"[{timestamp}] {model}：错误：{str(e)}"}
        yield updated_history, f"错误：{str(e)}"

def stop_generation():
    global stop_flag
    stop_flag = True
    return "正在停止生成..."

def clear_all():
    memory_manager.clear_memory()
    initial_history = [{
        "role": "assistant",
        "content": """AI本地小助手

使用指南：
1. 编程/技术问题 -> 选择 **deepseek-r1-8b-q5**（深度推理）
2. 通用任务/创意/分析 -> 选择 **qwen3.5:9b**（支持图片识别！）
3. 轻量/智能体应用 -> 选择 **qwen3.5:4b**（通用/多模态）
4. 翻译任务 -> 选择 **translategemma:4b**（自动添加翻译指令）
5. 不确定时 -> 可以多个模型对比答案

开始对话："""
    }]
    return initial_history, "对话历史和记忆已清空"

def check_ollama_status():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return "Ollama服务运行正常✅ " if response.status_code == 200 else "Ollama服务异常❌"
    except:
        return "Ollama服务未启动"

# ---------- 构建界面 ----------
logo_path = os.path.join(SCRIPT_DIR, "ai_logo.png")
ico_path = os.path.join(SCRIPT_DIR, "ai_logo.ico")

with gr.Blocks(title="轻舟 AI・LightShip AI") as demo:
    # 顶部 Logo 和标题
    with gr.Row():
        if os.path.exists(logo_path):
            gr.Image(logo_path, height=50, show_label=False, container=False, scale=0)
        with gr.Column(scale=1):
            gr.Markdown("""
            # 轻舟 AI・LightShip AI  
            ###### 轻舟渡万境，一智载千灵。 One Ship, All Souls. One AI, All Minds.
            """)

    with gr.Tabs():
        # ---------- Tab1: 聊天 ----------
        with gr.Tab("聊天"):
            with gr.Row():
                # 左侧主区域
                with gr.Column(scale=4):
                    history_box = gr.Chatbot(
                        value=[{
                            "role": "assistant",
                            "content": """AI本地小助手

使用指南：
1. 编程/技术问题 -> 选择 **deepseek-r1-8b-q5**（深度推理）
2. 通用任务/创意/分析 -> 选择 **qwen3.5:9b**（支持图片识别！）
3. 轻量/智能体应用 -> 选择 **qwen3.5:4b**（通用/多模态）
4. 翻译任务 -> 选择 **translategemma:4b**（自动添加翻译指令）
5. 不确定时 -> 可以多个模型对比答案

开始对话："""
                        }],
                        height=900,
                        sanitize_html=False
                    )
                    with gr.Row():
                        input_box = gr.Textbox(
                            label="输入文字",
                            placeholder="请输入问题... (按回车发送)",
                            lines=3,
                            scale=4
                        )
                        send_btn = gr.Button("发送", variant="primary", scale=1)
                        stop_btn = gr.Button("停止", variant="stop", scale=1)

                # 右侧边栏
                with gr.Column(scale=1, min_width=250):
                    gr.Markdown("### 模型设置")
                    model_select = gr.Dropdown(
                        choices=AVAILABLE_MODELS,
                        value=AVAILABLE_MODELS[0][1],
                        label="选择模型"
                    )
                    temp_slider = gr.Slider(0.1, 2.0, value=0.5, step=0.1, label="温度")
                    token_slider = gr.Slider(100, 8192, value=2048, step=100, label="最大长度")
                    gr.Markdown("---")
                    gr.Markdown("### 图片上传")
                    image_input = gr.Image(
                        label="仅多模态模型支持识别",
                        type="filepath",
                        height=180
                    )
                    gr.Markdown("---")
                    check_btn = gr.Button("检查服务", variant="secondary")
                    clear_btn = gr.Button("清空对话", variant="secondary")
                    status_box = gr.Textbox(label="状态", value="就绪", interactive=False)

            # 聊天事件绑定
            send_btn.click(
                fn=stream_response,
                inputs=[input_box, image_input, model_select, temp_slider, token_slider, history_box],
                outputs=[history_box, status_box]
            ).then(lambda: ("", None), None, [input_box, image_input])

            input_box.submit(
                fn=stream_response,
                inputs=[input_box, image_input, model_select, temp_slider, token_slider, history_box],
                outputs=[history_box, status_box]
            ).then(lambda: ("", None), None, [input_box, image_input])

            stop_btn.click(fn=stop_generation, outputs=[status_box])
            clear_btn.click(fn=clear_all, outputs=[history_box, status_box])
            check_btn.click(fn=check_ollama_status, outputs=[status_box])
            demo.load(fn=check_ollama_status, outputs=[status_box])

        # ---------- Tab2: 在线AI入口 ----------
        with gr.Tab("在线AI入口"):
            with gr.Column():
                gr.Markdown("### 快速入口")
                gr.Markdown("点击下方按钮，浏览器将自动打开对应网站。")
                with gr.Row(equal_height=True):
                    btn_deepl = gr.Button("DeepL", variant="secondary", scale=1, min_width=120)
                    btn_youdao = gr.Button("有道翻译", variant="secondary", scale=1, min_width=120)
                    btn_deepseek = gr.Button("DeepSeek", variant="secondary", scale=1, min_width=120)
                    btn_doubao = gr.Button("豆包", variant="secondary", scale=1, min_width=120)
                with gr.Row(equal_height=True):
                    btn_qianwen = gr.Button("通义千问", variant="secondary", scale=1, min_width=120)
                    btn_kimi = gr.Button("Kimi", variant="secondary", scale=1, min_width=120)
                    btn_chatglm = gr.Button("ChatGLM", variant="secondary", scale=1, min_width=120)
                    btn_yuanbao = gr.Button("腾讯元宝", variant="secondary", scale=1, min_width=120)
                status_trans = gr.Textbox(label="", value="等待操作...", interactive=False)

                gr.Markdown("---")
                gr.Markdown("### 提示词模板")
                gr.Markdown("选择模板后复制，然后到上方「快速入口」打开网站粘贴使用。")
                with gr.Row():
                    prompt_selector = gr.Dropdown(
                        label="选择提示词类型",
                        choices=list(PROMPTS.keys()),
                        value="SRT字幕翻译(保留时间码)",
                        scale=2
                    )
                    gr.Column(scale=1)
                prompt_display = gr.Textbox(
                    label="提示词内容 (可直接编辑，点击右上角按钮复制)",
                    value=PROMPTS["SRT字幕翻译(保留时间码)"],
                    lines=10,
                    interactive=True,
                )
                gr.Markdown("💡 **使用方法**：选择模板 → 复制提示词 → 点击上方按钮打开网站 → 粘贴使用。")

                # 按钮事件
                btn_deepl.click(fn=lambda: open_url(URLS["DeepL"]), outputs=status_trans)
                btn_youdao.click(fn=lambda: open_url(URLS["有道翻译"]), outputs=status_trans)
                btn_deepseek.click(fn=lambda: open_url(URLS["DeepSeek"]), outputs=status_trans)
                btn_doubao.click(fn=lambda: open_url(URLS["豆包"]), outputs=status_trans)
                btn_qianwen.click(fn=lambda: open_url(URLS["通义千问"]), outputs=status_trans)
                btn_kimi.click(fn=lambda: open_url(URLS["Kimi"]), outputs=status_trans)
                btn_chatglm.click(fn=lambda: open_url(URLS["ChatGLM"]), outputs=status_trans)
                btn_yuanbao.click(fn=lambda: open_url(URLS["腾讯元宝"]), outputs=status_trans)

                prompt_selector.change(fn=update_prompt, inputs=[prompt_selector], outputs=[prompt_display])

    # ---------- 页脚 ----------
    gr.Markdown("---")
    gr.HTML("""
    <div class="notice">
        注意事项：<br>
        • 本工具仅用于个人学习与视频剪辑使用<br>
        • 禁止用于商业用途及侵权行为<br>            
        • 使用前确保模型与依赖环境正常配置
    </div>
    <div style="text-align: center; color: #666; font-size: 0.9em;">
        <p>本软件包不提供任何模型文件，模型由用户自行从官方渠道获取。用户需自行遵守模型的原许可证。</p>
        <p>本软件包按“原样”提供，不提供任何明示或暗示的担保。使用本软件所产生的一切风险由用户自行承担。</p>
        <p>本软件包开发者不对因使用本软件而导致的任何直接或间接损失负责。</p> 
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin: 15px auto; max-width: 600px;">
            <p style="color: white; font-weight: bold; margin: 5px 0; font-size: 1em;">🎬 更新请关注B站up主：光影的故事2018</p>
            <p style="color: white; margin: 5px 0; font-size: 0.9em;">
                🔗 <strong>B站主页</strong>: <a href="https://space.bilibili.com/381518712" target="_blank" style="color: #ffdd40; text-decoration: none; font-weight: bold;">
                    space.bilibili.com/381518712
                </a>
            </p>
        </div>
    </div>
    <div style="text-align: center; color: #666; margin-top: 10px; font-size: 0.9em;">
        © 原创 WebUI 代码 © 2026 光影紐扣 版权所有  |  轻舟渡万境，一智载千灵。 One Ship, All Souls. One AI, All Minds.
    </div>
    """)

# ---------- 启动 ----------
if __name__ == "__main__":
    print("=" * 60)
    print("启动 轻舟 AI・LightShip AI WebUI）")
    print("可用模型：")
    for display, value in AVAILABLE_MODELS:
        print(f"  - {display} (值: {value})")
    print("=" * 60)    
    print("=" * 60)
    print("⚠️ 请确保已启动 Ollama 服务")
    print("=" * 60)

    ports_to_try = [7863, 7961, 7861, 7862, 7960]
    for port in ports_to_try:
        try:
            demo.launch(
                server_name="127.0.0.1",
                server_port=port,
                share=False,
                inbrowser=True,
                theme=gr.themes.Default(),
                favicon_path=ico_path if os.path.exists(ico_path) else None
            )
            break
        except OSError as e:
            if "Address already in use" in str(e) or "端口" in str(e):
                print(f"端口 {port} 被占用，尝试下一个...")
                continue
            else:
                raise e
    else:
        print("所有尝试的端口均被占用，请手动指定空闲端口。")