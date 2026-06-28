"""
SSH 连接管理模块
使用 paramiko 实现 SSH 连接和命令执行
"""

import paramiko
import threading
import time
from typing import Optional, Dict
from datetime import datetime


class SSHConnection:
    """SSH 连接管理器"""
    
    def __init__(self):
        self.client: Optional[paramiko.SSHClient] = None
        self.channel = None
        self.connected = False
        self.connection_info: Dict = {}
        self._lock = threading.Lock()
    
    def connect(self, hostname: str, port: int, username: str, password: Optional[str] = None, 
                key_filename: Optional[str] = None) -> Dict:
        """
        建立 SSH 连接
        
        Args:
            hostname: 主机地址
            port: 端口号
            username: 用户名
            password: 密码（可选）
            key_filename: 私钥文件路径（可选）
            
        Returns:
            连接结果字典
        """
        with self._lock:
            if self.connected:
                return {"success": False, "error": "已经连接，请先断开"}
            
            try:
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                connect_kwargs = {
                    'hostname': hostname,
                    'port': port,
                    'username': username,
                    'timeout': 10,
                    'allow_agent': True,
                    'look_for_keys': True
                }
                
                if password:
                    connect_kwargs['password'] = password
                
                if key_filename:
                    connect_kwargs['key_filename'] = key_filename
                
                self.client.connect(**connect_kwargs)
                
                # 打开交互式 shell channel
                self.channel = self.client.invoke_shell(
                    term='xterm-256color',
                    width=200,
                    height=50
                )
                self.channel.settimeout(1.0)
                
                self.connected = True
                self.connection_info = {
                    'hostname': hostname,
                    'port': port,
                    'username': username,
                    'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 读取初始输出
                time.sleep(0.5)
                initial_output = self._read_channel_output()
                
                return {
                    "success": True,
                    "message": f"成功连接到 {hostname}:{port}",
                    "info": self.connection_info,
                    "initial_output": initial_output
                }
                
            except paramiko.AuthenticationException:
                return {"success": False, "error": "认证失败，请检查用户名和密码/密钥"}
            except paramiko.SSHException as e:
                return {"success": False, "error": f"SSH 错误: {str(e)}"}
            except Exception as e:
                return {"success": False, "error": f"连接失败: {str(e)}"}
    
    def execute_command(self, command: str) -> Dict:
        """
        执行命令（通过交互式 channel）
        
        Args:
            command: 要执行的命令
            
        Returns:
            执行结果
        """
        with self._lock:
            if not self.connected or not self.channel:
                return {"success": False, "error": "未连接到 SSH 服务器"}
            
            try:
                # 发送命令
                self.channel.send(command + '\n')
                
                # 等待并读取输出
                time.sleep(0.5)
                output = self._read_channel_output()
                
                return {
                    "success": True,
                    "output": output,
                    "command": command
                }
                
            except Exception as e:
                return {"success": False, "error": f"命令执行失败: {str(e)}"}
    
    def _read_channel_output(self) -> str:
        """读取 channel 的输出"""
        output = ""
        try:
            while self.channel.recv_ready():
                data = self.channel.recv(65535).decode('utf-8', errors='replace')
                output += data
        except Exception:
            pass
        return output
    
    def disconnect(self) -> Dict:
        """断开 SSH 连接"""
        with self._lock:
            try:
                if self.channel:
                    self.channel.close()
                    self.channel = None
                
                if self.client:
                    self.client.close()
                    self.client = None
                
                self.connected = False
                hostname = self.connection_info.get('hostname', 'unknown')
                self.connection_info = {}
                
                return {
                    "success": True,
                    "message": f"已断开连接 {hostname}"
                }
                
            except Exception as e:
                return {"success": False, "error": f"断开连接失败: {str(e)}"}
    
    def get_status(self) -> Dict:
        """获取连接状态"""
        return {
            "connected": self.connected,
            "info": self.connection_info if self.connected else {}
        }


# 全局 SSH 连接实例
ssh_manager = SSHConnection()
