"""
Ochiq kalitni (public_key.pem) brauzer tushunadigan JWK formatga o'giradi.
Kalitlarni yangilasangiz (yangi RSA juftlik yaratsangiz), buni qayta ishga
tushiring va natijadagi JSON'ni verify.html ichidagi PUBLIC_KEY_JWK
o'zgaruvchisiga qo'ying.

Ishlatish: python get_public_jwk.py
"""

import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives import serialization

BASE_DIR = Path(__file__).parent


def b64url(n: int) -> str:
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def main():
    pub = serialization.load_pem_public_key((BASE_DIR / "public_key.pem").read_bytes())
    numbers = pub.public_numbers()

    jwk = {
        "kty": "RSA",
        "n": b64url(numbers.n),
        "e": b64url(numbers.e),
        "alg": "PS256",
        "ext": True,
        "key_ops": ["verify"],
    }

    out_path = BASE_DIR / "public_key_jwk.json"
    out_path.write_text(json.dumps(jwk, indent=2))
    print(f"✅ Saqlandi: {out_path}")
    print(json.dumps(jwk))


if __name__ == "__main__":
    main()
