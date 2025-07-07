import os
import sys
import argparse
import logging
from typing import List, Optional
import math

from PIL import Image

"""
图像水印工具模块

该模块提供了为图像添加水印的功能，支持批量处理、自定义水印图片和透明度。
"""

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)  # 配置日志记录器
class Watermarker:
    """
    水印处理类，负责水印的叠加
    
    属性：
        watermark_path (str): 水印图片路径
        opacity (float): 水印透明度 (0.0 - 1.0)
        output_folder (str): 输出文件夹路径
    """
    def __init__(self, watermark_path: str, opacity: float, output_folder: Optional[str] = None):
        """
        初始化Watermarker实例
        
        Args:
            watermark_path (str): 水印图片路径
            opacity (float): 水印透明度 (0.0 - 1.0)
            output_folder (Optional[str]): 输出文件夹路径
        """
        self.opacity = opacity
        self.output_folder = output_folder
        
        # 加载水印图片
        self.watermark = Image.open(watermark_path).convert('RGBA')
        
        # 创建输出文件夹
        if output_folder is not None:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

    def resize_image(self, image: Image.Image, target_width: int = 800) -> Image.Image:
        """调整图片大小，保持宽高比"""
        width_percent = target_width / float(image.size[0])
        target_height = int(float(image.size[1]) * width_percent)
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

    def create_watermark_layer(self, target_size: tuple) -> Image.Image:
        """创建水印层，重复平铺水印图片"""
        # 创建透明图层
        layer = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # 计算需要多少行和列的水印
        cols = math.ceil(target_size[0] / self.watermark.size[0])
        rows = math.ceil(target_size[1] / self.watermark.size[1])
        
        # 平铺水印
        for row in range(rows):
            for col in range(cols):
                x = col * self.watermark.size[0]
                y = row * self.watermark.size[1]
                layer.paste(self.watermark, (x, y))
        
        # 裁剪到目标大小
        layer = layer.crop((0, 0, target_size[0], target_size[1]))
        
        # 调整透明度
        if self.opacity < 1.0:
            layer.putalpha(Image.eval(layer.getchannel('A'), 
                                    lambda x: int(x * self.opacity)))
        
        return layer

    def add_watermark(self, image: Image.Image) -> Image.Image:
        """为单个图片添加水印"""
        # 调整图片大小
        image = self.resize_image(image)
        
        # 确保图片是RGBA模式
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 创建水印层
        watermark_layer = self.create_watermark_layer(image.size)
        
        # 合并图片和水印
        return Image.alpha_composite(image, watermark_layer)

    def process_single_image(self, image_path: str) -> Optional[Image.Image]:
        """处理单个图片"""
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 添加水印
            watermarked = self.add_watermark(image)
            
            # 如果指定了输出文件夹，则保存图片
            if self.output_folder:
                output_path = os.path.join(
                    self.output_folder,
                    os.path.basename(image_path)
                )
                
                # 如果原图是JPEG，转换回RGB模式
                if image_path.lower().endswith(('.jpg', '.jpeg')):
                    watermarked = watermarked.convert('RGB')
                
                watermarked.save(output_path, quality=95)
            
            return watermarked
            
        except Exception as e:
            logger.error(f"处理图片 {image_path} 时出错: {str(e)}")
            return None

    def process_images(self, folder: str):
        """处理文件夹中的所有图片"""
        if not self.output_folder:
            self.output_folder = os.path.join(folder, 'watermarked')
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
                
        # 获取所有图片文件
        image_files = self.get_image_files(folder)
        
        # 处理每个图片
        for image_file in image_files:
            self.process_single_image(image_file)
    
    def get_image_files(self, folder: str) -> List[str]:
        """获取指定文件夹内所有支持的图片文件"""
        supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"]
        return [
            os.path.join(folder, f)
            for f in os.listdir(folder)
        ]
