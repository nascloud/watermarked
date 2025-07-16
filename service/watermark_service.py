import os
import logging
from typing import List, Optional, Callable
from PIL import Image
from config.settings import AppConfig
from core.watermark_algorithm import apply_watermark, resize_image

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class WatermarkService:
    """
    水印服务类，封装了所有与水印处理相关的业务逻辑。

    该服务依赖于 AppConfig 来获取配置，并使用 core 中的算法来处理图像。
    它负责处理单个图像预览、批量处理文件夹中的图像等操作。
    """
    def __init__(self, config: AppConfig):
        """
        初始化 WatermarkService。

        Args:
            config (AppConfig): 应用程序的配置实例。
        """
        self.config = config

    def create_preview(self, image_path: str) -> Optional[Image.Image]:
        """
        为指定的单个图片创建水印预览。

        此方法会按照与实际处理相同的顺序：先统一宽度，再添加水印。
        如果水印未设置，则返回调整宽度后的图片。

        Args:
            image_path (str): 要创建预览的图片的路径。

        Returns:
            Optional[Image.Image]: 处理后的预览图像对象，如果发生错误则返回 None。

        Raises:
            Exception: 如果在处理过程中发生任何错误。
        """
        try:
            image = Image.open(image_path)

            # 第一步：根据配置统一图像宽度（与实际处理保持一致）
            target_width = self.config.get('target_width')
            if self.config.get('width_option') == 'uniform':
                image = resize_image(image, target_width)

            # 第二步：添加水印
            watermark_image = self._get_watermark_image()
            if not watermark_image:
                return image  # 如果没有水印，返回调整宽度后的图片

            return apply_watermark(
                image,
                watermark_image,
                self.config.get('opacity')
            )
        except Exception as e:
            logger.error(f"创建预览失败: {e}")
            raise

    def process_images_with_progress(self, progress_callback: Callable[[int, int, str], None]):
        """
        批量处理指定输入文件夹中的所有图片，并实时报告进度。

        此方法会遍历输入文件夹中的所有支持的图片格式，为每张图片添加水印，
        并将其保存到输出文件夹。

        Args:
            progress_callback (Callable[[int, int, str], None]):
                一个回调函数，用于在处理过程中报告进度。
                它接收三个参数：(当前处理的文件序号, 总文件数, 当前文件名)。
        
        Raises:
            ValueError: 如果输入文件夹未在配置中设置。
        """
        input_folder = self.config.get('input_folder')
        output_folder = self.config.get('output_folder')

        if not input_folder:
            raise ValueError("输入文件夹未设置")
        
        if not output_folder:
            output_folder = os.path.join(input_folder, 'watermarked')
            self.config.update(output_folder=output_folder)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        image_files = self._get_image_files(input_folder)
        total_files = len(image_files)

        for i, image_path in enumerate(image_files, 1):
            try:
                self.process_single_image(image_path)
                progress_callback(i, total_files, os.path.basename(image_path))
            except Exception as e:
                logger.error(f"处理文件 {os.path.basename(image_path)} 失败: {e}")

    def process_single_image(self, image_path: str):
        """
        处理单个图片文件：先统一宽度，再添加水印，最后保存到输出目录。

        处理顺序：
        1. 加载原始图片
        2. 根据配置统一图片宽度（如果需要）
        3. 添加水印
        4. 保存到输出文件夹

        Args:
            image_path (str): 要处理的图片的完整路径。

        Raises:
            Exception: 如果在打开、处理或保存图片时发生错误。
        """
        try:
            image = Image.open(image_path)

            # 第一步：根据配置统一图像宽度
            target_width = self.config.get('target_width')
            if self.config.get('width_option') == 'uniform':
                image = resize_image(image, target_width)

            # 第二步：添加水印
            watermark_image = self._get_watermark_image()
            if watermark_image:
                image = apply_watermark(
                    image,
                    watermark_image,
                    self.config.get('opacity')
                )

            # 第三步：保存图片
            output_path = os.path.join(self.config.get('output_folder'), os.path.basename(image_path))

            # 对于有损格式，确保在保存前转换为 RGB
            if image_path.lower().endswith(('.jpg', '.jpeg')):
                if image.mode == 'RGBA':
                    image = image.convert('RGB')

            image.save(output_path, quality=95)

        except Exception as e:
            logger.error(f"处理图片 {image_path} 时出错: {str(e)}")
            raise

    def _get_watermark_image(self) -> Optional[Image.Image]:
        """
        根据配置加载水印图片。

        如果未设置水印路径或文件不存在，则返回 None。
        加载的图片会被转换为 RGBA 模式以支持透明度。

        Returns:
            Optional[Image.Image]: 加载的水印图片对象，或在失败时返回 None。
        """
        watermark_path = self.config.get('watermark_path')
        if not watermark_path or not os.path.exists(watermark_path):
            return None
        try:
            return Image.open(watermark_path).convert('RGBA')
        except Exception as e:
            logger.error(f"加载水印图片失败: {e}")
            return None

    def _get_image_files(self, folder: str) -> List[str]:
        """
        获取指定文件夹内所有支持格式的、有效的图片文件列表。

        此方法会检查文件扩展名，并尝试打开和验证每个图片文件，
        以过滤掉损坏或无效的图片。

        Args:
            folder (str): 要搜索的文件夹路径。

        Returns:
            List[str]: 包含所有有效图片文件完整路径的列表。
        """
        supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"]
        valid_images = []
        if not os.path.isdir(folder):
            return []
        for f in os.listdir(folder):
            if os.path.splitext(f)[1].lower() in supported_formats:
                file_path = os.path.join(folder, f)
                try:
                    # 确保是文件而不是子目录
                    if os.path.isfile(file_path):
                        with Image.open(file_path) as img:
                            img.verify()  # 验证图片文件是否完整
                        valid_images.append(file_path)
                except Exception as e:
                    logger.warning(f"跳过无效或损坏的图片: {f} - {e}")
        return valid_images