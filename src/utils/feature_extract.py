# feature_extract.py
"""
音频特征提取的工具函数
"""
import librosa
import numpy as np

def extract_features(y, sr, frame_size=2.0):
    """
    将音频 y 分成若干 frame_size 秒的窗口，
    对每个窗口提取例如 MFCC(取mean)等特征
    返回: [ [特征向量], [特征向量], ... ]
    """
    hop_length = int(frame_size * sr)
    total_len = len(y)
    features_list = []

    start = 0
    while start < total_len:
        end = min(start + hop_length, total_len)
        y_frame = y[start:end]
        if len(y_frame) == 0:
            break
        mfcc = librosa.feature.mfcc(y=y_frame, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        features_list.append(mfcc_mean)
        start += hop_length

    return features_list