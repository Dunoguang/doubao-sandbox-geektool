#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import json
import subprocess
import os
import sys
import time

class CommandExecutor:
    def __init__(self, server_host='localhost', server_port=8888):
        self.server_host = server_host
        self.server_port = server_port
        
    def check_server(self):
        """检查server.py是否在运行"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)
            test_socket.connect((self.server_host, self.server_port))
            test_socket.close()
            return True
        except:
            return False
            
    def start_server(self):
        """启动server.py作为独立进程"""
        try:
            # 获取当前脚本所在目录
            script_dir = os.path.dirname(os.path.abspath(__file__))
            server_path = os.path.join(script_dir, 'server.py')
            
            # 启动server.py作为独立进程
            process = subprocess.Popen(
                ['python3', server_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # 等待服务器启动
            time.sleep(1)
            
            # 检查是否成功启动
            if self.check_server():
                print("Server started successfully")
                return True
            else:
                print("Failed to start server")
                return False
                
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
            
    def execute_via_server(self, cmd):
        """通过server.py执行命令"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(10)
            client_socket.connect((self.server_host, self.server_port))
            
            # 发送命令
            command_data = json.dumps({'cmd': cmd})
            client_socket.send(command_data.encode('utf-8'))
            
            # 接收结果
            response = client_socket.recv(65536).decode('utf-8')
            result = json.loads(response)
            
            return result
            
        except Exception as e:
            return {
                'stdout': '',
                'stderr': f"Connection error: {e}",
                'returncode': -1
            }
        finally:
            client_socket.close()
            
    def execute(self, cmd):
        """执行命令的主逻辑"""
        # 检查服务器是否在运行
        if self.check_server():
            print("Server is running, sending command...")
            return self.execute_via_server(cmd)
        else:
            print("Server not running, starting...")
            if self.start_server():
                print("Sending command to new server...")
                return self.execute_via_server(cmd)
            else:
                print("Failed to start server, executing locally...")
                return self.execute_locally(cmd)
                
    def execute_locally(self, cmd):
        """本地执行命令（备用方案）"""
        try:
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

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <command>")
        print("Example: python3 main.py 'cat /proc/cpuinfo'")
        sys.exit(1)
        
    # 获取命令（支持多个参数组合成一个命令）
    cmd = ' '.join(sys.argv[1:])
    
    # 创建执行器并执行命令
    executor = CommandExecutor()
    result = executor.execute(cmd)
    
    # 输出结果
    if result['stdout']:
        print("STDOUT:")
        print(result['stdout'])
        
    if result['stderr']:
        print("STDERR:")
        print(result['stderr'])
        
    print(f"RETURN: {result['returncode']}")
    
    # 以返回码退出
    sys.exit(result['returncode'])

if __name__ == '__main__':
    main()
