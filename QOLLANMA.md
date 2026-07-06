# Hujjatni QR orqali tasdiqlash tizimi — qo'llanma

my.gov.uz uslubida: hujjat ma'lumotlari raqamli imzolanadi, QR kodga
joylanadi. QR kod skanerlanganda brauzerda `verify.html` ochiladi va u
hech qanday serversiz, faqat o'zining ichida (JavaScript + Web Crypto)
imzoni tekshirib, to'liq shablonni ko'rsatadi.

## Fayllar

- `generate_hujjat.py` — maydonlarni imzolab, QR kod yaratadi
- `verify.html` — QR skanerlanganda ochiladigan tekshiruv sahifasi
- `private_key.pem` — MAXFIY kalit (faqat siz uchun, hech kimga bermang!)
- `public_key.pem` / `public_key_jwk.json` — ochiq kalit (verify.html ichida allaqachon joylashtirilgan)
- `get_public_jwk.py` — kalitlarni yangilaganda JWK qayta hosil qilish uchun
- `namuna_fields.json` — misol uchun maydonlar fayli

## 1-qadam: verify.html'ni joylashtirish (hosting)

`verify.html` faylini o'z veb-saytingizga (masalan `https://tkxu.uz/verify.html`)
yuklang. Bu — statik fayl, hech qanday backend/server-side kod kerak emas,
oddiy hosting yetarli.

## 2-qadam: har bir hujjat uchun QR yaratish

Har bir yangi hujjat/ma'lumotnoma tayyorlanganda, uning maydonlarini JSON
faylga yozing (`namuna_fields.json` kabi) va ishga tushiring:

```bash
python generate_hujjat.py \
    --fields-json namuna_fields.json \
    --base-url "https://tkxu.uz/verify.html" \
    --out hujjat_qr.png
```

Bu `hujjat_qr.png` faylini yaratadi — shu rasmni PDF shabloningizning
pastki qismiga (aynan yuborgan namunangizdagi kabi) joylashtirasiz.

## 3-qadam: maydonlarni moslashtirish

Agar boshqa turdagi hujjatlar uchun boshqa maydonlar kerak bo'lsa:
1. `namuna_fields.json`dagi kalit nomlarini o'zgartiring/qo'shing
2. `verify.html` ichidagi `FIELD_LABELS` obyektiga mos yorliqlarni qo'shing
   (masalan `"mansab": "Mansabi"`), aks holda maydon nomi xom holida chiqadi

## Ishlash printsipi (qisqacha)

1. Maydonlar (F.I.SH, sana va h.k.) qat'iy formatda JSON qilinadi
2. Shu JSON'ning SHA-256 hash'i olinadi
3. Hash MAXFIY kalit bilan (RSA-PSS) imzolanadi
4. {maydonlar, hash, imzo} — siqiladi (zlib) va Base64 qilib URL'ga qo'shiladi
5. URL QR kodga aylantiriladi va PDF'ga joylanadi
6. Odam QR'ni skanerlaydi → brauzer verify.html'ni ochadi
7. Sahifa: (a) maydonlardan hash'ni qayta hisoblaydi — mos kelmasa "buzilgan" deydi
           (b) OCHIQ kalit bilan imzoni tekshiradi — soxta bo'lsa aniqlanadi
           (c) ikkalasi ham to'g'ri bo'lsa — to'liq shablonni chiroyli holda ko'rsatadi

## MUHIM xavfsizlik eslatmalari

- `private_key.pem` faylini hech qachon veb-saytga yoki ommaviy joyga qo'ymang —
  faqat hujjat generatsiya qiladigan serveringizda/kompyuteringizda saqlang.
- `public_key.pem`/`public_key_jwk.json` ni ommaga ochiq qilish xavfsiz — u
  faqat tekshirish uchun ishlatiladi, imzolash uchun emas.
- Agar `private_key.pem` biror kimga oshkor bo'lib qolsa, DARHOL yangi kalit
  juftligi yarating (avvalgi RSA kalit yaratish kodidan foydalanib) va
  `get_public_jwk.py`ni qayta ishga tushirib, `verify.html`dagi kalitni
  yangilang — aks holda soxta hujjatlar "haqiqiy" deb chiqishi mumkin.
