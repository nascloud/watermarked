import unittest
from PIL import Image
from core.watermark_algorithm import resize_image

class TestWatermarkAlgorithm(unittest.TestCase):

    def test_resize_image(self):
        """测试图片缩放功能"""
        # 创建一个白色的 100x200 像素图片
        original_image = Image.new('RGB', (100, 200), 'white')
        
        # 目标宽度为 50
        target_width = 50
        resized_image = resize_image(original_image, target_width)
        
        # 检查缩放后的宽度
        self.assertEqual(resized_image.size[0], target_width)
        
        # 检查缩放后的高度是否保持了宽高比
        expected_height = int(original_image.size[1] * (target_width / original_image.size[0]))
        self.assertEqual(resized_image.size[1], expected_height)

if __name__ == '__main__':
    unittest.main()