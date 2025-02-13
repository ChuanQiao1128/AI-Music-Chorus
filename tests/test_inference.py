# test_inference.py
import pytest
import os
from src.inference import detect_chorus


def test_detect_chorus():
    # 假设在 tests/ 下有一个测试用音频 test_sample.mp3
    audio_path = os.path.join("tests", "test_sample.mp3")

    # 如果没有这个文件，你可以mock或者跳过
    if not os.path.exists(audio_path):
        pytest.skip("测试音频文件不存在，跳过测试。")

    segments = detect_chorus(audio_path)
    # 检查是否返回了段落信息
    assert isinstance(segments, list), "detect_chorus 应该返回一个列表"
    # 进一步断言可根据业务场景判断
    # 例如 segments不为空
    # assert len(segments) > 0, "期望至少检测到一个副歌段落"