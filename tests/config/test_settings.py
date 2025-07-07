import unittest
import os
import json
from unittest.mock import patch, mock_open
from config.settings import AppConfig

class TestAppConfig(unittest.TestCase):

    def setUp(self):
        """在每个测试前设置模拟的配置文件路径"""
        self.mock_config_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "watermark_test")
        os.makedirs(self.mock_config_dir, exist_ok=True)
        self.mock_config_path = os.path.join(self.mock_config_dir, 'watermark_config.json')

    def tearDown(self):
        """在每个测试后清理模拟的配置文件和目录"""
        if os.path.exists(self.mock_config_path):
            os.remove(self.mock_config_path)
        if os.path.exists(self.mock_config_dir):
            os.rmdir(self.mock_config_dir)

    @patch('os.path.expanduser')
    def test_load_valid_config(self, mock_expanduser):
        """测试加载有效的配置文件"""
        mock_expanduser.return_value = os.path.join(self.mock_config_dir, "..", "..", "..") # Mock a different user home
        
        config_data = {"opacity": 0.8, "target_width": 1000}
        with open(self.mock_config_path, 'w') as f:
            json.dump(config_data, f)

        with patch.object(AppConfig, '__init__', lambda s: None):
            config = AppConfig()
            config.config_path = self.mock_config_path
            config.config = {}
            config.load()
            self.assertEqual(config.get('opacity'), 0.8)
            self.assertEqual(config.get('target_width'), 1000)

    def test_validate_invalid_opacity(self):
        """测试无效的 opacity 配置是否会引发 ValueError"""
        with patch.object(AppConfig, '__init__', lambda s: None):
            config = AppConfig()
            config.config = {"opacity": 1.5}
            with self.assertRaises(ValueError):
                config._validate()

    def test_validate_invalid_width_option(self):
        """测试无效的 width_option 配置是否会引发 ValueError"""
        with patch.object(AppConfig, '__init__', lambda s: None):
            config = AppConfig()
            config.config = {"width_option": "invalid_option", "opacity": 0.5, "target_width": 800}
            with self.assertRaises(ValueError):
                config._validate()

if __name__ == '__main__':
    unittest.main()