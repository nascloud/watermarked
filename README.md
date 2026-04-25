# 批量加水印工具 (Watermark Tool)

一个用于批量添加水印的图片处理工具，支持多种图片格式和智能图像缩放。

## 功能特性

### 核心功能
- **批量添加水印** - 一次处理多张图片，支持子目录递归
- **多种图片格式** - 支持 JPG, PNG, BMP, GIF, TIFF, WebP 等
- **透明度调节** - 0-100% 透明度可调
- **统一输出宽度** - 自动调整图片尺寸，保持宽高比
- **实时预览** - 所见即所得的效果预览

### 智能处理
- **AI超分辨率放大** - 小图放大时使用边缘引导超分辨率算法提升清晰度
- **智能缩放** - 根据缩放比例自动选择最佳算法
- **分步处理** - 大幅缩放时使用多步保持质量
- **细节增强** - 多级锐化保持边缘清晰度

### 技术特性
- **OpenCV加速** - 使用OpenCV进行高性能图像处理
- **边缘保持** - 优化算法保持图像边缘和细节
- **EXIF保留** - 保留原始图片的EXIF元数据

## 项目结构

```
watermarker/
├── core/                    # 核心算法
│   ├── ai_super_resolution.py  # AI超分辨率
│   └── watermark_algorithm.py # 水印算法
├── config/                   # 配置
│   ├── settings.py          # 设置管理
│   └── watermark_config.json
├── service/                 # 服务层
│   └── watermark_service.py
├── tests/                   # 测试
├── build.py                 # 构建脚本
├── version.py               # 版本管理
├── watermark_gui.py         # GUI主程序
└── main.py                 # 入口
```

## 开始使用

### 前置要求
- Python 3.13+
- Windows 10/11

### 安装运行

```bash
# 安装依赖
uv pip install -e .

# 运行程序
uv run python watermark_gui.py
```

### 构建可执行文件

```bash
uv run python build.py --pyinstaller
```

生成的文件在 `dist/` 目录。

## 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| watermark_path | 水印图片路径 | - |
| opacity | 水印透明度 | 1.0 |
| target_width | 统一宽度 | 1440 |
| upscale_algorithm | 放大算法 (edge/cubic/deep/lanczos) | edge |

## 放大算法

| 算法 | 说明 | 适用场景 |
|------|------|----------|
| edge | 边缘引导超分辨率（默认） | 通用场景，推荐 |
| cubic | Cubic插值+去噪+锐化 | 快速处理 |
| deep | 深度学习（需PyTorch） | 高质量需求 |
| lanczos | 传统LANCZOS | 对比测试 |

## 技术栈

- **Pillow** - 图像处理
- **OpenCV** - AI超分辨率
- **NumPy** - 数值计算
- **PyInstaller** - 打包分发

## 许可证

MIT License

## 作者

nascloud