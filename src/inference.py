import torch
import librosa
import numpy as np

from src.config import AUDIO_SAMPLE_RATE, MODEL_PATH
from src.utils.feature_extract import extract_features
from src.model import ChorusMLP

# 1. 定义并加载模型
model = ChorusMLP(input_dim=13, hidden_size=16, output_dim=2)
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()


def detect_chorus(
        audio_file_path,
        frame_size=1.0,
        min_chorus_len=5.0,
        max_chorus_len=None,
        merge_gap=3.0
):
    """
    对给定音频文件进行副歌检测，返回一个[(chorus_start, chorus_end), ...]列表.

    主要优化逻辑:
      1. 每帧做二分类 (0 or 1)，若全为0则插入一个伪副歌.
      2. 副歌段长度若低于 min_chorus_len 则丢弃.
      3. 如果 max_chorus_len 不为 None, 超过则截断/限制.
      4. 支持合并相邻副歌段(间隔< merge_gap 秒).

    :param audio_file_path: mp3/wav文件路径
    :param frame_size: 每帧长度(秒), 默认1.0 => 1秒一帧
    :param min_chorus_len: 副歌段的最短阈值(秒). 如果小于此长度则认为无效
    :param max_chorus_len: 副歌段的最大长度(秒). 如果不为None则超出时截断
    :param merge_gap: 若两个副歌段之间空隙< merge_gap, 则合并
    :return: 副歌区间列表 [ (start_sec, end_sec), ... ]
    """
    # 1. 读取音频 & 提取特征
    y, sr = librosa.load(audio_file_path, sr=AUDIO_SAMPLE_RATE)
    segments_features = extract_features(y, sr, frame_size=frame_size)

    label_sequence = []
    time_sequence = []
    current_time = 0.0

    # 2. 模型推理（对每帧做二分类）
    for feat in segments_features:
        input_tensor = torch.tensor(feat, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            output = model(input_tensor)  # shape: (1,2)
            pred_label = torch.argmax(output, dim=1).item()  # 0 or 1
        label_sequence.append(pred_label)
        time_sequence.append(current_time)
        current_time += frame_size

    total_time = current_time

    # 3. 若全为0，插入伪副歌
    if all(lbl == 0 for lbl in label_sequence):
        print(f"[detect_chorus] 预测结果全是0, 人为插入伪副歌. total_time={total_time:.1f}s")
        label_sequence = [0] * len(label_sequence)
        # 示例: 如果 >= 90s => 插入[60,90], 否则插入[10, 50]
        if total_time >= 90:
            start_fake, end_fake = 60.0, 90.0
        else:
            start_fake, end_fake = 10.0, min(10.0 + 40.0, total_time)

        # 对应帧设为1
        start_idx = int(start_fake / frame_size)
        end_idx = int(end_fake / frame_size)
        for i in range(start_idx, min(end_idx, len(label_sequence))):
            label_sequence[i] = 1

    # 4. 合并连续为1的帧 => (start_sec, end_sec)
    raw_segments = []
    start = None
    for i, lbl in enumerate(label_sequence):
        if lbl == 1 and start is None:
            start = time_sequence[i]
        elif lbl == 0 and start is not None:
            end = time_sequence[i]
            raw_segments.append((start, end))
            start = None
    # 若结尾仍在副歌
    if start is not None:
        raw_segments.append((start, total_time))

    # 5. 过滤过短段/截断过长段
    filtered_segments = []
    for (s, e) in raw_segments:
        dur = e - s
        if dur < min_chorus_len:
            continue
        if max_chorus_len is not None and dur > max_chorus_len:
            e = s + max_chorus_len
        filtered_segments.append((s, e))

    # 6. 合并相邻段(若间隔< merge_gap)
    merged_segments = []
    if not filtered_segments:
        return merged_segments
    # 先按照起始时间排序
    filtered_segments.sort(key=lambda seg: seg[0])
    curr_start, curr_end = filtered_segments[0]
    for i in range(1, len(filtered_segments)):
        nxt_start, nxt_end = filtered_segments[i]
        # 若下一个段的开始 与 当前段的结束 之间的间隔 < merge_gap => 合并
        if nxt_start - curr_end <= merge_gap:
            # 合并 => 取更大的end
            curr_end = max(curr_end, nxt_end)
        else:
            # 不合并,先把前一个放进数组,再更新
            merged_segments.append((curr_start, curr_end))
            curr_start, curr_end = nxt_start, nxt_end
    # 把最后一段放进
    merged_segments.append((curr_start, curr_end))

    return merged_segments