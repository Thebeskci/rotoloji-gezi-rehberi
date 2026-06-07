# Rotoloji Final Proje Raporu Taslagi

## Kapak
- Proje adi: Rotoloji
- Ogrenci adi soyadi: ...
- Numara: ...
- Ders: BIP210 Icerik Yonetimi
- Teslim tarihi: ...

## Proje Ozeti
Rotoloji, dunyanin farkli sehirleri icin gezi icerigi toplayan, bu icerigi YZ ile zenginlestiren, cok dilli olarak Strapi icinde saklayan ve Streamlit arayuzu ile son kullaniciya gosteren uc katmanli bir sistemdir.

Kullanilan ana teknolojiler:
- Strapi 5
- Python 3.12
- Streamlit
- deep-translator
- Pollinations
- Wikivoyage
- Wikimedia REST API

## Sistem Mimarisi
- Seed veri kumesi sehirleri ve mekanlari tanimlar.
- Python ingest betigi secilen gezi kaynagi olarak Wikivoyage sehir rehberlerini okur.
- Mekan aciklamalari gerekiyorsa Wikimedia ozetleri ile desteklenir.
- Pollinations text endpoint'i ile Turkce aciklamalar genisletilir.
- Nihai TR icerik `deep-translator` ile EN locale'ine cevrilir.
- Pollinations image endpoint'i ile mekan prompt'una uygun gorsel uretilmeye calisilir.
- Uretilen ya da fallback olarak indirilen gorsel Strapi Media Library'ye yuklenir.
- `City` ve `Place` belgeleri JWT ile Strapi REST API uzerinden `tr` ve `en` locale'lerinde upsert edilir.
- Streamlit, Strapi API'den veriyi cekip sehir filtresi ve dil secimi ile gosteri yapar.

Mimari diyagram:
- [docs/architecture.mmd](/Users/thebesikci/Documents/Strapi/docs/architecture.mmd)

## Erisim Bilgileri
- Strapi admin linki: ...
- Strapi admin kullanici adi: ...
- Strapi admin sifresi: ...
- Streamlit linki: ...

## Teknik Detaylar

### Strapi Veri Modeli
- `City`
  - `name`
  - `slug`
  - `country`
  - `short_description`
  - `hero_image`
  - `places` relation
- `Place`
  - `name`
  - `slug`
  - `description`
  - `rating`
  - `category`
  - `source_url`
  - `generated_prompt`
  - `cover_image`
  - `city` relation

### Iliskiler
- Bir sehirin birden fazla mekani olabilir.
- Her mekan tek bir sehire baglidir.

### Cok Dilli Yapi
- Varsayilan locale `tr`
- Ikinci locale `en`

### Python Modulleri
- `seed.py`: seed veri setini yukler ve dogrular.
- `travel_guides.py`: Wikivoyage sehir sayfalarindan giris metni ve mekan parcaciklari ceker.
- `wikimedia.py`: ozet ve fallback gorsel bilgilerini toplar.
- `text_enrichment.py`: Pollinations text ucu ile TR aciklamayi zenginlestirir.
- `translator.py`: TR <-> EN ceviri katmani.
- `images.py`: Pollinations image denemesi ve fallback indirme katmani.
- `strapi_client.py`: JWT auth, upload ve collection CRUD katmani.
- `ingest.py`: tum otomasyon zincirini tek komutta birlestirir.

## Kod Aciklamasi

### Tek Komut Akisi
`python -m rota_yz.ingest`

Bu komut:
1. Seed verisini okur.
2. Wikivoyage kaynagindan sehir ve mekan metinlerini bulmaya calisir.
3. Wikimedia ozetlerini destekleyici katman olarak kullanir.
4. Pollinations text ile aciklamalari genisletir.
5. EN locale cevirisini uretir.
6. Pollinations image ile gorsel olusturmayi dener.
7. Gorseli Strapi Media Library'ye yukler.
8. `City` ve `Place` verisini `tr` ve `en` olarak Strapi'ye yazar.

### JWT Kimlik Dogrulama
`StrapiClient.authenticate()` fonksiyonu `/api/auth/local` istegi ile JWT alir. Sonraki tum korumali API cagrilarinda bu token `Authorization: Bearer ...` basligi ile gonderilir.

### Media Library Yukleme
`StrapiClient.upload_image()` fonksiyonu `/api/upload` endpoint'ine multipart `files` payload'i yollar. Donen media `id` degeri `cover_image` ya da `hero_image` iliskisinde kullanilir.

### Streamlit Gosterimi
Streamlit arayuzu sehir secimi, kategori secimi ve minimum puan filtresi ile Strapi API'den gelen `City` ve `Place` verisini listeler. TR/EN locale secimi yapilabilir.

## Oncesi / Sonrasi Kanitlari
Bu bolume su ekran goruntuleri eklenmelidir:
- Strapi `Places` listesi bosken ekran goruntusu
- Ingest sonrasi `Places` listesinin dolu hali
- Media Library icinde yuklenmis gorseller
- `Settings > Internationalization` ekraninda `tr` ve `en`
- Streamlit ana ekrani
- Streamlit `EN` locale goruntusu
- Sehir filtresi uygulanmis gorunum

## Sonuc
Bu proje, BIP210 final beklentilerindeki Strapi backend, Python otomasyon motoru ve Streamlit frontend iskeletini tek repoda toplar. Teknik olarak en kritik gereksinimler olan iliskisel veri modeli, i18n, JWT ile API yazimi, Media Library upload, ceviri, YZ gorsel ve metin zenginlestirme zinciri repo icinde karsilanmistir.

Son teslim oncesi manuel olarak tamamlanmasi gerekenler:
- Canli Strapi ve Streamlit URL'lerini rapora yazmak
- Degerlendirici kullanicisini tanimlamak
- Ekran goruntulerini alip PDF'e eklemek
- Markdown raporunu PDF formatina donusturmek
