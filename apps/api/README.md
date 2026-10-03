# CERNO API

Backend FastAPI untuk katalog 20 route di `ARCHITECTURE.md`. Penilaian tahap ini memakai **baseline aturan**, bukan model AI terlatih. Pemeriksaan reputasi URL belum terhubung ke provider; hasil selalu menyebut status `not_checked`. URL pengguna tidak dikunjungi oleh server.

## Menjalankan di Windows

Prasyarat: Python 3.13, PostgreSQL, Node.js untuk Azurite, dan Tesseract OCR dengan data bahasa `ind` serta `eng`. [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-install-azurite?tabs=npm) mengemulasikan Azure Blob dan Queue secara lokal. [Data bahasa Tesseract](https://github.com/tesseract-ocr/tessdata_fast) menyediakan `ind.traineddata` dan `eng.traineddata`.

```powershell
cd E:\cerno\apps\api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[test]'
Copy-Item .env.example .env
npm install --global azurite
azurite --location "$env:TEMP\cerno-azurite" --silent
```

Pada terminal lain, instal Tesseract dan data bahasanya jika belum tersedia:

```powershell
winget install --id UB-Mannheim.TesseractOCR -e
New-Item -ItemType Directory -Force .venv\tessdata | Out-Null
Invoke-WebRequest 'https://github.com/tesseract-ocr/tessdata_fast/raw/refs/heads/main/ind.traineddata' -OutFile .venv\tessdata\ind.traineddata
Invoke-WebRequest 'https://github.com/tesseract-ocr/tessdata_fast/raw/refs/heads/main/eng.traineddata' -OutFile .venv\tessdata\eng.traineddata
$env:TESSDATA_PREFIX = (Resolve-Path .venv\tessdata).Path
```

Buat database PostgreSQL bernama `cerno`, lalu ubah `DATABASE_URL` di `.env` sesuai akun lokal. Jangan commit `.env`. Jalankan migrasi dan ketiga proses ini pada terminal terpisah:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
.\.venv\Scripts\python.exe -m app.ocr.worker
.\.venv\Scripts\python.exe -m app.maintenance
```

Perintah maintenance menjalankan pembersihan satu kali; jadwalkan berulang untuk menegakkan penghapusan fisik. API menolak akses data kedaluwarsa segera, meski pekerjaan pembersihan belum berjalan. Untuk membuat Admin secara administratif:

```powershell
.\.venv\Scripts\python.exe -m app.admin_cli admin@example.com
```

Jika Tesseract tidak berada di `PATH`, isi `TESSERACT_CMD` dengan path lengkap ke `tesseract.exe`. Atur `TESSDATA_PREFIX` pada terminal worker, seperti contoh di atas. Instalasi lokal yang diuji memakai `C:\Program Files\Tesseract-OCR\tesseract.exe` dan data bahasa di `.venv\tessdata`. `GET http://localhost:8000/docs` menampilkan skema OpenAPI.

## Alur API

Semua route berikut memakai prefiks `/api/v1`. Respons kesalahan memakai `application/problem+json`. Token hasil dan OCR dikembalikan **sekali** pada respons pembuatan; klien menyimpannya sementara dan mengirim melalui header `X-Access-Token`, bukan URL. Frontend dapat menaruh token hasil pada fragmen URL untuk tautan yang bisa dibuka ulang. Semua respons API memakai `Cache-Control: no-store`.

| Alur | Permintaan penting |
|---|---|
| Analisis | `POST /analyses` dengan `{"input_type":"text","text":"..."}` atau `{"input_type":"url","url":"https://example.org"}`; `GET /analyses/{id}` memakai `X-Access-Token`. |
| Screenshot | `POST /ocr-jobs` multipart field `screenshot` (PNG/JPEG, maks. 5 MB), kemudian `GET /ocr-jobs/{id}` dengan `X-Access-Token`. Setelah pengguna meninjau teks, `POST /analyses` dengan `input_type:"screenshot"`, `text`, `ocr_job_id`, dan `ocr_access_token`. Satu job hanya dapat menghasilkan satu analisis. |
| Akun | `POST /auth/register` dan `/auth/login` menerima `email` dan `password`; login memberi cookie sesi HttpOnly dan `csrf_token`. `GET /auth/me` membaca sesi; `POST /auth/logout` membutuhkan `X-CSRF-Token`. |
| Riwayat | `POST /history` menerima `analysis_id` dan `access_token`, serta cookie sesi dan `X-CSRF-Token`. `GET /history`, `GET /history/{id}`, dan `DELETE /history/{id}` hanya untuk pemilik; DELETE juga membutuhkan CSRF. |
| Feedback | `POST /analyses/{id}/feedback` menerima `helpful`, `verdict` (`correct`, `too_high`, `too_low`, `unsure`), dan `comment` opsional. Gunakan token hasil; jika ada sesi login, sertakan CSRF. |
| Laporan | `POST /reports` menerima `target_type` (`url`/`text`), `target`, `reason`, dan `consent:true`. Simpan `reporter_token` respons untuk deduplikasi melalui `X-Reporter-Token`; laporan belum menjadi sinyal sebelum diterima Admin. |
| Admin | `GET /admin/summary`, `/admin/reports`, `/admin/reports/{id}`, `/admin/feedback`, `/admin/models`; `POST /admin/reports/{id}/decisions` menerima `decision` (`accepted`, `rejected`, `duplicate`) dan `reason`, dengan cookie Admin dan CSRF. |

Contoh cepat memakai PowerShell setelah API hidup:

```powershell
$api = 'http://localhost:8000/api/v1'
$hasil = Invoke-RestMethod "$api/analyses" -Method Post -ContentType 'application/json' -Body '{"input_type":"text","text":"Segera kirim OTP Anda"}'
Invoke-RestMethod "$api/analyses/$($hasil.id)" -Headers @{ 'X-Access-Token' = $hasil.access_token }
```

## Batas tahap ini

- Registrasi langsung aktif hanya pada `ENVIRONMENT=development`. Pada `production`, registrasi ditolak sampai verifikasi email tersedia.
- Baseline aturan menghasilkan indikator yang dapat dijelaskan, tetapi belum memiliki metrik evaluasi model. `GET /admin/models` menyatakan `not_evaluated`.
- Adapter reputasi URL mengembalikan `not_checked`; kegagalan provider mendatang harus menghasilkan `incomplete`, bukan klaim aman.
- Pembatasan permintaan saat ini berada di memori proses untuk uji lokal. Deployment multi-replica memerlukan limiter bersama.
- Azure deployment, provider OCR Azure, layanan email, MFA Admin, dan integrasi frontend belum termasuk tahap ini.

## Pengujian

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Untuk uji integrasi PostgreSQL, siapkan database disposable dengan nama berakhiran `_test`, jalankan migrasi terhadapnya, lalu set `DATABASE_URL` dan `CERNO_TEST_DATABASE_URL` ke URL database itu sebelum `pytest`. Uji OCR memakai mock untuk kegagalan deterministik, dan satu uji manual dengan Tesseract, Azurite, PostgreSQL, serta screenshot berbahasa Indonesia memeriksa jalur nyata.
