import os
import shutil
import sys

def copy_python_dlls():
    # 获取 Python 安装目录
    python_dir = os.path.dirname(sys.executable)
    # 获取当前程序目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 需要复制的 DLL 文件列表
    required_dlls = [
        'python313.dll',
        'python3.dll',
        'vcruntime140.dll',
    ]
    
    for dll in required_dlls:
        src = os.path.join(python_dir, dll)
        dst = os.path.join(current_dir, dll)
        try:
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"已复制 {dll} 到程序目录")
            else:
                print(f"警告: 未找到 {dll}")
        except Exception as e:
            print(f"复制 {dll} 时出错: {e}")

if __name__ == '__main__':
    copy_python_dlls() 