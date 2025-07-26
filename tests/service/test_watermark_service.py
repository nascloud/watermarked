import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
from config.settings import AppConfig
from service.watermark_service import WatermarkService

class TestWatermarkService(unittest.TestCase):

    def setUp(self):
        """设置模拟的 AppConfig 和 WatermarkService 实例"""
        self.mock_config = MagicMock(spec=AppConfig)
        self.mock_config.get.side_effect = self.mock_config_get
        self.config_data = {
            "watermark_path": "path/to/watermark.png",
            "opacity": 0.5,
            "target_width": 800,
            "width_option": "uniform",
            "input_folder": "path/to/input",
            "output_folder": "path/to/output"
        }
        self.service = WatermarkService(self.mock_config)

    def mock_config_get(self, key, default=None):
        """模拟 AppConfig.get 方法"""
        return self.config_data.get(key, default)

    def test_initialization(self):
        """测试 WatermarkService 是否正确初始化"""
        self.assertIsNotNone(self.service)
        self.assertEqual(self.service.config, self.mock_config)

    @patch('service.watermark_service.Image.open')
    @patch('service.watermark_service.apply_watermark')
    @patch('service.watermark_service.resize_image')
    def test_create_preview(self, mock_resize_image, mock_apply_watermark, mock_image_open):
        """测试创建预览的功能"""
        # 模拟图片和水印
        mock_image = Image.new('RGB', (100, 100), 'white')
        mock_watermark = Image.new('RGBA', (10, 10), (255, 0, 0, 255))
        mock_resized_image = Image.new('RGB', (800, 800), 'white')

        # 设置模拟返回值
        mock_image_open.return_value = mock_image
        mock_resize_image.return_value = mock_resized_image

        # 模拟 _get_watermark_image 方法
        with patch.object(self.service, '_get_watermark_image', return_value=mock_watermark):
            # 模拟 apply_watermark 返回一个新图片
            mock_final_image = Image.new('RGBA', (800, 800), (255, 255, 255, 255))
            mock_apply_watermark.return_value = mock_final_image

            # 调用 create_preview
            preview_image = self.service.create_preview("dummy_path.jpg")

            # 断言
            self.assertIsNotNone(preview_image)
            mock_image_open.assert_called_once_with("dummy_path.jpg")
            mock_resize_image.assert_called_once_with(mock_image, 800)
            mock_apply_watermark.assert_called_once_with(
                mock_resized_image, mock_watermark, self.config_data['opacity']
            )
            self.assertEqual(preview_image, mock_final_image)

if __name__ == '__main__':
    unittest.main()