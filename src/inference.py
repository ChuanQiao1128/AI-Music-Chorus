"""
inference.py
------------
核心: detect_chorus(...) => 若无满足threshold的重复段 => fallback => get_high_energy_segment
"""

import numpy as np
import logging
import librosa
from dataclasses import dataclass
from typing import Optional

from src.audio_processing import get_high_energy_segment

@dataclass
class ChorusSegment:
    start: float
    end: float
    confidence: Optional[float]= None
    is_fallback: bool= False

    @property
    def duration(self)->float:
        return self.end- self.start

def detect_chorus(
    audio_data: np.ndarray,
    sr: int,
    min_duration: float=15.0,
    max_duration: float=30.0,
    threshold: float=0.7
)-> ChorusSegment:
    """
    检测副歌, 若找不到重复段则fallback => get_high_energy_segment
    """

    if min_duration< 15.0:
        logging.warning(f"Given min_duration={min_duration}, forcing to 15.0")
        min_duration= 15.0
    if max_duration< min_duration:
        max_duration= min_duration

    total_duration= len(audio_data)/ sr if len(audio_data)>0 else 0.0
    if total_duration<=0:
        raise ValueError("audio_data is empty.")

    # 若音频 <= max_duration => 整首 fallback
    if total_duration<= max_duration:
        logging.info(f"Short track {total_duration:.2f}s <= {max_duration:.2f}, entire track as chorus.")
        return ChorusSegment(0.0, total_duration, None, True)

    # 计算 chroma => 找重复(如cosine相似)
    try:
        hop_length= 1024
        chroma= librosa.feature.chroma_stft(y=audio_data, sr=sr, hop_length=hop_length)
    except Exception as e:
        logging.error(f"Failed to compute chroma: {e}, fallback => high energy.")
        # fallback
        if total_duration> min_duration:
            s= get_high_energy_segment(audio_data, sr, min_duration)
        else:
            s=0.0
        e= min(s+ min_duration, total_duration)
        return ChorusSegment(s,e,None, True)

    num_frames= chroma.shape[1]
    frames_per_sec= sr/ float(hop_length)
    min_frames= int(min_duration* frames_per_sec)
    if min_frames<1:
        min_frames=1

    best_sim= 0.0
    best_i= 0
    best_j= 0

    step_frames= int(frames_per_sec) #1秒粒度
    for i in range(0, num_frames- min_frames+1, step_frames):
        seg_i= chroma[:, i:i+min_frames]
        if seg_i.shape[1]< min_frames:
            continue
        vec_i= seg_i.flatten()
        norm_i= np.linalg.norm(vec_i)
        if norm_i==0:
            continue
        for j in range(i+ min_frames, num_frames- min_frames+1, step_frames):
            seg_j= chroma[:, j:j+ min_frames]
            if seg_j.shape[1]< min_frames:
                continue
            vec_j= seg_j.flatten()
            norm_j= np.linalg.norm(vec_j)
            if norm_j==0:
                continue
            sim= np.dot(vec_i, vec_j)/(norm_i*norm_j)
            if sim> best_sim:
                best_sim= sim
                best_i= i
                best_j= j
                logging.debug(f"Found new best sim={best_sim:.3f}, i={i}, j={j}")
                if best_sim>=0.9999:
                    break
        if best_sim>=0.9999:
            break

    if best_sim>= threshold:
        # 找到重复
        frame_dur=1.0/ frames_per_sec
        seg_start= best_i* frame_dur
        seg_end  = seg_start+ min_duration
        seg_len  = seg_end- seg_start
        if seg_len> max_duration:
            seg_end= seg_start+ max_duration
            seg_len= max_duration
        logging.info(f"Chorus detected (repeated segment) conf={best_sim:.3f}")
        return ChorusSegment(seg_start, seg_end, best_sim, False)
    else:
        # fallback
        logging.info(f"No repeated segment above threshold={threshold:.3f}, fallback => high energy")
        s= get_high_energy_segment(audio_data, sr, min_duration)
        e= s+ min_duration
        if e> total_duration:
            e= total_duration
        return ChorusSegment(s,e,None, True)