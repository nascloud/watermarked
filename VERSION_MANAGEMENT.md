# 版本管理说明

本项目使用统一的版本管理系统，让你可以在一个地方管理版本号，并在整个项目中自动使用。

## 文件结构

```
├── version.py              # 版本信息定义文件（主要配置文件）
├── update_version.py       # 版本更新工具
├── build.py               # 构建脚本示例
└── VERSION_MANAGEMENT.md  # 本说明文档
```

## 核心文件：version.py

这是版本管理的核心文件，包含：

- `VERSION`: 主版本号字符串
- `VERSION_INFO`: 详细版本信息字典
- `APP_NAME`: 应用程序名称
- `APP_TITLE`: 完整应用标题（名称 + 版本）
- `BUILD_INFO`: 构建信息

## 使用方法

### 1. 查看当前版本

```bash
uv run python update_version.py --show
```

### 2. 更新版本号

#### 设置完整版本号
```bash
uv run python update_version.py 2.1.0
```

#### 增量更新
```bash
# 增加主版本号 (2.1.0 -> 3.0.0)
uv run python update_version.py --major

# 增加次版本号 (2.1.0 -> 2.2.0)  
uv run python update_version.py --minor

# 增加修订号 (2.1.0 -> 2.1.1)
uv run python update_version.py --patch
```

### 3. 在代码中使用版本信息

```python
from version import get_version, get_app_title, get_build_info

# 获取版本号
version = get_version()  # "2.4.0"

# 获取应用标题
title = get_app_title()  # "批量加水印工具 2.4.0"

# 获取构建信息
info = get_build_info()
```

### 4. 构建和打包

#### 使用构建脚本
```bash
# 查看构建选项
uv run python build.py --help

# 清理构建目录
uv run python build.py --clean

# 使用 PyInstaller 构建可执行文件
uv run python build.py --pyinstaller

# 创建发布说明
uv run python build.py --release-notes

# 执行完整构建流程
uv run python build.py --all
```

#### 手动使用 PyInstaller
```bash
# 版本号会自动包含在文件名中
pyinstaller --onefile --windowed --name "批量加水印工具-2.1.0" watermark_gui.py
```

## 自动化集成

### GUI 应用标题
GUI 窗口标题会自动使用版本信息：

```python
# watermark_gui.py
from version import get_app_title

self.window.title(get_app_title())  # 自动显示 "批量加水印工具 2.4.0"
```

### setuptools 集成
`pyproject.toml` 配置为使用固定版本号，版本更新工具会自动同步：

```toml
[project]
name = "watermarked"
version = "2.1.0"  # 自动与 version.py 同步
description = "一个用于批量添加水印的图片处理工具"
```

版本更新时，`update_version.py` 会同时更新两个文件中的版本号。

## 版本号规范

本项目使用 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

格式：`主版本号.次版本号.修订号`

例如：`2.1.0`

## 发布流程建议

1. **开发完成后更新版本号**
   ```bash
   uv run python update_version.py --minor  # 或其他适当的更新
   ```

2. **测试应用程序**
   ```bash
   uv run python watermark_gui.py
   ```

3. **构建发布版本**
   ```bash
   uv run python build.py --all
   ```

4. **提交代码**
   ```bash
   git add .
   git commit -m "Release v$(uv run python -c 'from version import get_version; print(get_version())')"
   git tag v$(uv run python -c 'from version import get_version; print(get_version())')
   ```

## 自定义配置

你可以根据需要修改 `version.py` 中的配置：

- 修改应用程序名称
- 添加预发布版本标识
- 更新构建信息
- 添加其他元数据

## 注意事项

1. **只修改 version.py**：所有版本相关的修改都应该在 `version.py` 中进行
2. **使用工具更新**：建议使用 `update_version.py` 工具而不是手动编辑
3. **测试验证**：更新版本后记得测试应用程序是否正常工作
4. **提交版本标签**：发布时建议创建 git 标签以便追踪

## 故障排除

### 版本号不显示
- 检查 `version.py` 文件是否存在
- 确认导入语句是否正确
- 验证 `VERSION` 变量格式是否正确

### 构建失败
- 确认所需的构建工具已安装（如 PyInstaller）
- 检查文件路径是否正确
- 查看错误信息并相应调整

### 版本不同步
- 确认所有引用版本的地方都使用了 `version.py` 中的函数
- 重新运行 `update_version.py` 确保所有地方都已更新
