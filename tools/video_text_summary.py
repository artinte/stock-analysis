import os
import subprocess
import whisper
from openai import OpenAI


# ==============================================================================
# 配置区域（如不使用 AI 总结，仅转文字，可忽略 API 配置）
# ==============================================================================
API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
BASE_URL = "https://api.openai.com/v1" 
LLM_MODEL = "gpt-4o-mini"


def extract_audio_with_ffmpeg(video_path: str, output_audio_path: str = "temp_audio.mp3") -> str:
    """1. 使用 ffmpeg 命令行直接从视频中提取音频"""
    print(f"🎬 1/3 正在使用 ffmpeg 从视频中提取音频...")
    
    # 构建 ffmpeg 命令
    # -i: 输入文件
    # -vn: 禁用视频（只保留音频）
    # -acodec libmp3lame / copy: 音频编码
    # -y: 覆盖同名输出文件
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "mp3",
        "-ar", "16000",  # 设置 16kHz 采样率，非常适合 Whisper 识别
        "-ac", "1",      # 单声道，减小文件体积
        "-y",
        output_audio_path
    ]
    
    try:
        # 执行 ffmpeg 命令，隐藏冗余的 stdout 控制台输出
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"✅ 音频提取成功: {output_audio_path}")
        return output_audio_path
    except FileNotFoundError:
        raise RuntimeError("❌ 未检测到 ffmpeg，请确保系统中已安装 ffmpeg 并已添加至环境变量中！")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ ffmpeg 提取音频失败: {e}")


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """
    2. 使用 Whisper 将音频转为文字
    model_size 可选: 'tiny', 'base', 'small', 'medium', 'large'
    """
    print(f"🎙️ 2/3 正在使用 Whisper ({model_size}) 转录语音为文字...")
    model = whisper.load_model(model_size)
    
    result = model.transcribe(audio_path, fp16=False)
    text = result["text"].strip()
    print("✅ 语音转写完成！")
    return text


def summarize_text(text: str) -> str:
    """3. 调用大语言模型（LLM）对转写文本进行总结"""
    print("🤖 3/3 正在调用 AI 生成文本总结...")
    
    if not API_KEY or API_KEY == "your-api-key-here":
        print("⚠️ 未检测到有效的 API Key，跳过总结步骤，仅输出原始转写文本。")
        return text

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    prompt = f"""
你是一个专业的视频内容总结专家。请阅读以下视频转录出的文本，提供一份结构清晰、条理分明的总结报告。

要求：
1. **一句话总结**：用一句话精炼概括视频的核心主题。
2. **核心要点**：列出 3-5 个关键要点（使用带序号的列表）。
3. **详细总结**：分段或分层次对视频提到的主要内容进行综合提炼。

视频文本内容如下：
---
{text}
---
"""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "你是一个高效、精准的视频内容总结助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ AI 总结出错 ({e})，返回原始转写文本。")
        return text


def process_video_to_text(video_path: str, output_txt_path: str = None, whisper_model: str = "base"):
    """主处理管道"""
    if not os.path.exists(video_path):
        print(f"❌ 错误: 找不到视频文件 '{video_path}'")
        return

    if not output_txt_path:
        base_name = os.path.splitext(video_path)[0]
        output_txt_path = f"{base_name}_summary.md"

    temp_audio = f"temp_{os.getpid()}.mp3"

    try:
        # Step 1: ffmpeg 提取音频
        extract_audio_with_ffmpeg(video_path, temp_audio)

        # Step 2: 音频转文字
        raw_text = transcribe_audio(temp_audio, model_size=whisper_model)

        # 保存原始文本
        raw_txt_path = os.path.splitext(output_txt_path)[0] + "_raw.txt"
        with open(raw_txt_path, "w", encoding="utf-8") as f:
            f.write(raw_text)
        print(f"📝 原始转写文本已存至: {raw_txt_path}")

        # Step 3: AI 总结文本
        final_summary = summarize_text(raw_text)

        # 保存总结结果
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(final_summary)

        print("\n" + "=" * 20 + " 最终结果预览 " + "=" * 20)
        print(final_summary[:500] + ("...\n" if len(final_summary) > 500 else "\n"))
        print("=" * 52)
        print(f"🎉 处理完成！最终文本已保存至: {output_txt_path}")

    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)


if __name__ == "__main__":
    INPUT_VIDEO = "sample.mp4"

    process_video_to_text(
        video_path=INPUT_VIDEO,
        whisper_model="base"  # 中文视频建议改为 'small' 或 'medium'
    )