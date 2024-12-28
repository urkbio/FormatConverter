import os
import shutil
import sys
import subprocess
from PIL import Image
import PyQt5

def build_project():
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, 'build')
    dist_dir = os.path.join(root_dir, 'dist')  # 临时目录
    
    # 创建 build 目录（如果不存在）
    os.makedirs(build_dir, exist_ok=True)
    
    # 使用 PyInstaller 编译程序
    try:
        pyinstaller_args = [
            'pyinstaller',
            '--noconfirm',     # 覆盖现有文件
            '--clean',         # 清理临时文件
            '--windowed',      # 隐藏终端窗口
            '--workpath', os.path.join(build_dir, 'temp'),  # 临时文件目录
            '--distpath', build_dir,    # 直接输出到build目录
            '--add-data', f'{os.path.join(root_dir, "icons")}:icons',  # 添加图标资源
            '--hidden-import', 'PIL',
            '--hidden-import', 'PIL._imagingtk',
            '--hidden-import', 'PIL._tkinter_finder',
            '--hidden-import', 'PyQt5',
            '--hidden-import', 'PyQt5.QtCore',
            '--hidden-import', 'PyQt5.QtGui',
            '--hidden-import', 'PyQt5.QtWidgets',
            'file_converter.py'  # 主程序文件
        ]
        
        # 在 macOS 上使用 .icns 文件作为图标
        if sys.platform == 'darwin':
            icns_path = os.path.join(root_dir, 'icons', 'converter.icns')
            if os.path.exists(icns_path):
                pyinstaller_args.extend(['--icon', icns_path])
        else:
            # 在 Windows 上使用 .ico 文件
            pyinstaller_args.extend([
                '--icon', os.path.join(root_dir, 'icons', 'converter.ico'),
                '--manifest', 'app.manifest',  # 添加清单文件
                '--add-data', f'{os.path.join(root_dir, "ffmpeg")};ffmpeg'  # 添加ffmpeg
            ])
            
        subprocess.run(pyinstaller_args, check=True)
        print("编译完成！")
                
    except subprocess.CalledProcessError as e:
        print(f"编译失败: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if build_project():
        print("构建成功！输出目录: build/")
    else:
        print("构建失败！")