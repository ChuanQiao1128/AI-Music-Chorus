# src/utils/feature_extract.py

import librosa
import numpy as np

def extract_advanced_features(y, sr, n_mfcc=13):
    """
    提取多个特征:
      - MFCC (13维)
      - Delta MFCC(13维)
      - Chroma(12维)
    => 拼成 38维
    """
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)  # (13, t)
    mfcc_delta = librosa.feature.delta(mfcc)               # (13, t)
    mfcc_mean = mfcc.mean(axis=1)                          # (13,)
    mfcc_delta_mean = mfcc_delta.mean(axis=1)              # (13,)

    chroma = librosa.feature.chroma_stft(y=y, sr=sr)       # (12, t)
    chroma_mean = chroma.mean(axis=1)                      # (12,)

    feats_38 = np.concatenate([mfcc_mean, mfcc_delta_mean, chroma_mean], axis=0)
    return feats_38  # shape (38,)

def _combine_context_features(feature_seq, i, context=1):
    """
    把 feature_seq[i-context : i+context+1] 的 38维 各帧拼接 => (38*(2*context+1),).
    若越界 => 用 0 向量填充
    """
    base_dim = len(feature_seq[0])  # 38
    out_vecs = []
    for offset in range(-context, context+1):
        idx_c = i+offset
        if idx_c<0 or idx_c>= len(feature_seq):
            out_vecs.append(np.zeros(base_dim, dtype=np.float32))
        else:
            out_vecs.append(feature_seq[idx_c])
    return np.concatenate(out_vecs, axis=0)  # (38*(2*context+1),)= (114,) if context=1

def extract_features_advanced_context(y, sr, frame_size=2.0, context=1):
    """
    1) 分帧(每帧 frame_size 秒),
    2) 对每帧提取 38维 (mfcc+delta+chroma),
    3) 再用前后各 context 帧拼成 114维 => (2*context+1)*38
    返回 feats_seq: list of shape(114,),
          time_seq: 每帧起始时间(秒)
    """
    features_seq = []
    time_seq     = []

    samples_per_frame = int(frame_size*sr)
    total_len = len(y)

    i=0
    current_t= 0.0
    while True:
        start_samp = i*samples_per_frame
        end_samp   = (i+1)*samples_per_frame
        if start_samp>= total_len:
            break
        segment = y[start_samp:end_samp]
        feats_38 = extract_advanced_features(segment, sr)
        features_seq.append(feats_38)
        time_seq.append(current_t)

        current_t+= frame_size
        i+=1

    # 做 context 拼帧 => (114,) if context=1
    final_feats_seq= []
    for idx_frame in range(len(features_seq)):
        combined = _combine_context_features(features_seq, idx_frame, context=context)
        final_feats_seq.append(combined)

    return final_feats_seq, time_seq