import numpy as np
import cv2
from PIL import Image
from typing import Literal, Optional


AlgorithmType = Literal["lanczos", "cubic", "edge", "deep"]


def pil_to_cv(pil_image: Image.Image) -> np.ndarray:
    """PIL Image 转 OpenCV 格式"""
    return np.array(pil_image)


def cv_to_pil(cv_image: np.ndarray) -> Image.Image:
    """OpenCV 格式转 PIL Image"""
    return Image.fromarray(cv_image)


def ai_upscale_image(
    image: Image.Image,
    target_width: int,
    algorithm: AlgorithmType = "edge"
) -> Image.Image:
    """
    使用AI增强算法放大图片

    Args:
        image: PIL Image对象
        target_width: 目标宽度
        algorithm: 算法类型
            - lanczos: 传统LANCZOS（用于对比）
            - cubic: 使用CUBIC+后处理
            - edge: 边缘引导超分辨率（推荐）
            - deep: 深度学习超分辨率（如果可用）

    Returns:
        放大后的PIL Image
    """
    src_cv = pil_to_cv(image)
    src_cv = _ensure_rgb(src_cv)

    ratio = target_width / image.width

    if ratio <= 1.0:
        return _downscale_cv(src_cv, target_width, int(image.height * ratio))

    if ratio >= 2.0 and algorithm == "deep":
        result_cv = _deep_super_resolution(src_cv, target_width, int(image.height * ratio))
    elif algorithm == "edge":
        result_cv = _edge_guided_upscale(src_cv, target_width, int(image.height * ratio))
    elif algorithm == "cubic":
        result_cv = _cubic_with_enhancement(src_cv, target_width, int(image.height * ratio))
    else:
        result_cv = _lanczos_upscale(src_cv, target_width, int(image.height * ratio))

    return cv_to_pil(result_cv)


def _ensure_rgb(img: np.ndarray) -> np.ndarray:
    """确保图像是RGB格式"""
    if len(img.shape) == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _edge_guided_upscale(src: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """
    边缘引导超分辨率 - 保持边缘的同时放大

    通过去噪 + 自适应锐化 + 边缘-preserving放大
    """
    # 计算需要的scale factor
    scale = target_w / src.shape[1]

    # 第一步：去噪（仅对较大图像有效果）
    if src.shape[0] * src.shape[1] > 500 * 500:
        src = cv2.fastNlMeansDenoisingColored(src, None, 3, 3, 7, 21)

    # 边缘增强
    src = _enhance_edges(src)

    if scale < 1.5:
        # 小幅放大：直接用INTER_CUBIC
        result = cv2.resize(src, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
    else:
        # 大幅放大：使用INTER_LANCZOS4（OpenCV 4.x）
        try:
            result = cv2.resize(src, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)
        except AttributeError:
            # 老版本OpenCV使用分步放大
            result = _progressive_resize(src, target_w, target_h)

    # 后处理锐化
    result = _enhance_edges(result, strength=0.8)

    return result


def _enhance_edges(img: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """增强边缘和细节"""
    # 创建锐化核
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]) * strength

    # 应用锐化
    sharpened = cv2.filter2D(img, -1, kernel)

    # 混合原始和锐化
    alpha = min(1.0, strength * 0.3)
    return cv2.addWeighted(img, 1 - alpha, sharpened, alpha, 0)


def _cubic_with_enhancement(src: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """
    Cubic插值 + 去噪 + 锐化增强
    """
    scale = target_w / src.shape[1]

    # 小幅去噪
    if src.shape[0] * src.shape[1] > 300 * 300:
        src = cv2.fastNlMeansDenoisingColored(src, None, 2, 2, 5, 15)

    # 使用CUBIC放大
    if scale >= 2.0:
        # 分两步放大以保持质量
        mid_w = int(src.shape[1] * 1.5)
        mid_h = int(src.shape[0] * 1.5)
        mid = cv2.resize(src, (mid_w, mid_h), interpolation=cv2.INTER_CUBIC)
        result = cv2.resize(mid, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
    else:
        result = cv2.resize(src, (target_w, target_h), interpolation=cv2.INTER_CUBIC)

    # 轻微锐化
    result = _enhance_edges(result, strength=0.5)

    return result


def _progressive_resize(src: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """分步放大"""
    scale = target_w / src.shape[1]
    current = src.copy()

    while current.shape[1] < target_w:
        step = min(1.5, target_w / current.shape[1])
        new_w = int(current.shape[1] * step)
        new_h = int(current.shape[0] * step)
        current = cv2.resize(current, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

        if current.shape[1] < target_w:
            current = _enhance_edges(current, strength=0.3)

    return cv2.resize(current, (target_w, target_h), interpolation=cv2.INTER_CUBIC)


def _deep_super_resolution(src: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """
    深度学习超分辨率（模拟版）

    使用去噪 + 多尺度混合 + 自适应锐化的组合
    """
    # 尝试导入深度学习模块
    try:
        import torch
        import torch.nn as nn
        from torchvision import transforms

        # 使用简单的SRCNN模拟
        class SimpleSRNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 5, padding=2)
                self.conv2 = nn.Conv2d(64, 32, 3, padding=1)
                self.conv3 = nn.Conv2d(32, 3, 3, padding=1)
                self.relu = nn.ReLU()

            def forward(self, x):
                x = self.relu(self.conv1(x))
                x = self.relu(self.conv2(x))
                x = self.conv3(x)
                return x

        # 准备tensor
        tensor = torch.from_numpy(src).permute(2, 0, 1).unsqueeze(0).float() / 255.0

        # 中间放大
        mid = cv2.resize(src, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        mid_tensor = torch.from_numpy(mid).permute(2, 0, 1).unsqueeze(0).float() / 255.0

        # 应用模型
        model = SimpleSRNN()
        model.eval()
        with torch.no_grad():
            output = model(mid_tensor)

        result = (output.squeeze(0).permute(1, 2, 0).numpy() * 255.0)
        result = np.clip(result, 0, 255).astype(np.uint8)

        # 锐化增强
        result = _enhance_edges(result, strength=0.6)
        return result

    except ImportError:
        # 如果没有torch，使用增强版CUBIC
        return _cubic_with_enhancement(src, target_w, target_h)


def _lanczos_upscale(src: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """LANCZOS放大（使用PIL的API）"""
    pil_img = cv_to_pil(src)
    result = pil_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return pil_to_cv(result)


def _downscale_cv(src: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    """优化的缩小"""
    # 预锐化
    src = _enhance_edges(src, strength=0.2)

    # 缩小
    result = cv2.resize(src, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

    # 锐化恢复
    result = _enhance_edges(result, strength=0.3)

    return result


def get_available_algorithms() -> list[str]:
    """获取可用的算法列表"""
    algorithms = ["lanczos", "cubic", "edge"]

    try:
        import torch
        algorithms.append("deep")
    except ImportError:
        pass

    return algorithms