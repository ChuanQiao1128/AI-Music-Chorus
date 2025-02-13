# 使用官方python基础镜像
FROM python:3.9-slim

# 安装ffmpeg等必要包（pydub/ffmpeg 可能需要）
RUN apt-get update && apt-get install -y ffmpeg

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt /app/requirements.txt

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目
COPY . /app

# 暴露端口（假设后端运行在8000端口）
EXPOSE 8000

# 启动命令，可以使用 uvicorn 或 python main.py
CMD ["python", "src/main.py"]