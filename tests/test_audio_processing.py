import pytest
import os
import sys
from pydub import AudioSegment

# 保证能找到 src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.audio_processing import (
    extract_audio_segment,
    merge_audio_segments,
    extract_chorus
)

def test_extract_audio_segment():
    test_file = "tests/test_sample.mp3"
    if not os.path.exists(test_file):
        pytest.skip("测试音频文件不存在，跳过测试。")

    out_file = "tests/test_segment.mp3"
    extract_audio_segment(test_file, 0, 5, out_file)
    assert os.path.exists(out_file), "没有生成切割文件"
    os.remove(out_file)

def test_merge_audio_segments():
    seg1 = AudioSegment.silent(duration=1000)  # 1s静音
    seg2 = AudioSegment.silent(duration=2000)  # 2s静音
    out_file = "tests/merged_test.mp3"
    merge_audio_segments([seg1, seg2], out_file)
    assert os.path.exists(out_file), "没有生成合并文件"
    os.remove(out_file)

def test_extract_chorus():
    test_file = "tests/test_sample.mp3"
    if not os.path.exists(test_file):
        pytest.skip("测试音频文件不存在，跳过测试。")

    out_file = "tests/test_chorus.mp3"
    result_path = extract_chorus(test_file, out_file)

    assert os.path.exists(out_file), "副歌提取文件未生成"

    chorus_audio = AudioSegment.from_file(out_file)
    assert len(chorus_audio) > 0, "提取的副歌时长为0"

    # 如需清理可取消注释
    # os.remove(out_file)