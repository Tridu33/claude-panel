"""tmux-ai-coder-panel:Claude 键盘控制面板,单端口整体服务(FastAPI + Vue3 + tmux)。"""

__version__ = "1.0.2"

__all__ = ["app", "__version__"]


def __getattr__(name: str):
    """惰性导入 app:避免 import 包即触发 main.py 的模块级副作用。

    cli.py 需要先写 .env 再导入应用模块,使 load_dotenv() 能读到新配置;
    同时 `uvicorn tmux_ai_coder_panel:app` 仍可用(PEP 562 getattr 生效)。
    """
    if name == "app":
        from .main import app
        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
