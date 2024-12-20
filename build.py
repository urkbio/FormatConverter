import os
import shutil
import sys
import subprocess

def build_project():
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, 'build')
    dist_dir = os.path.join(root_dir, 'dist')  # 临时目录
    
    # 创建 build 目录（如果不存在）
    os.makedirs(build_dir, exist_ok=True)
    
    # 使用 PyInstaller 编译程序
    try:
        subprocess.run([
            'pyinstaller',
            '--noconfirm',     # 覆盖现有文件
            '--clean',         # 清理临时文件
            '--onedir',        # 生成目录模式
            '--windowed',      # 隐藏终端窗口
            '--workpath', os.path.join(build_dir, 'temp'),  # 临时文件目录
            '--distpath', dist_dir,    # 临时输出目录
            '--add-data', f'{os.path.join(root_dir, "icons")};icons',  # 添加图标资源
            '--icon', os.path.join(root_dir, 'icons', 'converter.ico'),  # 设置程序图标
            '--add-data', f'{os.path.join(root_dir, "ffmpeg")};ffmpeg',  # 添加ffmpeg
            '--manifest', 'app.manifest',  # 添加清单文件
            'file_converter.py'  # 主程序文件
        ], check=True)
        
        # 将编译结果移动到 build 目录
        program_dir = os.path.join(dist_dir, 'file_converter')
        if os.path.exists(program_dir):
            # 如果 build 目录下已存在目标文件夹，先删除
            target_dir = os.path.join(build_dir, 'file_converter')
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            # 移动编译结果
            shutil.move(program_dir, build_dir)
            # 删除临时目录
            shutil.rmtree(dist_dir)
            
        print("编译完成！")
        
        # 复制 DLL 文件到编译输出目录
        dll_files = ['python313.dll', 'python3.dll', 'vcruntime140.dll']
        program_dir = os.path.join(build_dir, 'file_converter')
        for dll in dll_files:
            src = os.path.join(root_dir, dll)
            dst = os.path.join(program_dir, dll)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"已复制 {dll} 到构建目录")
            else:
                print(f"警告: 未找到 {dll}")
                
    except subprocess.CalledProcessError as e:
        print(f"编译失败: {e}")
        return False
    except Exception as e:
        print(f"发生错误: {e}")
        return False
    
    return True

if __name__ == '__main__':
    if build_project():
        print("构建成功！输出目录: build/file_converter/")
    else:
        print("构建失败！") 