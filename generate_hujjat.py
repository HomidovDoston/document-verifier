"""
Hujjat generatori: imzolash + QR + PDF
========================================

Bu skript "shablon" ma'lumotlarini (F.I.SH, sana, lavozim va h.k.) oladi,
ularni raqamli imzolaydi va shu ma'lumot + imzoni QR kodga joylaydi.

QR kod ICHIDA quyidagi URL bo'ladi:
    https://SIZNING-DOMEN/verify.html?d=<siqilgan-va-imzolangan-malumot>

Odam QR kodni skanerlaganda telefon brauzerida verify.html ochiladi va u
JavaScript orqali (internetga ulanmasdan, faqat sahifaning o'zida) imzoni
tekshiradi hamda TO'LIQ SHABLONNI chiroyli ko'rinishda ko'rsatadi —
xuddi my.gov.uz kabi.

MUHIM: --base-url parametriga o'zingizning domeningizni yozing
(masalan https://tkxu.uz/verify.html). Domen bo'lmasa, vaqtinchalik
`file://.../verify.html?d=...` ko'rinishida ham ishlaydi (faqat shu
kompyuterda sinov uchun).

Kerakli kutubxonalar:
    pip install cryptography qrcode[pil] reportlab pillow --break-system-packages
"""

import argparse
import base64
import json
import zlib
import uuid
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import qrcode

BASE_DIR = Path(__file__).parent
PRIVATE_KEY_PATH = BASE_DIR / "private_key.pem"
PUBLIC_KEY_PATH = BASE_DIR / "public_key.pem"

SALT_LENGTH = 32  # brauzerdagi Web Crypto bilan mos kelishi uchun qat'iy belgilangan


def load_private_key():
    return serialization.load_pem_private_key(PRIVATE_KEY_PATH.read_bytes(), password=None)


def canonical_json(data: dict) -> str:
    """Python va JavaScript'da bir xil natija beradigan qat'iy JSON format."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def sign_fields(fields: dict) -> dict:
    """Maydonlarni hash qiladi, imzolaydi va to'liq paketni qaytaradi."""
    private_key = load_private_key()

    canonical = canonical_json(fields)
    doc_hash = hashes.Hash(hashes.SHA256())
    doc_hash.update(canonical.encode("utf-8"))
    doc_hash_hex = doc_hash.finalize().hex()

    signature = private_key.sign(
        doc_hash_hex.encode("utf-8"),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=SALT_LENGTH),
        hashes.SHA256(),
    )

    package = {
        "id": str(uuid.uuid4())[:8],
        "fields": fields,
        "hash": doc_hash_hex,
        "sig": base64.b64encode(signature).decode("ascii"),
    }
    return package


def make_verify_url(package: dict, base_url: str) -> str:
    payload = canonical_json(package)
    compressed = zlib.compress(payload.encode("utf-8"), level=9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}d={encoded}"


def make_qr(url: str, out_path: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)


def generate(fields: dict, base_url: str, qr_out: str = "hujjat_qr.png"):
    package = sign_fields(fields)
    url = make_verify_url(package, base_url)
    make_qr(url, qr_out)
    return package, url, qr_out


def main():
    parser = argparse.ArgumentParser(description="Hujjat maydonlarini imzolab, QR yaratish")
    parser.add_argument("--fields-json", required=True, help="Maydonlar JSON fayli yo'li")
    parser.add_argument("--base-url", required=True, help="Tekshiruv sahifasi manzili, masalan https://tkxu.uz/verify.html")
    parser.add_argument("--out", default="hujjat_qr.png", help="Chiqish QR fayli")
    args = parser.parse_args()

    fields = json.loads(Path(args.fields_json).read_text(encoding="utf-8"))
    package, url, qr_path = generate(fields, args.base_url, args.out)

    print(f"✅ QR yaratildi: {qr_path}")
    print(f"   Hujjat ID: {package['id']}")
    print(f"   URL uzunligi: {len(url)} belgi")
    print(f"   To'liq URL:\n{url}")


if __name__ == "__main__":
    main()
