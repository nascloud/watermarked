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

    def test_resize_image_smaller_than_target(self):
        """测试当图片宽度小于目标宽度时进行放大以统一宽度"""
        # 创建一个白色的 50x100 像素图片
        original_image = Image.new('RGB', (50, 100), 'white')

        # 目标宽度为 100（大于原图宽度）
        target_width = 100
        resized_image = resize_image(original_image, target_width)

        # 应该放大到目标宽度，保持宽高比
        self.assertEqual(resized_image.size[0], target_width)
        expected_height = int(original_image.size[1] * (target_width / original_image.size[0]))
        self.assertEqual(resized_image.size[1], expected_height)

    def test_resize_image_same_width(self):
        """测试当图片宽度等于目标宽度时不进行缩放"""
        # 创建一个白色的 100x200 像素图片
        original_image = Image.new('RGB', (100, 200), 'white')

        # 目标宽度为 100（等于原图宽度）
        target_width = 100
        resized_image = resize_image(original_image, target_width)

        # 应该返回原图，不进行缩放
        self.assertEqual(resized_image.size, original_image.size)

    def test_resize_image_large_upscale(self):
        """测试大幅放大时的优化算法"""
        # 创建一个小图片
        original_image = Image.new('RGB', (100, 100), 'white')

        # 目标宽度为 400（4倍放大）
        target_width = 400
        resized_image = resize_image(original_image, target_width)

        # 检查尺寸是否正确
        self.assertEqual(resized_image.size[0], target_width)
        expected_height = int(original_image.size[1] * (target_width / original_image.size[0]))
        self.assertEqual(resized_image.size[1], expected_height)

        # 验证返回的是新图片对象（不是原图）
        self.assertIsNot(resized_image, original_image)

    def test_resize_image_downscale(self):
        """测试缩小图片的功能"""
        # 创建一个大图片
        original_image = Image.new('RGB', (800, 600), 'white')

        # 目标宽度为 400（缩小一半）
        target_width = 400
        resized_image = resize_image(original_image, target_width)

        # 检查尺寸是否正确
        self.assertEqual(resized_image.size[0], target_width)
        expected_height = int(original_image.size[1] * (target_width / original_image.size[0]))
        self.assertEqual(resized_image.size[1], expected_height)

if __name__ == '__main__':
    unittest.main()