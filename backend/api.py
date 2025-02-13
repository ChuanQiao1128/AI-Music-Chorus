# api.py

from fastapi import FastAPI, File, UploadFile
from src.inference import detect_chorus
import os
import uuid

app = FastAPI()

@app.post("/song/segments")
async def get_song_segments(audio: UploadFile = File(...)):
    """
    接收上传的音频文件，调用 detect_chorus 获取副歌区间，并返回
    """
    # 将上传文件暂存
    temp_filename = f"temp_{uuid.uuid4()}.mp3"
    with open(temp_filename, "wb") as f:
        f.write(await audio.read())

    # 调用副歌检测
    segments = detect_chorus(temp_filename)

    # 删除临时文件
    os.remove(temp_filename)

    return {"chorus_segments": segments}