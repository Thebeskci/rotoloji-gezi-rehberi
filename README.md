# RotaYZ Gezi Rehberi

RotaYZ, BIP210 final proje beklentilerine gore sifirdan kurulmus cok dilli bir gezi rehberi uygulamasidir. Proje uc katmandan olusur:

- `backend/`: Strapi 5 uzerinde `City` ve `Place` koleksiyonlari
- `python/rota_yz/`: veri toplama, ceviri, gorsel uretimi ve Strapi ingest akisi
- `frontend/app.py`: Streamlit arayuzu

## Klasor Yapisi

- `backend/`: Strapi uygulamasi ve i18n/JWT bootstrap ayarlari
- `data/seed_places.json`: 6 sehir ve 30 mekanlik cekirdek veri seti
- `python/rota_yz/`: ingest ve frontend istemci kodu
- `frontend/app.py`: kullanici arayuzu
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
2. gerekiyorsa Wikimedia ozetini ceker
3. TR aciklamayi `deep-translator` ile EN'e cevirir
4. Pollinations ile gorsel uretmeyi dener
5. hata halinde Wikimedia veya placeholder gorseline duser
6. gorseli Strapi Media Library'ye yukler
7. `City` ve `Place` belgelerini `tr` ve `en` locale'lerinde upsert eder

## Testler

```bash
source .venv/bin/activate
pytest
```

## Render Deploy

- `render.yaml` backend web service ve Postgres kaynagini tarif eder.
- Render uzerinde blueprint import ederek `rotayz-strapi` servisini olustur.
- Disk mount yolu `backend/public/uploads` icin tanimlidir.
- Deploy sonrasi `INGEST_USER_EMAIL`, `INGEST_USER_USERNAME`, `INGEST_USER_PASSWORD` degiskenlerini gir.
- Canli veriyi basmak icin lokal ortamdan `STRAPI_URL` degerini Render URL'i ile degistirip ingest komutunu tekrar calistir.

## Streamlit Cloud Deploy

- Repo'yu GitHub'a gonder.
- Streamlit Community Cloud uzerinde `frontend/app.py` dosyasini giris noktasi olarak sec.
- Python version olarak `3.12` sec.
- Secret veya environment olarak sunlardan birini kullan:
  - `STREAMLIT_DATA_MODE=auto` ve `STRAPI_URL=https://your-strapi-service.onrender.com`
  - veya Strapi olmadan calismasi icin `STREAMLIT_DATA_MODE=snapshot`

## GitHub Actions

- `/.github/workflows/ci.yml`
  - Python 3.12 kurar
  - paketi yukler
  - testleri calistirir
  - `data/live_content.json` snapshot'ini dogrular
  - Streamlit uygulamasini ayaga kaldirip `localhost:8501` smoke testi yapar
- `/.github/workflows/deploy-render.yml`
  - `main` veya `master` branch push'unda testten sonra Render deploy hook tetikler
  - su secret'lar eklenirse otomatik deploy calisir:
    - `RENDER_FRONTEND_DEPLOY_HOOK_URL`
    - `RENDER_BACKEND_DEPLOY_HOOK_URL`

## Normal Yayin

- GitHub Actions tek basina hosting yapmaz; CI/CD saglar.
- Bu repo icin iki temiz yayin yolu vardir:
  - Streamlit Community Cloud: en kolay public frontend yayini
  - Render: `render.yaml` icindeki `rotoloji-streamlit` ve `rotayz-strapi` servisleri ile tam yayin
- Render kullanacaksan blueprint import et, sonra deploy hook URL'lerini GitHub repo secret'larina gir.

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

- Pollinations API anahtari yoksa uygulama yine calisir; ancak final sunumu icin AI gorsel ciktisini gostermek adina anahtar eklenmesi tavsiye edilir.
- Gercek deploy linkleri ve giris bilgileri rapor icin manuel olarak doldurulmalidir.
