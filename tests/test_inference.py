# tests/test_inference.py

import pytest
import os
from src.inference import detect_chorus

def test_detect_chorus():
    test_file= "tests/songList/test_sample_02.mp3"
    if not os.path.exists(test_file):
        pytest.skip(f"{test_file} 不存在, 跳过测试.")
    segments= detect_chorus(test_file)
    print("detect_chorus =>", segments)

    assert isinstance(segments, list), "detect_chorus 应返回 list"
    # 你可视情况断言更多, e.g. >=1
    # assert len(segments)>0, "期望至少检测到1个副歌区段"