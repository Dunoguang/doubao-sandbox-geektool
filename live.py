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

class LiveExecutor:
    def __init__(self):
        # 硬编码下载链接
        self.download_url = "https://github.com/Dunoguang/doubao-sandbox-geektool/archive/refs/tags/0.0.1.zip"
        self.target_dir = "/mnt"
        self.temp_dir = tempfile.mkdtemp()
        self.zip_path = os.path.join(self.temp_dir, '0.0.1.zip')
        
    def download_zip(self):
        """下载zip文件"""
        try:
            print(f"Downloading from {self.download_url}...")
            
            # 设置请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(self.download_url, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                with open(self.zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
            
            print(f"Download completed: {self.zip_path}")
            
            # 检查文件大小
            file_size = os.path.getsize(self.zip_path)
            print(f"Downloaded size: {file_size} bytes")
            
            if file_size == 0:
                print("Error: Downloaded file is empty")
                return False
                
            return True
            
        except urllib.error.URLError as e:
            print(f"Download failed (URL error): {e}")
            return False
        except Exception as e:
            print(f"Download failed: {e}")
            return False
            
    def extract_zip(self):
        """解压zip文件到目标目录"""
        try:
            print(f"Extracting to {self.target_dir}...")
            
            # 确保目标目录存在
            os.makedirs(self.target_dir, exist_ok=True)
            
            # 解压zip文件
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # 获取zip中的文件列表
                file_list = zip_ref.namelist()
                print(f"Files in zip: {len(file_list)}")
                
                # 解压所有文件
                zip_ref.extractall(self.temp_dir)
                
            # 找到解压后的文件夹（通常是doubao-sandbox-geektool-0.0.1）
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
            
        except zipfile.BadZipFile:
            print("Error: Invalid or corrupted zip file")
            return False
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
                    
                    # 给.py和.sh文件添加执行权限
                    if file.endswith('.py') or file.endswith('.sh'):
                        os.chmod(file_path, 0o755)
                        print(f"Set +x: {file_path}")
                        
            print("Permissions set successfully")
            return True
            
        except Exception as e:
            print(f"Failed to set permissions: {e}")
            return False
            
    def execute_main_script(self):
        """执行/mnt/main.py并传递硬编码命令"""
        try:
            main_script = os.path.join(self.target_dir, 'main.py')
            cmd = "cat /proc/cpuinfo"  # 硬编码命令
            
            if not os.path.exists(main_script):
                print(f"Error: {main_script} not found")
                return False
                
            print(f"Executing: {main_script} with command '{cmd}'")
            
            # 构建命令
            command = [sys.executable, main_script] + cmd.split()
            
            # 执行main.py
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
            print("Execution Results:")
            print("="*50)
            
            if stdout:
                print("STDOUT:")
                print(stdout)
                
            if stderr:
                print("STDERR:")
                print(stderr, file=sys.stderr)
                
            print(f"RETURN CODE: {returncode}")
            print("="*50)
            
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
    
    # 创建执行器
    executor = LiveExecutor()
    
    try:
        # 步骤1: 下载zip文件
        print("\n[Step 1] Downloading...")
        if not executor.download_zip():
            print("Failed to download zip file")
            sys.exit(1)
            
        # 步骤2: 解压到/mnt
        print("\n[Step 2] Extracting...")
        if not executor.extract_zip():
            print("Failed to extract zip file")
            sys.exit(1)
            
        # 步骤3: 设置执行权限
        print("\n[Step 3] Setting permissions...")
        if not executor.set_executable_permissions():
            print("Failed to set permissions")
            sys.exit(1)
            
        # 步骤4: 执行main.py
        print("\n[Step 4] Executing main.py...")
        if not executor.execute_main_script():
            print("Failed to execute main.py")
            sys.exit(1)
            
        print("\n✅ All steps completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        # 清理临时文件
        executor.cleanup()

if __name__ == '__main__':
    main()
