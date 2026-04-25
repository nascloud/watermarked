import json
import os
from typing import Any, Dict

class AppConfig:
    """
    应用配置管理类，负责加载、验证和提供配置。

    该类处理配置文件的读取、写入、验证和默认值设置。
    配置文件存储在用户本地的 AppData 目录中。
    """
    def __init__(self):
        """
        初始化 AppConfig 实例。

        - 创建配置目录（如果不存在）。
        - 设置配置文件路径。
        - 加载现有配置或创建默认配置。
        """
        appdata_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "watermark")
        os.makedirs(appdata_path, exist_ok=True)
        self.config_path = os.path.join(appdata_path, 'watermark_config.json')
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """
        从 JSON 文件加载配置。

        如果文件不存在或解析失败，则会加载一个空配置，
        然后由 _set_defaults() 设置默认值。
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置失败: {e}")
                self.config = {}  # 如果加载失败，则使用空配置
        self._set_defaults()

    def _set_defaults(self):
        """
        为缺失的配置项设置默认值。

        这确保了应用总有可用的基本配置。
        """
        defaults = {
            "watermark_path": "",
            "opacity": 1.0,
            "target_width": 1440,
            "width_option": "original",
            "output_width_option": "original",
            "output_target_width": 1440,
            "input_folder": "",
            "output_folder": ""
        }
        for key, value in defaults.items():
            self.config.setdefault(key, value)

    def _validate(self):
        """
        验证关键配置项的类型和值范围。

        在更新配置时调用，以确保配置的有效性。

        Raises:
            ValueError: 如果配置项无效。
            FileNotFoundError: 如果水印文件路径指定但文件不存在。
        """
        if not isinstance(self.get('opacity'), (float, int)) or not (0.0 <= self.get('opacity') <= 1.0):
            raise ValueError("配置 'opacity' 必须是 0.0 到 1.0 之间的数字")

        if not isinstance(self.get('target_width'), int) or self.get('target_width') <= 0:
            raise ValueError("配置 'target_width' 必须是正整数")

        if not isinstance(self.get('output_target_width'), int) or self.get('output_target_width') <= 0:
            raise ValueError("配置 'output_target_width' 必须是正整数")

        if self.get('width_option') not in ["uniform", "original"]:
            raise ValueError("配置 'width_option' 必须是 'uniform' 或 'original'")

        if self.get('output_width_option') not in ["uniform", "original"]:
            raise ValueError("配置 'output_width_option' 必须是 'uniform' 或 'original'")

        watermark_path = self.get('watermark_path')
        if watermark_path and not os.path.isfile(watermark_path):
            raise FileNotFoundError(f"水印文件未找到: {watermark_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取一个配置项的值。

        Args:
            key (str): 配置项的键。
            default (Any, optional): 如果键不存在时返回的默认值。 Defaults to None.

        Returns:
            Any: 配置项的值。
        """
        return self.config.get(key, default)

    def update(self, **kwargs: Any):
        """
        更新一个或多个配置项。

        更新后会立即调用 _validate() 来验证新配置的有效性。

        Args:
            **kwargs: 要更新的键值对。
        """
        for key, value in kwargs.items():
            self.config[key] = value
        self._validate()  # 更新后立即验证

    def save(self):
        """
        将当前配置保存到 JSON 文件。

        Raises:
            IOError: 如果文件写入失败。
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise IOError(f"保存配置失败: {e}")
