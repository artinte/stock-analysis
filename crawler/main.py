import os
import asyncio

from content_fetch import fetch_mofcom_news_like_human
from data_generate import generate_xueqiu_article


# ==================== 主运行逻辑 ====================
async def main():
    mofcom_news = await fetch_mofcom_news_like_human()
    
    if mofcom_news:
        xueqiu_post = generate_xueqiu_article(mofcom_news)
        
        if xueqiu_post:
            print("\n" + "🔥" * 10 + " 本地 AI 生成的雪球深度分析长文 " + "🔥" * 10 + "\n")
            print(xueqiu_post)
            print("\n" + "=" * 50)
            
            output_filename = "xueqiu_local_output.txt"
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, output_filename)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xueqiu_post)
            print(f"🎉 本地实验大成功！文章已完美保存至本地：{output_file}")
    else:
        print("❌ 实验未能完成：未能从官网捕获到有效政策标题。")

if __name__ == "__main__":
    asyncio.run(main())