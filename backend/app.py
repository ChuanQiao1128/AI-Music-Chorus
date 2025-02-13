# app.py
"""
启动FastAPI服务的入口。如果你想用 uvicorn 命令行，也可以不用本文件。
"""

import uvicorn
from backend.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)