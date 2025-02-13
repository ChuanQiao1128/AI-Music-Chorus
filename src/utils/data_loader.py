# data_loader.py
"""
提供加载数据或元信息的工具类，例如从CSV读取音频文件路径、标签等
"""

import os
import pandas as pd

def load_metadata(csv_path):
    """
    从csv文件中读取元数据，返回DataFrame
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} 不存在")
    return pd.read_csv(csv_path)

def get_audio_files(data_dir):
    """
    返回 data_dir 下所有音频文件的路径列表
    """
    all_files = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith((".mp3", ".wav")):
            all_files.append(os.path.join(data_dir, fname))
    return all_files