import os
import sys

# 获取程序运行目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 DLL 搜索路径
os.environ["PATH"] = current_dir + os.pathsep + os.environ["PATH"]

# 原有代码...