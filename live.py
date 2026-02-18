#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import urllib.error
import zipfile
import os
import sys
import subprocess
import tempfile
import shutil
import time
import socket

class LiveExecutor:
    def __init__(self):
        self.download_url = "https://github.com/Dunoguang/doubao-sandbox-geektool/archive/refs/tags/0.0.1.zip"
        self.target_dir = "/mnt"
        self.temp_dir = tempfile.mkdtemp()
        self.zip_path = os.path.join(self.temp_dir, '0.0.1.zip')
        
    def download_zip(self):
        """下载zip文件"""
        try:
            print(f"Downloading from {self.download_url}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(self.download_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                with open(self.zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            
            print(f"Download completed: {self.zip_path}")
            file_size = os.path.getsize(self.zip_path)
            print(f"Downloaded size: {file_size} bytes")
            
            if file_size == 0:
                print("Error: Downloaded file is empty")
                return False
                
            return True
            
        except Exception as e:
            print(f"Download failed: {e}")
            return False
            
    def extract_zip(self):
        """解压zip文件到目标目录"""
        try:
            print(f"Extracting to {self.target_dir}...")
            os.makedirs(self.target_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"Files in zip: {len(file_list)}")
                zip_ref.extractall(self.temp_dir)
                
            extracted_items = os.listdir(self.temp_dir)
            source_dir = None
            
            for item in extracted_items:
                item_path = os.path.join(self.temp_dir, item)
                if os.path.isdir(item_path) and 'doubao-sandbox-geektool' in item:
                    source_dir = item_path
                    break
                    
            if not source_dir:
                print("Error: Could not find extracted directory")
                return False
                
            print(f"Found source directory: {source_dir}")
            
            # 复制所有文件到/mnt
            for item in os.listdir(source_dir):
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(self.target_dir, item)
                
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, target_item)
                    print(f"Copied: {item}")
                elif os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                    print(f"Copied directory: {item}")
                    
            print(f"All files extracted to {self.target_dir}")
            return True
            
        except Exception as e:
            print(f"Extraction failed: {e}")
            return False
            
    def set_executable_permissions(self):
        """设置所有.py和.sh文件的执行权限"""
        try:
            print("Setting executable permissions...")
            
            for root, dirs, files in os.walk(self.target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if file.endswith('.py') or file.endswith('.sh') or file == 'busybox':
                        os.chmod(file_path, 0o755)
                        print(f"Set +x: {file_path}")
                        
            print("Permissions set successfully")
            return True
            
        except Exception as e:
            print(f"Failed to set permissions: {e}")
            return False
    
    def check_server_port(self):
        """检查8888端口是否已被占用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8888))
            sock.close()
            return result == 0  # 0表示端口已被占用
        except:
            return False
    
    def execute_main_script(self):
        """执行/mnt/main.py并传递硬编码命令"""
        try:
            main_script = os.path.join(self.target_dir, 'main.py')
            cmd = "cat /proc/cpuinfo"
            
            if not os.path.exists(main_script):
                print(f"Error: {main_script} not found")
                return False
            
            # 检查文件内容
            print("\nChecking main.py content:")
            with open(main_script, 'r') as f:
                first_lines = ''.join([f.readline() for _ in range(5)])
                print(first_lines)
            
            # 检查端口状态
            port_busy = self.check_server_port()
            if port_busy:
                print("Warning: Port 8888 is already in use")
            
            print(f"\nExecuting: {main_script} with command '{cmd}'")
            
            # 使用超时机制执行
            command = [sys.executable, main_script] + cmd.split()
            
            print(f"Command: {' '.join(command)}")
            
            # 设置超时（30秒）
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=30)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                print("Process timed out after 30 seconds")
                return False
            
            # 输出结果
            print("\n" + "="*50)
            print("Execution Results:")
            print("="*50)
            
            if stdout:
                print("STDOUT:")
                print(stdout)
                
            if stderr:
                print("STDERR:")
                print(stderr)
                
            print(f"RETURN CODE: {returncode}")
            print("="*50)
            
            # 检查是否有server.py进程在运行
            print("\nChecking for server.py processes:")
            os.system("ps aux | grep server.py | grep -v grep")
            
            return returncode == 0
            
        except Exception as e:
            print(f"Execution failed: {e}")
            return False
            
    def cleanup(self):
        """清理临时文件"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print("Temporary files cleaned up")
        except Exception as e:
            print(f"Cleanup warning: {e}")

def main():
    print("Live Executor Starting...")
    print("-" * 50)
    
    executor = LiveExecutor()
    
    try:
        print("\n[Step 1] Downloading...")
        if not executor.download_zip():
            print("Failed to download zip file")
            sys.exit(1)
            
        print("\n[Step 2] Extracting...")
        if not executor.extract_zip():
            print("Failed to extract zip file")
            sys.exit(1)
            
        print("\n[Step 3] Setting permissions...")
        if not executor.set_executable_permissions():
            print("Failed to set permissions")
            sys.exit(1)
            
        print("\n[Step 4] Executing main.py...")
        if not executor.execute_main_script():
            print("Failed to execute main.py")
            # 不立即退出，让我们有机会检查
            response = input("\nDo you want to check the files? (y/n): ")
            if response.lower() == 'y':
                print("\nChecking /mnt directory:")
                os.system("ls -la /mnt/")
                print("\nTrying to run main.py directly:")
                os.system("python3 /mnt/main.py 'cat /proc/cpuinfo'")
            sys.exit(1)
            
        print("\n✅ All steps completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        executor.cleanup()

if __name__ == '__main__':
    main()
