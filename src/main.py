# main.py
"""
作为项目的入口脚本，可直接运行该文件来启动后端服务，或执行批处理任务等。
"""
from src.audio_processing import extract_chorus

def main():
    input_mp3 = "my_song.mp3"   # 你的一首歌
    output_mp3 = "my_song_chorus.mp3"

    # 只想要一首歌的副歌
    result = extract_chorus(input_mp3, output_mp3)
    if isinstance(result, str):
        print(f"副歌已保存到 => {result}")
    else:
        print("未生成文件, 可能没有检测到副歌")

if __name__ == "__main__":
    main()