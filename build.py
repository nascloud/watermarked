#!/usr/bin/env python3
"""
构建脚本

这个脚本展示了如何在构建/打包时使用版本信息。
你可以根据需要修改这个脚本来适应你的构建流程。
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from version import get_version, get_app_title, get_build_info


def print_build_info():
    """打印构建信息"""
    build_info = get_build_info()
    print("=" * 50)
    print("构建信息")
    print("=" * 50)
    print(f"应用名称: {build_info['name']}")
    print(f"版本号: {build_info['version']}")
    print(f"描述: {build_info['description']}")
    print(f"作者: {build_info['author']}")
    print(f"许可证: {build_info['license']}")
    print("=" * 50)


def clean_build():
    """清理构建目录"""
    print("清理构建目录...")

    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for dir_pattern in dirs_to_clean:
        for path in Path('.').glob(dir_pattern):
            try:
                if path.is_dir():
                    print(f"删除目录: {path}")
                    shutil.rmtree(path, ignore_errors=True)
                elif path.is_file():
                    print(f"删除文件: {path}")
                    path.unlink()
            except (PermissionError, OSError) as e:
                print(f"警告: 无法删除 {path}: {e}")
                continue


def build_with_pyinstaller():
    """使用 PyInstaller 构建可执行文件"""
    print("使用 PyInstaller 构建可执行文件...")

    version = get_version()
    # 使用英文文件名避免编码问题
    exe_name = f"WatermarkTool-{version}"

    # PyInstaller 命令 - 使用python -m PyInstaller避免路径问题
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # Windows 下不显示控制台
        '--name', exe_name,             # 可执行文件名称（使用英文）
        '--add-data', 'config;config',  # 包含配置目录
        '--clean',                      # 清理临时文件
        'watermark_gui.py'              # 主程序文件
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"构建成功! 可执行文件位于: dist/{exe_name}.exe")

        # 创建一个带中文名的副本
        chinese_name = f"批量加水印工具-{version}.exe"
        src_path = Path(f"dist/{exe_name}.exe")
        dst_path = Path(f"dist/{chinese_name}")

        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            print(f"已创建中文名副本: dist/{chinese_name}")

    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        return False
    except FileNotFoundError:
        print("错误: 未找到 PyInstaller。请先安装: pip install pyinstaller")
        return False

    return True


def build_with_setuptools():
    """使用 setuptools 构建分发包"""
    print("使用 setuptools 构建分发包...")

    try:
        # 使用 build 模块构建（现代方式）
        try:
            subprocess.run([sys.executable, '-m', 'build'], check=True)
            print("构建成功! 分发包位于 dist/ 目录")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 如果没有 build 模块，尝试使用 pip
            print("尝试使用 pip 构建...")
            subprocess.run([sys.executable, '-m', 'pip', 'wheel', '.', '--wheel-dir', 'dist'], check=True)
            print("构建成功! wheel 包位于 dist/ 目录")

    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print("提示: 可以尝试安装 build 模块: pip install build")
        return False
    except FileNotFoundError:
        print("错误: 未找到必要的构建工具")
        return False

    return True


def create_release_notes():
    """创建发布说明"""
    version = get_version()
    build_info = get_build_info()
    
    release_notes = f"""# {build_info['name']} v{version}

## 版本信息
- 版本号: {version}
- 发布日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}

## 功能特性
- 批量添加水印到图片
- 支持多种图片格式
- 可调节水印透明度
- 统一输出图片宽度
- 实时预览效果

## 系统要求
- Python {sys.version_info.major}.{sys.version_info.minor}+
- PIL/Pillow 库

## 安装说明
1. 下载对应平台的可执行文件
2. 双击运行即可使用

## 更新日志
- 修改了统一输出宽度的处理逻辑，新逻辑为先统一宽度再添加水印
- 添加了版本管理系统
- 优化了用户界面

---
构建时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    release_file = Path(f"RELEASE-{version}.md")
    release_file.write_text(release_notes, encoding='utf-8')
    print(f"发布说明已创建: {release_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="构建脚本")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--pyinstaller", action="store_true", help="使用 PyInstaller 构建")
    parser.add_argument("--setuptools", action="store_true", help="使用 setuptools 构建")
    parser.add_argument("--release-notes", action="store_true", help="创建发布说明")
    parser.add_argument("--all", action="store_true", help="执行完整构建流程")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print_build_info()
    
    if args.clean or args.all:
        clean_build()
    
    if args.pyinstaller or args.all:
        if not build_with_pyinstaller():
            sys.exit(1)
    
    if args.setuptools or args.all:
        if not build_with_setuptools():
            sys.exit(1)
    
    if args.release_notes or args.all:
        create_release_notes()
    
    print("\n构建完成!")


if __name__ == "__main__":
    main()
