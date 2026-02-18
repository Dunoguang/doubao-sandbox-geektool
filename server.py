#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import subprocess
import json
import sys
import os
import time
import signal

class CommandServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.running = True
        
    def start(self):
        """启动服务器"""
        # 创建socket服务器
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            print(f"Server started on {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {e}")
            sys.exit(1)
            
        # 忽略终止信号，让main.py可以独立运行
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                self.handle_client(client_socket)
            except Exception as e:
                print(f"Error accepting connection: {e}")
                
    def handle_client(self, client_socket):
        """处理客户端连接"""
        try:
            # 接收命令
            data = client_socket.recv(4096).decode('utf-8')
            if not data:
                return
                
            command = json.loads(data)
            cmd = command.get('cmd', '')
            
            # 执行命令
            result = self.execute_command(cmd)
            
            # 返回结果
            response = json.dumps(result)
            client_socket.send(response.encode('utf-8'))
            
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
            
    def execute_command(self, cmd):
        """执行shell命令"""
        try:
            # 使用shell执行命令
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            returncode = process.returncode
            
            return {
                'stdout': stdout,
                'stderr': stderr,
                'returncode': returncode
            }
            
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
            
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.socket:
            self.socket.close()

def main():
    server = CommandServer()
    
    # 检查是否已经有实例在运行
    try:
        # 尝试连接已存在的服务器
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.connect(('localhost', 8888))
        test_socket.close()
        print("Server is already running")
        sys.exit(0)
    except:
        # 没有服务器运行，启动新的
        server.start()

if __name__ == '__main__':
    # 守护进程化
    if os.fork() > 0:
        sys.exit(0)
        
    os.setsid()
    if os.fork() > 0:
        sys.exit(0)
        
    # 重定向标准输入输出
    sys.stdout.flush()
    sys.stderr.flush()
    
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'w') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())
        
    main()
