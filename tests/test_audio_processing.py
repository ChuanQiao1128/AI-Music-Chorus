# audio_processing.py
import logging
import os
from pydub import AudioSegment
from src.inference import detect_chorus, ChorusSegment
from src.audio_processing import load_audio  # 如果你需要加载文件

def extract_chorus_list_and_merge(song_list, output_file="mega_chorus.mp3"):
    """
    对 song_list 中的每首歌:
      1) 检测副歌
      2) 打印/记录该首歌的副歌区间
      3) 拼接到 merged
    最后导出到 output_file, 并打印合并后的大小/时长
    """
    merged = AudioSegment.empty()
    for idx, song_file in enumerate(song_list):
        logging.info(f"[extract_chorus_list_and_merge] Processing Song #{idx+1}: {song_file}")

        # 1) 加载音频 => audio_data, sr
        audio_data, sr = load_audio(song_file)
        # 2) detect_chorus => ChorusSegment
        segment: ChorusSegment = detect_chorus(audio_data, sr)
        dur = segment.duration
        fallback_str = " (fallback)" if segment.is_fallback else ""
        conf_str = f"{segment.confidence:.2f}" if segment.confidence is not None else "N/A"

        logging.info(f"[Song#{idx+1}] {song_file} => start={segment.start:.2f}s, end={segment.end:.2f}s, "
                     f"duration={dur:.2f}s, conf={conf_str}{fallback_str}")

        # 用pydub再从文件中裁剪(如果你想精确操作, 需再 load_audio => pydubAudioSegment)
        whole_audio = AudioSegment.from_file(song_file)
        start_ms = int(segment.start * 1000)
        end_ms = int(segment.end * 1000)
        chorus_part = whole_audio[start_ms:end_ms]

        # 3) 拼到 merged
        if len(chorus_part) > 0:
            merged += chorus_part
        else:
            logging.warning(f"[Song#{idx+1}] Empty chorus segment from {song_file}?")

    # 4) 导出合并结果
    merged.export(output_file, format="mp3")
    merged_dur_sec = len(merged) / 1000.0
    file_size = os.path.getsize(output_file) if os.path.exists(output_file) else 0
    logging.info(f"[extract_chorus_list_and_merge] Merged => {output_file}, duration={merged_dur_sec:.2f}s, size={file_size} bytes")

    return output_file