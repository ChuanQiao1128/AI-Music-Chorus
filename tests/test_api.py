# test_api.py
"""
对后端API进行集成测试，可使用 requests 或 httpx
"""
import pytest
import os
import requests
import subprocess
import time

# 如果你用 uvicorn 启动服务，需要先启动再测试
# 也可以使用TestClient (FastAPI内置) 做本地测试

def test_api_chorus_segments():
    # 假设后端运行在 localhost:8000
    url = "http://127.0.0.1:8000/song/segments"
    test_file = os.path.abspath("tests/test_sample.mp3")
    if not os.path.exists(test_file):
        pytest.skip("测试音频文件不存在")

    with open(test_file, "rb") as f:
        files = {"audio": f}
        r = requests.post(url, files=files)
    assert r.status_code == 200, f"API请求失败, status_code={r.status_code}"
    data = r.json()
    assert "chorus_segments" in data, "返回结果中应包含 chorus_segments 字段"