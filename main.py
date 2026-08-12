"""本地/开发入口(兼容 systemd `uvicorn main:app` 与 `python main.py`)。
生产安装请: pip install tmux-ai-coder-panel && tmux-ai-coder-panel
"""
from tmux_ai_coder_panel import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10015, reload=True)
