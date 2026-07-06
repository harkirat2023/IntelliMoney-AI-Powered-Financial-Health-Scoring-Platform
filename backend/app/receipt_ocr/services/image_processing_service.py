import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available — image preprocessing disabled")


class ImageProcessingService:
    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
    MAX_SIZE_MB = 10

    def preprocess(self, image_path: str) -> bytes | None:
        if not CV2_AVAILABLE:
            return self._fallback_read(image_path)
        try:
            img = cv2.imread(image_path)
            if img is None:
                return self._fallback_read(image_path)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray, h=30)
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            coords = np.column_stack(np.where(thresh > 0))
            if len(coords) > 0:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = 90 + angle
                if abs(angle) > 2:
                    h, w = thresh.shape
                    center = (w // 2, h // 2)
                    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    thresh = cv2.warpAffine(thresh, matrix, (w, h),
                                            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

            _, buf = cv2.imencode(".png", thresh)
            return buf.tobytes()

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return self._fallback_read(image_path)

    def _fallback_read(self, image_path: str) -> bytes | None:
        try:
            with open(image_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Fallback image read failed: {e}")
            return None
