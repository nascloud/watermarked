import math
from PIL import Image

def resize_image(image: Image.Image, target_width: int) -> Image.Image:
    """
    按比例调整图像大小以适应目标宽度，同时保持其纵横比。

    无论原图宽度是大于还是小于目标宽度，都会调整到目标宽度，
    以实现真正的"统一宽度"效果。

    Args:
        image (Image.Image): Pillow Image 对象。
        target_width (int): 目标宽度（像素）。

    Returns:
        Image.Image: 调整大小后的 Pillow Image 对象。
    """
    # 如果图片宽度已经等于目标宽度，直接返回
    if image.width == target_width:
        return image

    # 计算新的高度，保持宽高比
    ratio = target_width / image.width
    new_height = int(image.height * ratio)

    return image.resize((target_width, new_height), Image.Resampling.LANCZOS)

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