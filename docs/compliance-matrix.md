# BIP210 Uyum Matrisi

Bu dosya, [BIP210_final_projesi.pdf](/Users/thebesikci/Downloads/BIP210_final_projesi.pdf) icindeki maddeleri repo ile eslestirir.

## 1. Veri Mimarisi ve Backend

- `City` ve `Place` koleksiyonlari mevcut:
  - [backend/src/api/city/content-types/city/schema.json](/Users/thebesikci/Documents/Strapi/backend/src/api/city/content-types/city/schema.json)
  - [backend/src/api/place/content-types/place/schema.json](/Users/thebesikci/Documents/Strapi/backend/src/api/place/content-types/place/schema.json)
- Iliski dogru kurulmus:
  - `City.places` one-to-many
  - `Place.city` many-to-one
- i18n acik ve varsayilan locale `tr`, ek locale `en`:
  - [backend/src/index.js](/Users/thebesikci/Documents/Strapi/backend/src/index.js)

## 2. Otomasyon Motoru

- Tek komut ingest:
  - `python -m rota_yz.ingest`
  - [python/rota_yz/ingest.py](/Users/thebesikci/Documents/Strapi/python/rota_yz/ingest.py)
- Gezi sitesi verisi:
  - `Wikivoyage` sehir sayfalari okunur
  - [python/rota_yz/travel_guides.py](/Users/thebesikci/Documents/Strapi/python/rota_yz/travel_guides.py)
  - [data/seed_places.json](/Users/thebesikci/Documents/Strapi/data/seed_places.json)
- Metin zenginlestirme:
  - Pollinations text endpoint
  - [python/rota_yz/text_enrichment.py](/Users/thebesikci/Documents/Strapi/python/rota_yz/text_enrichment.py)
- Ceviri:
  - [python/rota_yz/translator.py](/Users/thebesikci/Documents/Strapi/python/rota_yz/translator.py)
- Gorsel uretimi:
  - [python/rota_yz/images.py](/Users/thebesikci/Documents/Strapi/python/rota_yz/images.py)
- JWT ile Strapi yazimi ve upload:
  - [python/rota_yz/strapi_client.py](/Users/thebesikci/Documents/Strapi/python/rota_yz/strapi_client.py)

## 3. Frontend

- Streamlit arayuzu:
  - [frontend/app.py](/Users/thebesikci/Documents/Strapi/frontend/app.py)
- Sehir secimi ve filtreleme mevcut.
- API veya snapshot modunda veri okuyabilir.

## 4. Rapor ve Kanitlar

- Mimari diyagram:
  - [docs/architecture.mmd](/Users/thebesikci/Documents/Strapi/docs/architecture.mmd)
- Rapor taslagi:
  - [docs/report-template.md](/Users/thebesikci/Documents/Strapi/docs/report-template.md)
- Ekran goruntusu kontrol listesi:
  - [docs/screenshot-checklist.md](/Users/thebesikci/Documents/Strapi/docs/screenshot-checklist.md)

## 5. Manuel Kapanis Adimlari

Su maddeler kodla hazirlandi ama son teslim icin manuel olarak tamamlanmalidir:

- Gecerli `POLLINATIONS_API_KEY` girerek AI text ve image adimlarini canli ortamda garanti altina almak
- Render uzerinde blueprint'i import edip canli `Strapi` linkini acmak
- Render uzerinde `rotoloji-streamlit` linkini acmak
- Strapi admin kullanicisi ve sifresini rapora yazmak
- Once/sonra ekran goruntulerini alip rapora eklemek
- Markdown raporunu PDF ciktisina donusturmek
