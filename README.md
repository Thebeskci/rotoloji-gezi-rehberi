# Rotoloji Gezi Rehberi

Rotoloji, BIP210 final proje beklentilerine gore sifirdan kurulmus cok dilli bir gezi rehberi uygulamasidir. Proje uc katmandan olusur:

- `backend/`: Strapi 5 uzerinde `City` ve `Place` koleksiyonlari
- `python/rota_yz/`: veri toplama, ceviri, gorsel uretimi ve Strapi ingest akisi
- `frontend/app.py`: Streamlit arayuzu
- `pages/`: GitHub Pages icin statik arayuz kaynagi

## Klasor Yapisi

- `backend/`: Strapi uygulamasi ve i18n/JWT bootstrap ayarlari
- `data/seed_places.json`: 6 sehir ve 30 mekanlik cekirdek veri seti
- `data/live_content.json`: Streamlit ve GitHub Pages tarafinin beslendigi yayin snapshot'i
- `python/rota_yz/`: ingest ve frontend istemci kodu
- `frontend/app.py`: kullanici arayuzu
- `pages/`: GitHub Pages arayuzu
- `docs/`: rapor ve mimari belgeleri

## Gereksinimler

- Node.js 22
- Python 3.12
- npm
- `uv` tavsiye edilir

## Lokal Kurulum

1. Python ortamini hazirla:

