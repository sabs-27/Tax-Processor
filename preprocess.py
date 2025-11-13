"""
Basic preprocessing utilities for images (grayscale, resize, simple contrast) when Pillow is available.
Functions are optional for the pipeline; if Pillow is not installed, functions raise informative errors.
"""
from typing import Tuple


def normalize_image(path: str, out_path: str, max_width: int = 2000) -> Tuple[str, Tuple[int,int]]:
    """Load image, convert to grayscale, resize if wider than max_width, save to out_path and return (out_path, size).
    Requires Pillow to be installed.
    """
    try:
        from PIL import Image, ImageOps
    except Exception:
        raise RuntimeError('Pillow required for image preprocessing')

    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = img.convert('L')
    w, h = img.size
    if w > max_width:
        new_h = int(h * (max_width / w))
        img = img.resize((max_width, new_h))
    img.save(out_path)
    return out_path, img.size
