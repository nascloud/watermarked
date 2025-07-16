"""
版本管理模块

在这里统一管理应用程序的版本信息。
修改版本号时，只需要更新这个文件中的 VERSION 变量即可。
"""

# 主版本号.次版本号.修订号
VERSION = "2.1.0"

# 版本信息
VERSION_INFO = {
    "major": 2,
    "minor": 1,
    "patch": 0,
    "pre_release": None,  # 例如: "alpha", "beta", "rc1" 等
}

# 应用程序名称
APP_NAME = "批量加水印工具"

# 完整的应用程序标题（包含版本号）
APP_TITLE = f"{APP_NAME} {VERSION}"

# 构建信息（可选，用于调试）
BUILD_INFO = {
    "name": APP_NAME,
    "version": VERSION,
    "description": "一个用于批量添加水印的图片处理工具",
    "author": "开发者",
    "license": "MIT",
}


def get_version():
    """
    获取版本号字符串
    
    Returns:
        str: 版本号，例如 "2.1.0"
    """
    return VERSION


def get_version_info():
    """
    获取详细的版本信息
    
    Returns:
        dict: 包含版本各部分信息的字典
    """
    return VERSION_INFO.copy()


def get_app_title():
    """
    获取应用程序完整标题
    
    Returns:
        str: 应用程序标题，例如 "批量加水印工具 2.1.0"
    """
    return APP_TITLE


def get_build_info():
    """
    获取构建信息
    
    Returns:
        dict: 包含应用程序构建信息的字典
    """
    return BUILD_INFO.copy()


def format_version(include_pre_release=True):
    """
    格式化版本号
    
    Args:
        include_pre_release (bool): 是否包含预发布版本信息
        
    Returns:
        str: 格式化的版本号
    """
    version = f"{VERSION_INFO['major']}.{VERSION_INFO['minor']}.{VERSION_INFO['patch']}"
    
    if include_pre_release and VERSION_INFO.get('pre_release'):
        version += f"-{VERSION_INFO['pre_release']}"
    
    return version


# 兼容性：为了向后兼容，提供一些常用的变量
__version__ = VERSION
__title__ = APP_TITLE
