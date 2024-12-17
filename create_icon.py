from PIL import Image, ImageDraw

def create_converter_icon():
    # 创建一个新的图像，使用RGBA模式支持透明度
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 设置颜色
    primary_color = "#2196F3"    # 蓝色
    secondary_color = "#4CAF50"  # 绿色
    
    # 绘制圆形背景
    padding = size * 0.1
    circle_bbox = (padding, padding, size-padding, size-padding)
    draw.ellipse(circle_bbox, fill=primary_color)
    
    # 绘制转换箭头
    arrow_width = size * 0.4
    arrow_height = size * 0.2
    center_x = size / 2
    center_y = size / 2
    
    # 绘制两个箭头形成循环转换的图案
    points1 = [
        (center_x - arrow_width/2, center_y - arrow_height),
        (center_x, center_y - arrow_height*2),
        (center_x + arrow_width/2, center_y - arrow_height),
        (center_x + arrow_width/2, center_y),
        (center_x - arrow_width/2, center_y)
    ]
    
    points2 = [
        (center_x + arrow_width/2, center_y + arrow_height),
        (center_x, center_y + arrow_height*2),
        (center_x - arrow_width/2, center_y + arrow_height),
        (center_x - arrow_width/2, center_y),
        (center_x + arrow_width/2, center_y)
    ]
    
    draw.polygon(points1, fill=secondary_color)
    draw.polygon(points2, fill=secondary_color)
    
    # 保存PNG文件
    img.save('icons/converter.png')
    
    # 创建多个尺寸的图标并保存为ICO文件
    sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
    icons = []
    for size in sizes:
        icons.append(img.resize(size, Image.Resampling.LANCZOS))
    
    # 保存ICO文件
    icons[0].save('icons/converter.ico', format='ICO', sizes=sizes, append_images=icons[1:])

# 确保icons目录存在
import os
if not os.path.exists('icons'):
    os.makedirs('icons')

# 创建图标
create_converter_icon()