```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

2. Backend degiskenlerini ayarla:

```bash
cp backend/.env.example backend/.env
```

3. Ingest ve frontend degiskenlerini ayarla:

```bash
cp .env.example .env
```

4. Strapi'yi baslat:

```bash
cd backend
npm install
npm run develop
```

5. Ayrı terminalde ingest calistir:

```bash
source .venv/bin/activate
python -m rota_yz.ingest
```

6. Streamlit arayuzunu ac:

```bash
source .venv/bin/activate
streamlit run frontend/app.py
```

## Backend Davranisi

- Bootstrap sirasinda `tr` varsayilan locale olarak ayarlanir, `en` locale eklenir.
- `Public` rolune `find` ve `findOne` izinleri verilir.
- `Authenticated` rolune `create`, `update` ve upload izinleri verilir.
- `INGEST_USER_*` degiskenleri varsa ingest kullanicisi otomatik olusturulur.

## Python Ingest Akisi

`python -m rota_yz.ingest` komutu:

1. seed veri setini yukler
2. secilen gezi sitesi kaynagi olarak `Wikivoyage` sehir sayfasini okur
3. her mekan icin sehir rehberi icinden ilgili metin parcacigini bulmaya calisir
4. gerekiyorsa Wikimedia ozetini destekleyici kaynak olarak ceker
5. Pollinations text API ile TR aciklamayi editoryal bir gezi notuna genisletir
6. TR aciklamayi `deep-translator` ile EN'e cevirir
7. Pollinations ile gorsel uretmeyi dener
8. hata halinde Wikimedia veya placeholder gorseline duser
9. gorseli Strapi Media Library'ye yukler
10. `City` ve `Place` belgelerini `tr` ve `en` locale'lerinde upsert eder

Bu akisin hedefi, final rubric'inde istenen su dordunu birlikte saglamaktir:

- gezi sitesi verisini okumak
- YZ ile metin zenginlestirmek
- YZ ile gorsel uretmek
- JWT ile Strapi Media Library ve koleksiyonlara yazmak

## Testler

```bash
source .venv/bin/activate
pytest
```

## GitHub Pages Yayin

Bu repo, dis sunucu gerektirmeden GitHub Pages uzerinde yayinlanabilecek statik bir Rotoloji arayuzu da icerir.

1. Pages paketini uret:

```bash
source .venv/bin/activate
python -m rota_yz.build_pages
```

2. Istersen yerelde onizle:

```bash
python -m http.server 8010 -d dist-pages
```

3. Tarayicida ac:

```text
http://localhost:8010
```

Build sonunda `dist-pages/` altinda sunlar olusur:

- `index.html`, `styles.css`, `app.js`
- `data/tr.json`, `data/en.json`, `data/manifest.json`
- `assets/cities/*`, `assets/places/*`

Gorseller snapshot icindeki base64 ya da uzak URL kaynaklarindan statik dosyaya cevrilir; boylece Pages tarafinda Streamlit veya Strapi calistirmaya gerek kalmaz.

## Render Deploy

- `render.yaml` canli `Strapi + Streamlit + Postgres` topolojisini tarif eder.
- Render uzerinde blueprint import ederek `rotayz-strapi` ve `rotoloji-streamlit` servislerini birlikte olustur.
- Disk mount yolu `backend/public/uploads` icin tanimlidir.
- Ilk kurulumda Render Dashboard su degerleri ister:
  - `INGEST_USER_EMAIL`
  - `INGEST_USER_USERNAME`
  - `INGEST_USER_PASSWORD`
  - `PUBLIC_URL`
  - tercihen `POLLINATIONS_API_KEY`
  - tercihen `WIKIMEDIA_USER_AGENT`
- `rotoloji-streamlit` servisi acilisinda backend'in public URL'ini `STRAPI_URL` olarak otomatik alir ve `initialDeployHook` ile ilk ingest'i dener.
- Ilk ingest bir nedenle atlanirsa daha sonra lokal ortamdan `STRAPI_URL` degerini Render URL'i ile degistirip `python -m rota_yz.ingest` komutunu tekrar calistirabilirsin.

## Streamlit Cloud Deploy

- Repo'yu GitHub'a gonder.
- Streamlit Community Cloud uzerinde `frontend/app.py` dosyasini giris noktasi olarak sec.
- Python version olarak `3.12` sec.
- Secret veya environment olarak sunlardan birini kullan:
  - `STREAMLIT_DATA_MODE=auto` ve `STRAPI_URL=https://your-strapi-service.onrender.com`
  - veya Strapi olmadan calismasi icin `STREAMLIT_DATA_MODE=snapshot`

## Final Teslim Yolu

BIP210 final teslimi acisindan birincil yayin yolu su ikilidir:

- `Strapi`: Render uzerindeki `rotayz-strapi` servisi
- `Streamlit`: Render uzerindeki `rotoloji-streamlit` servisi veya Streamlit Community Cloud

GitHub Pages bu repoda yalnizca ek bir statik gosterim secenegidir; final teslimde istenen `Strapi + Streamlit` ciftinin yerini tutmaz.

## GitHub Actions

- `/.github/workflows/ci.yml`
  - Python 3.12 kurar
  - paketi yukler
  - testleri calistirir
  - `data/live_content.json` snapshot'ini dogrular
  - GitHub Pages paketini uretir ve `dist-pages/` smoke testi yapar
  - Streamlit uygulamasini ayaga kaldirip `localhost:8501` smoke testi yapar
- `/.github/workflows/deploy-pages.yml`
  - `main` veya `master` branch push'unda statik `dist-pages/` artifact'ini olusturur
  - resmi `actions/configure-pages`, `actions/upload-pages-artifact` ve `actions/deploy-pages` adimlari ile GitHub Pages yayinini yapar
- `/.github/workflows/deploy-render.yml`
  - yalnizca manuel calisir ve isterse Render deploy hook tetikler
  - su secret'lar eklenirse otomatik deploy calisir:
    - `RENDER_FRONTEND_DEPLOY_HOOK_URL`
    - `RENDER_BACKEND_DEPLOY_HOOK_URL`

## Ek Yayin

- Repo public oldugu surece statik tanitim sitesi su adreste yayinlanir:
  - `https://thebeskci.github.io/rotoloji-gezi-rehberi/`
- Bu katman final teslimin zorunlu parcasi degildir; destekleyici demonstrasyon katmanidir.

## Strapi'siz Streamlit Modu

- Repo icine gommeli snapshot dosyasi `data/live_content.json` icinden veri okunabilir.
- Snapshot'i guncellemek icin:

```bash
source .venv/bin/activate
python -m rota_yz.live_snapshot
```

- Ardindan uygulamayi sadece Streamlit ile kaldir:

```bash
./run_streamlit_live.sh
```

- Betik `snapshot` modunu zorlar ve sirayla `.live-venv`, `.venv`, `.frontend-venv` ortamlarindan uygun olani kullanir.

## Notlar

- Pollinations text ve image katmanlari zaman zaman anahtar veya rate-limit davranisi gosterebilir. Final sunumu icin hem metin zenginlestirme hem de gorsel uretimini istikrarli hale getirmek istiyorsan `POLLINATIONS_API_KEY` eklemen gerekir.
- Gercek deploy linkleri ve giris bilgileri rapor icin manuel olarak doldurulmalidir.
- Son teslim kontrolu icin [docs/compliance-matrix.md](/Users/thebesikci/Documents/Strapi/docs/compliance-matrix.md) dosyasini kullan.
