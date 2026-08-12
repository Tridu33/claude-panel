"""tmux-ai-coder-panel 命令行入口。

  tmux-ai-coder-panel                    # 默认 127.0.0.1:20016,端口被占用自动 +1
  tmux-ai-coder-panel --host 0.0.0.0     # 局域网/公网访问
  PORT=9999 tmux-ai-coder-panel          # 覆盖起始端口
  python -m tmux_ai_coder_panel             # 等价于 tmux-ai-coder-panel
"""

import ipaddress
import os
import secrets
import socket
import sys
from pathlib import Path

import uvicorn

DEFAULT_PORT = 20016
DEFAULT_HOST = "127.0.0.1"
MAX_PORT_ATTEMPTS = 50

USAGE = f"""tmux-ai-coder-panel - Claude 键盘控制面板

用法:
  tmux-ai-coder-panel [--port N] [--host IP] [--help] [--version]

选项:
  --port N       指定起始端口(默认 {DEFAULT_PORT},被占用自动 +1)
  --host IP      监听地址(默认 {DEFAULT_HOST},局域网访问用 0.0.0.0)
  -h, --help     显示本帮助
  --version      显示版本号

环境变量:
  PORT=N         等价于 --port N,用于容器/脚本场景
  HOST=IP        等价于 --host IP

示例:
  tmux-ai-coder-panel                    # 127.0.0.1:20016 起,冲突自动 +1
  tmux-ai-coder-panel --host 0.0.0.0     # 局域网/公网访问
  tmux-ai-coder-panel --port 3000        # 从 3000 起
"""


def _parse_port(raw: str) -> int:
    try:
        return int(raw)
    except ValueError:
        print(f"[警告] 无效端口 {raw!r},使用默认 {DEFAULT_PORT}", file=sys.stderr)
        return DEFAULT_PORT


def _parse_args(argv: list[str]):
    """解析命令行参数,返回 (起始端口, 监听地址);--help/--version 直接退出。"""
    port = None
    host = None
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            print(USAGE, end="")
            raise SystemExit(0)
        if arg == "--version":
            from . import __version__
            print(f"tmux-ai-coder-panel {__version__}")
            raise SystemExit(0)
        if arg.startswith("--port="):
            port = _parse_port(arg.split("=", 1)[1])
            i += 1
            continue
        if arg in ("--port", "-p") and i + 1 < len(argv):
            port = _parse_port(argv[i + 1])
            i += 2
            continue
        if arg.startswith("--host="):
            host = arg.split("=", 1)[1]
            i += 1
            continue
        if arg in ("--host", "-H") and i + 1 < len(argv):
            host = argv[i + 1]
            i += 2
            continue
        print(f"[警告] 未知参数: {arg}", file=sys.stderr)
        print(USAGE, end="", file=sys.stderr)
        raise SystemExit(2)
    return port, host


def _starting_port() -> int:
    """PORT 环境变量覆盖起始端口;非法值回退默认并警告。"""
    raw = os.environ.get("PORT")
    if raw:
        try:
            return int(raw)
        except ValueError:
            print(f"[警告] PORT={raw!r} 不是有效端口,使用默认 {DEFAULT_PORT}", file=sys.stderr)
    return DEFAULT_PORT


def _starting_host() -> str:
    """HOST 环境变量覆盖监听地址;非法值回退默认并警告。"""
    raw = os.environ.get("HOST")
    if raw:
        try:
            ipaddress.ip_address(raw)
            return raw
        except ValueError:
            print(f"[警告] HOST={raw!r} 不是有效 IP,使用默认 {DEFAULT_HOST}", file=sys.stderr)
    return DEFAULT_HOST


def _validate_host(host: str) -> None:
    """校验监听地址,非法 IP 直接退出。"""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        print(f"[错误] 无效监听地址 {host!r},应为 IP(如 127.0.0.1 / 0.0.0.0)", file=sys.stderr)
        raise SystemExit(2)


def find_free_port(start: int) -> int:
    """从 start 开始 bind 探测,占用则 +1,返回首个空闲端口。"""
    for port in range(start, start + MAX_PORT_ATTEMPTS):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("0.0.0.0", port))
            except OSError:
                continue
            return port
    raise RuntimeError(
        f"端口 {start}~{start + MAX_PORT_ATTEMPTS - 1} 全部被占用,请设置 PORT 环境变量后重试"
    )


def ensure_env_file() -> None:
    """首次启动:cwd 无 .env 时生成随机账号密码并打印。

    契约:运行目录 = 配置目录(pip 安装后 .env 不进 site-packages)。
    """
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        return
    account = secrets.token_hex(4)         # 8 位十六进制账号
    password = secrets.token_urlsafe(12)   # ~16 位 URL 安全随机密码
    content = (
        "# Claude Panel 环境变量配置(首次启动自动生成,可编辑后重启生效)\n"
        f"PANEL_ACCOUNT={account}\n"
        f"PANEL_SECERT={password}\n"
    )
    try:
        env_path.write_text(content)
    except OSError as exc:                 # 例如 cwd 只读
        print(f"[警告] 无法写入 {env_path}: {exc}", file=sys.stderr)
        print("[警告] 将以「不启用登录」模式启动,可稍后手动创建 .env 并重启", file=sys.stderr)
        return
    print(f"[首次启动] 已生成配置文件: {env_path}")
    print(f"[首次启动] 账号: {account}")
    print(f"[首次启动] 密码: {password}   (可编辑该文件修改)")


def _print_banner(host: str, port: int) -> None:
    """醒目启动横幅:最终端口 + 访问地址(仅监听 0.0.0.0 时展示局域网地址)。"""
    lines = [f"  本机访问:  http://127.0.0.1:{port}"]
    if host == "0.0.0.0":
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except OSError:
            ip = "127.0.0.1"
        lines.append(f"  局域网:    http://{ip}:{port}")
    print("=" * 60)
    print("  tmux-ai-coder-panel 已启动")
    for line in lines:
        print(line)
    print(f"  API 文档:  http://127.0.0.1:{port}/docs")
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)


def main() -> int:
    try:
        cli_port, cli_host = _parse_args(sys.argv)   # --port/--host/--help/--version
        start_port = cli_port if cli_port is not None else _starting_port()
        host = cli_host if cli_host is not None else _starting_host()
        _validate_host(host)
        ensure_env_file()                            # 无 .env 则生成随机账号密码写 cwd
        port = find_free_port(start_port)            # socket bind 探测,占用则 +1
        from .main import app                        # 再导入(load_dotenv 读到新 .env)
        _print_banner(host, port)                    # 打印最终 URL
        uvicorn.run(app, host=host, port=port, log_level="info")
        return 0
    except KeyboardInterrupt:
        print("\n[tmux-ai-coder-panel] 已停止(Ctrl+C)")
        return 0
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[tmux-ai-coder-panel] 启动失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
