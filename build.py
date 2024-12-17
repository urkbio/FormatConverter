import PyInstaller.__main__
import sys
from pathlib import Path

# 获取当前目录
current_dir = Path(__file__).parent

# 检查必要文件
ffmpeg_path = current_dir / 'ffmpeg'
icons_path = current_dir / 'icons'

# 确保 ffmpeg 目录存在
if not ffmpeg_path.exists():
    print(f"错误：找不到 ffmpeg 目录：{ffmpeg_path}")
    sys.exit(1)

# 检查 ffmpeg 可执行文件
ffmpeg_exe = ffmpeg_path / 'ffmpeg.exe'
if not ffmpeg_exe.exists():
    print(f"错误：找不到 ffmpeg.exe：{ffmpeg_exe}")
    sys.exit(1)

# 检查图标文件
icon_file = icons_path / 'converter.ico'
if not icon_file.exists():
    print(f"警告：找不到图标文件：{icon_file}")
    icon_arg = []
else:
    icon_arg = [f'--icon={icon_file}']

# 检查版本文件和清单文件
version_file = current_dir / 'version.txt'
manifest_file = current_dir / 'app.manifest'

if not version_file.exists():
    print(f"警告：找不到版本文件：{version_file}")
    version_arg = []
else:
    version_arg = [f'--version-file={version_file}']

if not manifest_file.exists():
    print(f"警告：找不到清单文件：{manifest_file}")
    manifest_arg = []
else:
    manifest_arg = [f'--manifest={manifest_file}']

print(f"使用 ffmpeg：{ffmpeg_exe}")

# 打包命令
PyInstaller.__main__.run([
    'file_converter.py',
    # '--onefile',        # 注释掉单文件模式
    '--windowed',         # 不显示控制台窗口
    '--clean',           # 清理临时文件
    '--noconfirm',       # 不确认覆盖
    '--name=FormatConverter',  # 可执行文件名称
    f'--add-data={ffmpeg_path};ffmpeg',  # 添加 ffmpeg 目录
    f'--add-data={icons_path};icons',    # 添加图标目录
    *icon_arg,           # 添加图标参数
    *version_arg,        # 添加版本信息
    *manifest_arg,       # 添加清单文件
]) 