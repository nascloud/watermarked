import math
from PIL import Image, ImageFilter

def resize_image(image: Image.Image, target_width: int) -> Image.Image:
    """
    按比例调整图像大小以适应目标宽度，同时保持其纵横比。

    当需要放大图片时，使用优化的算法来提高清晰度：
    - 对于小幅放大（<2倍），使用LANCZOS算法
    - 对于大幅放大（>=2倍），使用分步放大和锐化处理
    - 对于缩小，使用LANCZOS算法

    Args:
        image (Image.Image): Pillow Image 对象。
        target_width (int): 目标宽度（像素）。

    Returns:
        Image.Image: 调整大小后的 Pillow Image 对象。
    """
    # 如果图片宽度已经等于目标宽度，直接返回
    if image.width == target_width:
        return image

    # 计算缩放比例和新的高度
    ratio = target_width / image.width
    new_height = int(image.height * ratio)

    # 如果是缩小图片（ratio < 1），使用LANCZOS算法
    if ratio <= 1.0:
        return image.resize((target_width, new_height), Image.Resampling.LANCZOS)

    # 如果是放大图片，根据放大倍数选择不同策略
    if ratio < 2.0:
        # 小幅放大：直接使用LANCZOS算法
        resized = image.resize((target_width, new_height), Image.Resampling.LANCZOS)
        # 应用轻微锐化以增强细节
        return _apply_sharpening(resized, strength=0.3)
    else:
        # 大幅放大：使用分步放大策略
        return _progressive_upscale(image, target_width, new_height)

def _apply_sharpening(image: Image.Image, strength: float = 0.5) -> Image.Image:
    """
    对图像应用锐化滤镜以增强细节。

    Args:
        image (Image.Image): 要锐化的图像。
        strength (float): 锐化强度，0.0-1.0之间。

    Returns:
        Image.Image: 锐化后的图像。
    """
    if strength <= 0:
        return image

    # 创建锐化滤镜
    # 使用UnsharpMask滤镜，它比简单的锐化效果更好
    try:
        # 参数：radius=半径, percent=强度百分比, threshold=阈值
        sharpened = image.filter(ImageFilter.UnsharpMask(
            radius=1.0,
            percent=int(strength * 150),  # 将0-1映射到0-150%
            threshold=3
        ))
        return sharpened
    except Exception:
        # 如果UnsharpMask失败，使用简单的锐化
        return image.filter(ImageFilter.SHARPEN)

def _progressive_upscale(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    使用分步放大策略来提高大幅放大时的图像质量。

    分步放大可以减少插值伪影，保持更好的图像质量。

    Args:
        image (Image.Image): 原始图像。
        target_width (int): 目标宽度。
        target_height (int): 目标高度。

    Returns:
        Image.Image: 放大后的图像。
    """
    current_image = image
    current_width = image.width
    current_height = image.height

    # 计算总的放大倍数
    scale_factor = target_width / current_width

    # 如果放大倍数很大，分步进行
    while current_width < target_width:
        # 每次最多放大1.5倍，这样可以保持更好的质量
        step_scale = min(1.5, target_width / current_width)

        new_width = int(current_width * step_scale)
        new_height = int(current_height * step_scale)

        # 确保不超过目标尺寸
        if new_width > target_width:
            new_width = target_width
            new_height = target_height

        # 使用LANCZOS进行这一步的放大
        current_image = current_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 在每一步后应用轻微锐化
        if new_width < target_width:  # 不是最后一步
            current_image = _apply_sharpening(current_image, strength=0.2)

        current_width = new_width
        current_height = new_height

    # 最后一步应用更强的锐化
    return _apply_sharpening(current_image, strength=0.4)

def create_watermark_layer(target_size: tuple, watermark_image: Image.Image, opacity: float) -> Image.Image:
    """
    创建一个与目标图像大小相同的水印层。

    水印图像会以平铺的方式填充整个图层，并应用指定的不透明度。

    Args:
        target_size (tuple): (宽度, 高度) 的元组，表示目标图像的尺寸。
        watermark_image (Image.Image): 用作水印的 Pillow Image 对象。
        opacity (float): 水印的不透明度，范围从 0.0 (完全透明) 到 1.0 (完全不透明)。

    Returns:
        Image.Image: 创建好的水印层，为 RGBA 模式的 Pillow Image 对象。
    """
    layer = Image.new('RGBA', target_size, (0, 0, 0, 0))
    
    if watermark_image.size[0] == 0 or watermark_image.size[1] == 0:
        return layer

    cols = math.ceil(target_size[0] / watermark_image.size[0])
    rows = math.ceil(target_size[1] / watermark_image.size[1])
    
    for row in range(rows):
        for col in range(cols):
            x = col * watermark_image.size[0]
            y = row * watermark_image.size[1]
            layer.paste(watermark_image, (x, y))
    
    layer = layer.crop((0, 0, target_size[0], target_size[1]))
    
    if opacity < 1.0:
        alpha = layer.getchannel('A')
        alpha = Image.eval(alpha, lambda x: int(x * opacity))
        layer.putalpha(alpha)
    
    return layer

def apply_watermark(image: Image.Image, watermark_image: Image.Image, opacity: float) -> Image.Image:
    """
    为单个图片应用水印。

    此函数直接在传入的图片上添加水印，不进行大小调整。
    大小调整应该在调用此函数之前完成。

    Args:
        image (Image.Image): 需要添加水印的 Pillow Image 对象。
        watermark_image (Image.Image): 用作水印的 Pillow Image 对象。
        opacity (float): 水印的不透明度。

    Returns:
        Image.Image: 添加了水印的 Pillow Image 对象。
    """
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    watermark_layer = create_watermark_layer(image.size, watermark_image, opacity)

    return Image.alpha_composite(image, watermark_layer)