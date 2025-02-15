"""
audio_processing.py
-------------------
提供音频处理的实用函数:
  - load_audio: 加载音频文件 => (np.ndarray, sr)
  - save_audio_segment: 将 [start,end] 秒的音频写入文件
  - get_high_energy_segment: 返回长为 segment_duration (秒) 的音频里能量最大的起始时间

被 test_save_audio_segment、inference.py 等调用
"""

import os
import logging
import librosa
import numpy as np
import soundfile as sf

def load_audio(file_path: str, sr: int=22050):
    """
    加载音频文件(支持常见格式: WAV, MP3等), 返回: (audio_data, sample_rate)
    audio_data 为 单声道 np.float32 array
    sr 为采样率
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    try:
        # mono=True => librosa会自动混合到单声道
        audio_data, sample_rate = librosa.load(file_path, sr=sr, mono=True)
        logging.debug(f"Loaded audio: {file_path}, sr={sample_rate}, length={len(audio_data)/sample_rate:.2f}s")
        return audio_data, sample_rate
    except Exception as e:
        logging.error(f"Failed to load audio '{file_path}': {e}")
        raise ValueError(f"Could not load audio file: {e}")

def save_audio_segment(audio_data: np.ndarray, sr: int,
                       start_time: float, end_time: float,
                       output_file: str):
    """
    将 audio_data 数组里 [start_time, end_time] 的片段写到 output_file (WAV等格式).
    这里示例写成 WAV, 你也可用 soundfile 写 FLAC, etc.

    :param audio_data: shape=(samples,) 的np数组
    :param sr: 采样率
    :param start_time: 片段开始(秒)
    :param end_time: 片段结束(秒)
    :param output_file: 输出文件路径(如 .wav)
    """
    if start_time<0 or end_time<= start_time:
        raise ValueError(f"Invalid start/end time: {start_time}~{end_time}")
    total_sec= len(audio_data)/ sr
    if start_time >= total_sec:
        raise ValueError("start_time >= total audio duration, no segment to save.")
    # clamp
    end_time= min(end_time, total_sec)
    start_idx= int(start_time * sr)
    end_idx= int(end_time   * sr)
    segment= audio_data[start_idx:end_idx]

    try:
        sf.write(output_file, segment, sr, subtype='PCM_16')
        logging.info(f"Saved audio segment => {output_file}, duration={end_time-start_time:.2f}s")
    except Exception as e:
        logging.error(f"Failed saving segment to {output_file}: {e}")
        raise

def get_high_energy_segment(audio_data: np.ndarray, sr: int,
                            segment_duration: float=15.0) -> float:
    """
    返回音频中长度= segment_duration (秒) 的「能量最高」窗口的起始时间(秒).
    如果音频长 < segment_duration, 返回0.0
    """
    total_len= len(audio_data)/ sr
    if total_len<= segment_duration:
        return 0.0
    seg_samples= int(segment_duration * sr)
    # 计算能量(平方和)
    squared= audio_data**2
    cumsum= np.concatenate(([0.0], np.cumsum(squared)))
    best_energy= -1.0
    best_start_smpl= 0
    step= sr  # 1秒步长
    max_start= len(audio_data)- seg_samples
    for start_smpl in range(0, max_start+1, step):
        end_smpl= start_smpl+ seg_samples
        energy= cumsum[end_smpl]- cumsum[start_smpl]
        if energy> best_energy:
            best_energy= energy
            best_start_smpl= start_smpl
    return best_start_smpl/ sr