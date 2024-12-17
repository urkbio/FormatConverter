import os
import sys
import mimetypes
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
                           QComboBox, QMessageBox, QProgressBar, QLineEdit, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image
import subprocess
from PyQt5.QtGui import QIcon

class ConvertThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, file_path, output_path, file_type, target_format, ffmpeg_path):
        super().__init__()
        self.file_path = file_path
        self.output_path = output_path
        self.file_type = file_type
        self.target_format = target_format
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        try:
            if self.file_type == "image":
                self.convert_image()
            elif self.file_type == "video":
                self.convert_video()
            else:
                self.convert_audio()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def convert_image(self):
        try:
            # 打开图片
            img = Image.open(self.file_path)
            self.progress.emit(30)
            
            # 如果是PNG或其他带透明通道的格式，需要先转换为RGB
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                # 如果有透明通道，进行alpha合成
                if 'A' in img.mode:
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
            self.progress.emit(60)
            
            # 保存图片
            img.save(str(self.output_path), 
                    self.target_format.upper(), 
                    quality=95,  # JPEG质量设置
                    optimize=True)  # 优化文件大小
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(f"图片转换错误: {str(e)}")

    def convert_video(self):
        try:
            input_path = str(self.file_path)
            output_path = str(self.output_path)
            
            print(f"开始视频转换：")
            print(f"输入文件：{input_path}")
            print(f"输出文件：{output_path}")
            print(f"目标格式：{self.target_format}")
            
            # 检查编码器支持
            probe_cmd = [self.ffmpeg_path, '-encoders']
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            encoders = result.stdout.lower()
            print("可用编码器：", encoders)
            
            # 基础命令参数
            base_cmd = [
                self.ffmpeg_path,
                '-hide_banner',
                '-i', input_path,
                '-y'
            ]
            
            # 根据目标格式添加特定参数
            if self.target_format in ['mp4', 'mkv']:
                if 'libx264' not in encoders:
                    raise Exception("当前 FFmpeg 不支持 H.264 编码")
                format_cmd = [
                    '-c:a', 'aac',
                    '-c:v', 'libx264',
                    '-preset', 'medium',
                    '-crf', '23'
                ]
            elif self.target_format == 'flv':
                format_cmd = [
                    '-c:a', 'aac',
                    '-c:v', 'flv',
                    '-f', 'flv'
                ]
            elif self.target_format == 'wmv':
                if 'wmv2' not in encoders:
                    raise Exception("当前 FFmpeg 不支持 WMV 编码")
                format_cmd = [
                    '-c:a', 'wmav2',
                    '-c:v', 'wmv2',
                    '-f', 'asf'
                ]
            elif self.target_format == 'avi':
                format_cmd = [
                    '-c:a', 'mp3',
                    '-c:v', 'mpeg4'
                ]
            elif self.target_format == 'mov':
                format_cmd = [
                    '-c:a', 'aac',
                    '-c:v', 'h264',
                    '-f', 'mov'
                ]
            else:
                raise ValueError(f"不支持的视频格式: {self.target_format}")
            
            # 组合完整命令
            cmd = base_cmd + format_cmd + [output_path]
            print(f"执行命令：{' '.join(cmd)}")
            
            self.progress.emit(10)
            
            # 运行转换命令
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace',
                startupinfo=startupinfo  # 添加 startupinfo
            )
            
            stdout, stderr = process.communicate()
            print(f"FFmpeg 输出：")
            if stdout:
                print(f"标准输出：\n{stdout}")
            if stderr:
                print(f"错误输出：\n{stderr}")
            
            if process.returncode != 0:
                error_msg = stderr.strip() if stderr else "未知错误"
                raise Exception(f"FFmpeg 错误: {error_msg}")
            
            # 检查输出文件
            if not Path(output_path).exists():
                raise Exception("转换失败：输出文件未生成")
            if Path(output_path).stat().st_size == 0:
                raise Exception("转换失败：输出文件大小为0")
                
            print("转换成功完成")
            self.progress.emit(100)
            
        except Exception as e:
            error_msg = str(e)
            print(f"转换失败：{error_msg}")
            self.error.emit(f"视频转换错误: {error_msg}")

    def convert_audio(self):
        try:
            input_path = str(self.file_path)
            output_path = str(self.output_path)
            
            print(f"开始音频转换：")
            print(f"输入文件：{input_path}")
            print(f"输出文件：{output_path}")
            print(f"目标格式：{self.target_format}")
            
            # 检查编码器支持
            probe_cmd = [self.ffmpeg_path, '-encoders']
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            encoders = result.stdout.lower()
            print("可用编码器：", encoders)
            
            # 基础命令参数
            base_cmd = [
                self.ffmpeg_path,
                '-hide_banner',
                '-i', input_path,
                '-y'
            ]
            
            # 根据目标格式添加特定参数
            if self.target_format == 'm4a':
                if 'aac' not in encoders:
                    raise Exception("当前 FFmpeg 不支持 AAC 编码，无法转换为 M4A 格式")
                format_cmd = [
                    '-c:a', 'aac',
                    '-b:a', '192k',
                    '-f', 'mp4',  # 使用 mp4 容器
                    '-movflags', '+faststart'
                ]
            elif self.target_format == 'mp3':
                if 'libmp3lame' not in encoders:
                    raise Exception("当前 FFmpeg 不支持 MP3 编码")
                format_cmd = [
                    '-c:a', 'libmp3lame',
                    '-q:a', '4'
                ]
            elif self.target_format == 'wav':
                format_cmd = [
                    '-c:a', 'pcm_s16le',
                    '-ar', '44100'
                ]
            elif self.target_format == 'ogg':
                if 'libvorbis' not in encoders:
                    raise Exception("当前 FFmpeg 不支持 OGG/Vorbis 编码")
                format_cmd = [
                    '-c:a', 'libvorbis',
                    '-q:a', '4'
                ]
            else:
                raise ValueError(f"不支持的音频格式: {self.target_format}")
            
            # 组合完整命令
            cmd = base_cmd + format_cmd + [output_path]
            print(f"执行命令：{' '.join(cmd)}")
            
            self.progress.emit(10)
            
            # 运行转换命令
            startupinfo = None
            if sys.platform == 'win32':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace',
                startupinfo=startupinfo  # 添加 startupinfo
            )
            
            # 等待转换完成
            stdout, stderr = process.communicate()
            print(f"FFmpeg 输出：")
            if stdout:
                print(f"标准输出：\n{stdout}")
            if stderr:
                print(f"错误输出：\n{stderr}")
            
            if process.returncode != 0:
                error_msg = stderr.strip() if stderr else "未知错误"
                raise Exception(f"FFmpeg 错误: {error_msg}")
            
            # 检查输出文件
            if not Path(output_path).exists():
                raise Exception("转换失败：输出文件未生成")
            if Path(output_path).stat().st_size == 0:
                raise Exception("转换失败：输出文件大小为0")
                
            print("转换成功完成")
            self.progress.emit(100)
            
        except Exception as e:
            error_msg = str(e)
            print(f"转换失败：{error_msg}")
            self.error.emit(f"音频转换错误: {error_msg}")

class FileConverterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('媒体文件格式转换器')
        self.setGeometry(100, 100, 800, 600)  # 加大窗口尺寸
        
        # 设置程序图标
        icon_path = self.get_icon_path()
        if icon_path and icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
            QProgressBar {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
            }
        """)
        
        # 支持的格式
        self.image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif'}
        self.video_formats = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'}
        self.audio_formats = {'.mp3', '.wav', '.aac', '.ogg'}  # 移除 m4a
        
        # 允许拖放
        self.setAcceptDrops(True)
        
        self.selected_file = None
        self.file_type = None
        self.output_dir = str(Path.home() / "Downloads")
        
        # 设置 ffmpeg 路径
        self.ffmpeg_path = self.setup_ffmpeg()
        
        self.init_ui()

    def setup_ffmpeg(self):
        """设置 ffmpeg 路径"""
        try:
            # 获取程序所在目录
            if getattr(sys, 'frozen', False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent
            
            # 根据操作系统选择正确的 ffmpeg 可执行文件
            if sys.platform == 'win32':
                ffmpeg_path = base_path / 'ffmpeg' / 'ffmpeg.exe'
            else:
                ffmpeg_path = base_path / 'ffmpeg' / 'ffmpeg'
            
            print(f"FFMPEG路径: {ffmpeg_path}")
            print(f"路径是否存在: {ffmpeg_path.exists()}")
                
            if not ffmpeg_path.exists():
                alt_path = Path('ffmpeg') / ('ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg')
                if alt_path.exists():
                    ffmpeg_path = alt_path
                else:
                    raise FileNotFoundError(f"找不到 ffmpeg，已尝试路径：\n1. {ffmpeg_path}\n2. {alt_path}")
            
            # 设置 ffmpeg 环境变量
            os.environ["FFMPEG_BINARY"] = str(ffmpeg_path)
            print(f"设置的FFMPEG环境变量: {os.environ['FFMPEG_BINARY']}")
            
            return str(ffmpeg_path)
            
        except Exception as e:
            error_msg = f'设置 ffmpeg 失败：{str(e)}\n当前目录：{os.getcwd()}'
            print(error_msg)
            QMessageBox.critical(self, '错误', error_msg)
            sys.exit(1)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 增加控件间距
        layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        
        # 添加拖放提示区域
        self.drop_area = QLabel('将文件拖放到此处或点击"选择文件"按钮')
        self.drop_area.setAlignment(Qt.AlignCenter)
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #BDBDBD;
                border-radius: 8px;
                padding: 40px;
                background-color: #FFFFFF;
                color: #757575;
                font-size: 16px;
            }
        """)
        self.drop_area.setMinimumHeight(150)
        layout.addWidget(self.drop_area)
        
        # 输出目录选择
        dir_group = QGroupBox("输出设置")
        dir_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        dir_layout = QHBoxLayout()
        self.dir_edit = QLineEdit(self.output_dir)
        dir_layout.addWidget(QLabel('输出目录：'))
        dir_layout.addWidget(self.dir_edit)
        
        # 添加浏览和打开按钮
        button_container = QHBoxLayout()
        dir_button = QPushButton('浏览')
        dir_button.clicked.connect(self.select_output_dir)
        open_dir_button = QPushButton('打开输出目录')
        open_dir_button.clicked.connect(self.open_output_dir)
        
        # 设置按钮样式
        open_dir_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                padding: 8px 12px;  # 稍微调整padding以适应更长的文本
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """)
        
        button_container.addWidget(dir_button)
        button_container.addWidget(open_dir_button)
        dir_layout.addLayout(button_container)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # 进度显示组
        progress_group = QGroupBox("转换进度")
        progress_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDBDBD;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
        """)
        progress_layout = QVBoxLayout()
        
        # 上传进度
        upload_label = QLabel('文件上传进度：')
        self.upload_progress = QProgressBar()
        self.upload_progress.hide()
        progress_layout.addWidget(upload_label)
        progress_layout.addWidget(self.upload_progress)
        
        # 转换进度
        convert_label = QLabel('转换进度：')
        self.convert_progress = QProgressBar()
        self.convert_progress.hide()
        progress_layout.addWidget(convert_label)
        progress_layout.addWidget(self.convert_progress)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 文件选择按钮
        button_layout = QHBoxLayout()
        self.select_button = QPushButton('选择文件')
        self.select_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 文件信息标签
        self.file_info = QLabel('')
        self.file_info.setStyleSheet("padding: 10px; background-color: #FFFFFF; border-radius: 4px;")
        layout.addWidget(self.file_info)
        
        # 格式选择组
        format_group = QHBoxLayout()
        self.format_label = QLabel('选择目标格式：')
        self.format_combo = QComboBox()
        self.format_label.hide()
        self.format_combo.hide()
        format_group.addWidget(self.format_label)
        format_group.addWidget(self.format_combo)
        format_group.addStretch()
        layout.addLayout(format_group)
        
        # 转换按钮
        convert_layout = QHBoxLayout()
        convert_layout.addStretch()
        self.convert_button = QPushButton('开始转换')
        self.convert_button.clicked.connect(self.start_convert)
        self.convert_button.hide()
        convert_layout.addWidget(self.convert_button)
        convert_layout.addStretch()
        layout.addLayout(convert_layout)
        
        # 状态标签
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        layout.addStretch()  # 添加弹性空间
        main_widget.setLayout(layout)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "选择输出目录",
            self.output_dir
        )
        if dir_path:
            # 同时更新 output_dir 和 dir_edit
            self.output_dir = dir_path
            self.dir_edit.setText(dir_path)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "所有支持的文件 (*.*)"
        )
        
        if file_path:
            self.selected_file = file_path
            self.upload_progress.show()
            
            # 模拟上传进度
            for i in range(101):
                self.upload_progress.setValue(i)
                QApplication.processEvents()
                self.msleep(20)
            
            # 判断文件类型
            self.detect_file_type(file_path)
            
            # 显示文件信息
            file_name = Path(file_path).name
            self.file_info.setText(f'已选择文件：{file_name}\n类型：{self.get_type_name()}')
            
            # 更新可用的目标格式
            self.update_format_combo()
            
            # 显示转换相关控件
            self.format_label.show()
            self.format_combo.show()
            self.convert_button.show()
            self.status_label.setText('')

    def msleep(self, msecs):
        QThread.msleep(msecs)

    def detect_file_type(self, file_path):
        ext = Path(file_path).suffix.lower()
        if ext in self.image_formats:
            self.file_type = "image"
        elif ext in self.video_formats:
            self.file_type = "video"
        elif ext in self.audio_formats:
            self.file_type = "audio"
        else:
            mime_type = mimetypes.guess_type(file_path)[0]
            if mime_type:
                if mime_type.startswith('image/'):
                    self.file_type = "image"
                elif mime_type.startswith('video/'):
                    self.file_type = "video"
                elif mime_type.startswith('audio/'):
                    self.file_type = "audio"
            else:
                raise ValueError("不支持的文件类型")

    def get_type_name(self):
        return {
            "image": "图片文件",
            "video": "视频文件",
            "audio": "音频文件"
        }.get(self.file_type, "未知类型")

    def update_format_combo(self):
        self.format_combo.clear()
        current_ext = Path(self.selected_file).suffix.lower()
        
        if self.file_type == "image":
            formats = [f for f in self.image_formats if f != current_ext]
        elif self.file_type == "video":
            formats = [f for f in self.video_formats if f != current_ext]
        else:
            formats = [f for f in self.audio_formats if f != current_ext]
            
        self.format_combo.addItems([f[1:] for f in sorted(formats)])

    def start_convert(self):
        if not self.selected_file or not self.format_combo.currentText():
            return
            
        output_name = f"{Path(self.selected_file).stem}_converted.{self.format_combo.currentText()}"
        output_path = Path(self.output_dir) / output_name
        
        self.convert_progress.show()
        self.convert_progress.setValue(0)
        self.convert_button.setEnabled(False)
        self.status_label.setText('正在转换...')
        
        self.convert_thread = ConvertThread(
            self.selected_file,
            output_path,
            self.file_type,
            self.format_combo.currentText(),
            self.ffmpeg_path
        )
        self.convert_thread.progress.connect(self.convert_progress.setValue)
        self.convert_thread.finished.connect(self.conversion_finished)
        self.convert_thread.error.connect(self.conversion_error)
        self.convert_thread.start()

    def conversion_finished(self):
        self.convert_button.setEnabled(True)
        self.status_label.setText('转换完成！')
        QMessageBox.information(self, '完成', '文件转换已完成！')

    def conversion_error(self, error_msg):
        self.convert_button.setEnabled(True)
        self.status_label.setText('转换失败！')
        QMessageBox.critical(self, '错误', f'转换失败：{error_msg}')

    # 添加拖放相关方法
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.drop_area.setStyleSheet("""
                QLabel {
                    border: 2px dashed #4CAF50;
                    border-radius: 8px;
                    padding: 40px;
                    background-color: #E8F5E9;
                    color: #2E7D32;
                    font-size: 16px;
                }
            """)
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet("""
            QLabel {
                border: 2px dashed #BDBDBD;
                border-radius: 8px;
                padding: 40px;
                background-color: #FFFFFF;
                color: #757575;
                font-size: 16px;
            }
        """)

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            file_path = files[0]  # 只处理第一个文件
            try:
                # 使用现有的文件处理逻辑
                self.selected_file = file_path
                self.upload_progress.show()
                
                # 模拟上传进度
                for i in range(101):
                    self.upload_progress.setValue(i)
                    QApplication.processEvents()
                    self.msleep(20)
                
                # 判断文件类型
                self.detect_file_type(file_path)
                
                # 显示文件信息
                file_name = Path(file_path).name
                self.file_info.setText(f'已选择文件：{file_name}\n类型：{self.get_type_name()}')
                
                # 更新可用的目标格式
                self.update_format_combo()
                
                # 显示转换相关控件
                self.format_label.show()
                self.format_combo.show()
                self.convert_button.show()
                self.status_label.setText('')
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'无法处理文件：{str(e)}')

    def open_output_dir(self):
        """打开输出目录"""
        try:
            # 使用 dir_edit 中的路径而不是 self.output_dir
            output_dir = self.dir_edit.text()
            
            # 检查目录是否存在
            if not os.path.exists(output_dir):
                raise FileNotFoundError(f"目录不存在：{output_dir}")
                
            if sys.platform == 'win32':
                # 直接使用 explorer 打开目录
                subprocess.run(['explorer', str(Path(output_dir))])
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', '-n', output_dir])
            else:  # Linux
                try:
                    # 尝试使用 nautilus (GNOME)
                    subprocess.run(['nautilus', '--new-window', '--geometry=800x600', output_dir])
                except FileNotFoundError:
                    try:
                        # 尝试使用 dolphin (KDE)
                        subprocess.run(['dolphin', '--new-window', '--geometry=800x600', output_dir])
                    except FileNotFoundError:
                        # 如果都不可用，使用默认的 xdg-open
                        subprocess.run(['xdg-open', output_dir])
        except Exception as e:
            QMessageBox.warning(self, '警告', f'无法打开目录：{str(e)}')

    def get_icon_path(self):
        """获取图标路径"""
        try:
            if getattr(sys, 'frozen', False):
                # PyInstaller 打包后的路径
                base_path = Path(sys._MEIPASS)
            else:
                # 开发环境下的路径
                base_path = Path(__file__).parent
                
            icon_path = base_path / 'icons' / 'converter.png'
            return icon_path
        except Exception:
            return None

def main():
    try:
        app = QApplication(sys.argv)
        window = FileConverterWindow()
        window.show()
        return app.exec_()
    except SystemExit:
        pass
    except Exception as e:
        print(f"发生错误：{str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 