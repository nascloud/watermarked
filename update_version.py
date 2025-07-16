#!/usr/bin/env python3
"""
版本更新工具

使用方法：
    python update_version.py 2.1.0           # 设置完整版本号
    python update_version.py --major         # 增加主版本号
    python update_version.py --minor         # 增加次版本号  
    python update_version.py --patch         # 增加修订号
    python update_version.py --show          # 显示当前版本
"""

import argparse
import re
import sys
from pathlib import Path


def read_version_file():
    """读取当前版本信息"""
    version_file = Path("version.py")
    if not version_file.exists():
        print("错误: version.py 文件不存在")
        sys.exit(1)
    
    content = version_file.read_text(encoding='utf-8')
    
    # 提取版本号
    version_match = re.search(r'VERSION = ["\']([^"\']+)["\']', content)
    if not version_match:
        print("错误: 无法在 version.py 中找到 VERSION 变量")
        sys.exit(1)
    
    version = version_match.group(1)
    
    # 解析版本号
    parts = version.split('.')
    if len(parts) != 3:
        print(f"错误: 版本号格式不正确: {version}")
        sys.exit(1)
    
    try:
        major, minor, patch = map(int, parts)
        return major, minor, patch, content
    except ValueError:
        print(f"错误: 版本号包含非数字字符: {version}")
        sys.exit(1)


def write_version_file(major, minor, patch, original_content):
    """写入新的版本信息"""
    new_version = f"{major}.{minor}.{patch}"

    # 更新 VERSION 变量
    new_content = re.sub(
        r'VERSION = ["\'][^"\']+["\']',
        f'VERSION = "{new_version}"',
        original_content
    )

    # 更新 VERSION_INFO 字典
    new_content = re.sub(
        r'"major": \d+',
        f'"major": {major}',
        new_content
    )
    new_content = re.sub(
        r'"minor": \d+',
        f'"minor": {minor}',
        new_content
    )
    new_content = re.sub(
        r'"patch": \d+',
        f'"patch": {patch}',
        new_content
    )

    # 更新 APP_TITLE
    new_content = re.sub(
        r'APP_TITLE = f["\'][^"\']*["\']',
        f'APP_TITLE = f"{{APP_NAME}} {{VERSION}}"',
        new_content
    )

    # 写入 version.py 文件
    version_file = Path("version.py")
    version_file.write_text(new_content, encoding='utf-8')

    # 同时更新 pyproject.toml 中的版本号
    update_pyproject_toml(new_version)

    print(f"版本已更新为: {new_version}")
    return new_version


def update_pyproject_toml(new_version):
    """更新 pyproject.toml 中的版本号"""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print("警告: pyproject.toml 文件不存在，跳过更新")
        return

    try:
        content = pyproject_file.read_text(encoding='utf-8')

        # 更新版本号
        updated_content = re.sub(
            r'version = ["\'][^"\']+["\']',
            f'version = "{new_version}"',
            content
        )

        pyproject_file.write_text(updated_content, encoding='utf-8')
        print(f"已同步更新 pyproject.toml 中的版本号")

    except Exception as e:
        print(f"警告: 更新 pyproject.toml 失败: {e}")


def show_current_version():
    """显示当前版本信息"""
    try:
        from version import get_version, get_app_title, get_build_info
        print(f"当前版本: {get_version()}")
        print(f"应用标题: {get_app_title()}")
        
        build_info = get_build_info()
        print(f"应用名称: {build_info['name']}")
        print(f"描述: {build_info['description']}")
    except ImportError:
        major, minor, patch, _ = read_version_file()
        print(f"当前版本: {major}.{minor}.{patch}")


def main():
    parser = argparse.ArgumentParser(description="版本管理工具")
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument("version", nargs="?", help="设置完整版本号 (例如: 2.1.0)")
    group.add_argument("--major", action="store_true", help="增加主版本号")
    group.add_argument("--minor", action="store_true", help="增加次版本号")
    group.add_argument("--patch", action="store_true", help="增加修订号")
    group.add_argument("--show", action="store_true", help="显示当前版本")
    
    args = parser.parse_args()
    
    if args.show:
        show_current_version()
        return
    
    major, minor, patch, content = read_version_file()
    
    if args.version:
        # 设置完整版本号
        parts = args.version.split('.')
        if len(parts) != 3:
            print("错误: 版本号格式应为 major.minor.patch (例如: 2.1.0)")
            sys.exit(1)
        
        try:
            major, minor, patch = map(int, parts)
        except ValueError:
            print("错误: 版本号必须是数字")
            sys.exit(1)
    
    elif args.major:
        major += 1
        minor = 0
        patch = 0
    
    elif args.minor:
        minor += 1
        patch = 0
    
    elif args.patch:
        patch += 1
    
    new_version = write_version_file(major, minor, patch, content)
    
    print("\n提示:")
    print("- 版本号已更新，GUI 标题会自动使用新版本")
    print("- 如果使用 setuptools 打包，版本号会自动同步")
    print("- 建议提交代码前运行测试确保一切正常")


if __name__ == "__main__":
    main()
