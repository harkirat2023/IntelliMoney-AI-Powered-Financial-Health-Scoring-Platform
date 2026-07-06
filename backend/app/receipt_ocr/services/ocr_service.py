import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    import io
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract/PIL not available — OCR disabled")


class OCRService:
    def __init__(self):
        self._config = r"--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,/-:₹ " if TESSERACT_AVAILABLE else ""

    def extract(self, image_bytes: bytes) -> dict:
        if not TESSERACT_AVAILABLE:
            return {"raw_text": "", "merchant_name": "", "total_amount": 0.0,
                    "transaction_date": "", "transaction_time": "",
                    "currency": "INR", "tax_amount": 0.0, "items": []}

        try:
            img = Image.open(io.BytesIO(image_bytes))
            raw_text = pytesseract.image_to_string(img, config=self._config)
            lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

            merchant = self._extract_merchant(lines)
            total_amount = self._extract_amount(lines)
            tx_date = self._extract_date(lines)
            tx_time = self._extract_time(lines)
            currency = self._detect_currency(raw_text)

            return {
                "raw_text": raw_text,
                "merchant_name": merchant,
                "total_amount": total_amount,
                "transaction_date": tx_date,
                "transaction_time": tx_time,
                "currency": currency,
                "tax_amount": 0.0,
                "items": [],
            }
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {"raw_text": "", "merchant_name": "", "total_amount": 0.0,
                    "transaction_date": "", "transaction_time": "",
                    "currency": "INR", "tax_amount": 0.0, "items": [],
                    "error": str(e)}

    def _extract_merchant(self, lines: list[str]) -> str:
        noise_keywords = {"total", "amount", "tax", "gst", "cash", "change",
                         "receipt", "bill", "invoice", "date", "time",
                         "thanks", "thank", "visit", "store", "online"}
        for line in lines[:8]:
            clean = line.strip().title()
            words = clean.split()
            if len(words) >= 2 and not any(k in line.lower() for k in noise_keywords):
                return clean[:100]
        for line in lines:
            if any(kw in line.lower() for kw in ["store", "restaurant", "cafe",
                                                   "hotel", "shop", "mart",
                                                   "pharmacy", "clinic", "salon"]):
                return line.strip().title()[:100]
        return lines[0][:100] if lines else ""

    def _extract_amount(self, lines: list[str]) -> float:
        patterns = [
            r"(?:total|amount|grand\s*total|due|pay|net)[:\s]*[₹$€£]?\s*([0-9]+[,.]?[0-9]*)",
            r"[₹$€£]\s*([0-9]+[,.]?[0-9]*)",
            r"(?:^|\s)([0-9]+[,.][0-9]{2})\s*$",
        ]
        amounts = []
        for line in lines:
            clean = line.replace(",", "")
            for pat in patterns:
                matches = re.findall(pat, clean, re.IGNORECASE)
                for m in matches:
                    try:
                        val = float(m.replace(",", ""))
                        if 1 <= val <= 9999999:
                            amounts.append(val)
                    except ValueError:
                        continue
        return max(amounts) if amounts else 0.0

    def _extract_date(self, lines: list[str]) -> str:
        patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(\d{4}[/-]\d{1,2}[/-]\d{1,2})",
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})",
        ]
        for line in lines:
            for pat in patterns:
                m = re.search(pat, line, re.IGNORECASE)
                if m:
                    raw = m.group(1)
                    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d",
                                "%m/%d/%Y", "%m-%d-%Y", "%d %b %Y", "%d %B %Y"):
                        try:
                            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
                        except ValueError:
                            continue
        return ""

    def _extract_time(self, lines: list[str]) -> str:
        pat = r"(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?)"
        for line in lines:
            m = re.search(pat, line)
            if m:
                return m.group(1)
        return ""

    def _detect_currency(self, text: str) -> str:
        if "₹" in text or "INR" in text:
            return "INR"
        if "$" in text or "USD" in text:
            return "USD"
        if "€" in text or "EUR" in text:
            return "EUR"
        if "£" in text or "GBP" in text:
            return "GBP"
        return "INR"
