# Python DLL 加载问题解决方案

## 问题描述
需要在编译时自动将必要的 DLL 文件复制到构建目录

## 解决步骤
1. 创建 build.py 脚本处理编译和 DLL 复制
2. 运行 build.py 自动完成编译和文件复制

## 使用方法
1. 确保项目根目录包含所需的 DLL 文件：
   - python313.dll
   - python3.dll
   - vcruntime140.dll
2. 运行构建命令：
   ```bash
   python build.py
   ```
3. 构建完成后，所有文件将在 build 目录中

## 注意事项
- 需要安装 PyInstaller：`pip install pyinstaller`
- 确保有足够的磁盘空间和写入权限
- 编译输出的程序可以直接分发给用户使用