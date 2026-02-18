#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import subprocess
import sys
import os
import tempfile

class LiveExecutor:
    def __init__(self):
        # 硬编码main.py的下载链接
        self.main_script_url = "http://your-server.com/main.py"  # 修改为实际的下载地址
        # 硬编码要执行的命令
        self.cmd = "cat /proc/cpuinfo"  # 修改为要执行的命令
        
        self.temp_dir = tempfile.mkdtemp()
        self.main_script_path = os.path.join(self.temp_dir, 'main.py')
        
    def download_main_script(self):
        """下载main.py"""
        try:
            print(f"Downloading main.py from {self.main_script_url}...")
            urllib.request.urlretrieve(self.main_script_url, self.main_script_path)
            print("Download completed")
            
            # 确保脚本可执行
            os.chmod(self.main_script_path, 0o755)
            return True
            
        except urllib.error.URLError as e:
            print(f"Download failed: {e}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False
            
    def execute_main(self):
        """执行main.py并传递硬编码的命令"""
        try:
            # 构建命令 - 将硬编码的cmd作为参数传递给main.py
            command = [sys.executable, self.main_script_path] + self.cmd.split()
            
            # 执行main.py
            print(f"Executing: {' '.join(command)}")
            print(f"Command to execute: {self.cmd}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            returncode = process.returncode
            
            # 输出结果
            print("\n" + "="*50)
            print("EXECUTION RESULTS:")
            print("="*50)
            
            if stdout:
                print("STDOUT:")
                print(stdout)
                
            if stderr:
                print("STDERR:")
                print(stderr, file=sys.stderr)
                
            print(f"RETURN CODE: {returncode}")
            print("="*50)
            
            return returncode
            
        except Exception as e:
            print(f"Execution failed: {e}")
            return -1
            
    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.main_script_path):
                os.remove(self.main_script_path)
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
        except:
            pass

def main():
    # 创建执行器（使用硬编码的URL和命令）
    executor = LiveExecutor()
    
    print("="*50)
    print("LIVE EXECUTOR - HARDCODED CONFIGURATION")
    print("="*50)
    print(f"Download URL: {executor.main_script_url}")
    print(f"Command: {executor.cmd}")
    print("="*50)
    
    try:
        # 下载main.py
        if not executor.download_main_script():
            print("Failed to download main.py")
            sys.exit(1)
            
        # 执行命令
        returncode = executor.execute_main()
        
        # 以返回码退出
        sys.exit(returncode)
        
    finally:
        # 清理临时文件
        executor.cleanup()

if __name__ == '__main__':
    main()
