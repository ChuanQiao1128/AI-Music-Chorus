from pydub import AudioSegment
from src.inference import detect_chorus

def extract_audio_segment(input_file, start_time, end_time, output_file=None):
    """
    从 input_file 中提取 [start_time, end_time] (秒) 的片段.
    可导出到 output_file (mp3)
    """
    audio = AudioSegment.from_file(input_file)
    excerpt = audio[start_time * 1000 : end_time * 1000]  # 毫秒切片
    if output_file:
        excerpt.export(output_file, format="mp3")
        return output_file
    else:
        return excerpt

def merge_audio_segments(segments, output_file="merged.mp3"):
    """
    合并多个 AudioSegment 并导出mp3
    """
    merged = AudioSegment.empty()
    for seg in segments:
        merged += seg
    merged.export(output_file, format="mp3")
    return output_file

def extract_chorus(input_file, output_file=None):
    """
    只提取该歌曲第一段副歌。
    """
    chorus_segments = detect_chorus(input_file)
    if not chorus_segments:
        print("未检测到副歌段落，返回空AudioSegment")
        return AudioSegment.empty()

    # 只要第一段
    (start_sec, end_sec) = chorus_segments[0]
    print(f"[extract_chorus] 第1段副歌 => {start_sec:.1f}s ~ {end_sec:.1f}s")

    audio = AudioSegment.from_file(input_file)
    final_chorus = audio[start_sec*1000 : end_sec*1000]

    if output_file:
        final_chorus.export(output_file, format="mp3")
        return output_file
    else:
        return final_chorus