import math
from PIL import Image

def resize_image(image: Image.Image, max_size: tuple = (800, 800)) -> Image.Image:
    """
    按比例调整图像大小以适应最大尺寸，同时保持其纵横比。

    Args:
        image (Image.Image): Pillow Image 对象。
        max_size (tuple, optional): (宽度, 高度) 的元组，表示最大尺寸。
                                    默认为 (800, 800)。

    Returns:
        Image.Image: 调整大小后的 Pillow Image 对象。
    """
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image

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

def apply_watermark(image: Image.Image, watermark_image: Image.Image, opacity: float, max_size: tuple = (800, 800)) -> Image.Image:
    """
    为单个图片应用水印。

    此函数会先调整原图大小，然后创建一个水印层，最后将水印层合成到原图上。

    Args:
        image (Image.Image): 需要添加水印的 Pillow Image 对象。
        watermark_image (Image.Image): 用作水印的 Pillow Image 对象。
        opacity (float): 水印的不透明度。
        max_size (tuple, optional): 添加水印前，原图将被调整到的最大尺寸。
                                     默认为 (800, 800)。

    Returns:
        Image.Image: 添加了水印的 Pillow Image 对象。
    """
    image = resize_image(image, max_size)
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    watermark_layer = create_watermark_layer(image.size, watermark_image, opacity)
    
    return Image.alpha_composite(image, watermark_layer)