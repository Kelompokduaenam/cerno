# Tahap 1 — Kajian sumber dan rancangan pengerjaan Worksheet Week 2 CERNO

## 1. Fungsi masing-masing sumber

| Sumber | Fungsi dalam pengerjaan |
|---|---|
| Modul 1_26.pdf | Jawaban kelompok: masalah, anggota, pembagian peran, solusi, dan 10 fitur Cerno. |
| cerno-in-depth-analysis.md, versi 2.0 | Perincian scope, alur, arsitektur, data, keamanan, evaluasi, dan roadmap produk. |
| Modul 1 - Pembentukan Kelompok & Perumusan Masalah.pdf | Konteks penugasan: solusi nyata, feasible satu semester, mengimplementasikan AI, jaringan, dan cloud; deployment akhir di Azure departemen. |
| Modul 2 - SDLC & Git - rev3.pdf | Acuan kebutuhan tugas SDLC, GitHub Pages, Project, dan Actions, terutama halaman 10–13. |
| Copy of Week 2 - Worksheet (Kelompok PR).docx | Struktur dokumen yang akan diisi. |
| W2_24.pdf | Referensi penyajian jawaban EcoPoint, bukan sumber fitur Cerno atau bukti kegiatan kelompok Cerno. |

Instruksi praktikum dalam dokumen diperlakukan sebagai konteks tugas. Perintah membuat repository, mengundang anggota, mengirim formulir, atau melakukan deployment tidak otomatis dijalankan dalam tahap kajian ini. Permintaan pengguna menjadi acuan urutan pekerjaan: dikerjakan bertahap, dengan diagram dalam format draw.io.

## 2. Konsep produk yang menjadi dasar jawaban

CERNO, dengan tagline “Bedakan sebelum percaya”, adalah aplikasi web pendukung keputusan untuk menilai risiko pesan, URL, dan screenshot percakapan berbahasa Indonesia sebelum pengguna mengeklik tautan, membagikan informasi sensitif, atau bertransaksi. Hasilnya berupa tingkat risiko, skor, indikator yang menjelaskan hasil, serta rekomendasi tindakan.

Sepuluh fitur yang dipertahankan:

1. Text Scam Analyzer.
2. Automatic URL Extraction.
3. URL Risk Analyzer.
4. Explainable Risk Score.
5. Recommended Actions.
6. Analysis History.
7. User Feedback.
8. Admin Dashboard.
9. Screenshot OCR.
10. Anonymous Community Report / Crowdsourcing.

Prinsip desain lintas artefak:

- Hasil berupa Risiko Rendah, Mencurigakan, atau Risiko Tinggi; tidak menyatakan kepastian aman atau penipuan.
- Tidak ada klasifikasi jenis scam, public accusation feed, integrasi WhatsApp langsung, atau live website crawling.
- Pengguna dapat meninjau dan mengoreksi teks OCR sebelum analisis final.
- Analisis dasar dan laporan anonim tidak memerlukan akun; akun diperlukan untuk riwayat pribadi.
- Pesan dan screenshot mentah tidak disimpan secara default sebagai riwayat. Upload OCR menggunakan penyimpanan sementara yang dibatasi retensinya.
- Laporan anonim harus melalui redaksi, deduplikasi, pembatasan pengiriman, dan moderasi. Jumlah laporan bukan bukti tunggal untuk menetapkan risiko tinggi.
- Kegagalan layanan reputasi harus tampak sebagai pemeriksaan tidak lengkap, bukan hasil reputasi aman.
- Feedback tidak otomatis menjadi label pelatihan model.

Kontribusi teknologi mengikuti konsep sumber: AI untuk penilaian risiko dan OCR; jaringan untuk REST API, TLS, komunikasi provider dan antrean OCR; cloud Azure untuk aplikasi, worker, database, penyimpanan sementara, dan monitoring. Detail pilihan layanan masih merupakan rancangan, bukan implementasi yang sudah terbukti berjalan.

## 3. Identitas dan pembagian kerja

| Anggota | NIM | Peran pada jawaban Modul 1 |
|---|---|---|
| Galang Swastika Ramadhan | 24/538251/TK/59692 | Project Manager, Software Engineer |
| Nabila Putri Barokah | 24/541890/TK/60132 | UIUX Designer, Software Engineer |
| Farand Hafiz | 24/540618/TK/60027 | AI Engineer, Cloud Engineer |

Breakdown akan menggunakan tiga anggota ini, bukan contoh tim 4–5 orang pada analisis. Nama kelompok belum jelas: kolomnya pada Modul 1_26.pdf berisi ulang judul “Lab 1.2: PERUMUSAN PERMASALAHAN”. Nama produk CERNO tidak otomatis dianggap nama kelompok.

## 4. Pemetaan isi worksheet

| Bagian | Isi yang akan disusun | Bukti/keluaran |
|---|---|---|
| Lab 2.3 | Identitas dan dokumentasi GitHub Pages kelompok | Konfigurasi dan screenshot halaman yang benar-benar tersedia |
| Lab 2.4 — Metodologi | Usulan Agile dengan Scrumban: iterasi singkat, backlog visual, review berkala | Penjelasan yang terkait risiko data, OCR, integrasi, dan tim tiga orang |
| Tujuan produk | Penilaian sebelum tindakan, penjelasan indikator, rekomendasi, serta integrasi AI/jaringan/cloud | Narasi tujuan spesifik CERNO |
| Pengguna dan kebutuhan | Pengunjung, pengguna berakun, moderator, admin | Tabel kebutuhan dan hak akses |
| Use case | Interaksi pengguna dan layanan eksternal dengan batas sistem CERNO | File .drawio yang dapat diedit dan gambar untuk worksheet |
| Functional requirements | Persyaratan terukur dengan ID FR dan rujukan ke use case | Tabel FR, termasuk hasil/error penting |
| ERD | Entitas, atribut penting, PK/FK, kardinalitas, dan hubungan opsional | File .drawio dan gambar |
| Low-fidelity wireframe | Input, review OCR, hasil, riwayat, pelaporan, serta administrasi | Halaman wireframe .drawio dan gambar |
| Gantt chart | Urutan dan dependensi pekerjaan untuk satu semester | Tabel 12 pertemuan sesuai template, disertai penjelasan pemetaan waktu |
| Lab 2.5 — Breakdown | Subproyek, actionable, deliverable, dan PIC | Daftar yang siap dijadikan issue |
| GitHub Project | Kondisi sesudah assignment dan sesudah satu minggu | Screenshot kegiatan nyata; perkembangan satu minggu tidak dapat direkayasa |
| GitHub Actions | Workflow sesuai repository dan penjelasan trigger/job/hasil | main.yml dan bukti aktual bila sudah tersedia |

Metodologi Scrumban adalah usulan untuk CERNO. Alasannya: hasil baseline AI, kualitas OCR, dan layanan eksternal perlu diuji bertahap; tim kecil memerlukan pembagian tugas yang terlihat serta pembatasan pekerjaan aktif. Review dapat dilakukan mingguan dan prioritas diatur berdasarkan dependensi, dengan fitur akhir tetap dibatasi pada sepuluh fitur.

## 5. Rancangan awal use case

| Aktor | Tujuan/interaksi |
|---|---|
| Pengunjung | Analisis teks/URL/screenshot, koreksi OCR, melihat hasil dan rekomendasi, feedback, laporan anonim, registrasi/login |
| Pengguna berakun | Kemampuan umum ditambah menyimpan, melihat, dan menghapus riwayat miliknya |
| Moderator | Meninjau laporan teredaksi, menerima/menolak/menandai duplikasi, meninjau feedback sesuai kewenangan |
| Admin | Memantau statistik penggunaan, kegagalan layanan, OCR, versi/performa model, serta moderasi |
| Provider threat intelligence | Menyediakan hasil pemeriksaan reputasi URL |

AI, database, queue, dan worker OCR merupakan komponen internal pada batas sistem yang direncanakan; tidak digambar sebagai aktor manusia. Apabila OCR memakai provider eksternal, provider tersebut baru ditambahkan sebagai aktor pendukung. Relasi include/extend akan digunakan hanya jika sesuai kondisi alur, bukan untuk menggambar semua langkah pipeline.

Alur utama: input teks/URL → validasi dan redaksi → analisis sinyal yang relevan → hasil beserta bukti dan rekomendasi. Untuk screenshot: upload → OCR → review/koreksi pengguna → analisis final. Riwayat, feedback, dan laporan anonim merupakan interaksi lanjutan yang dapat dipilih pengguna.

## 6. Rancangan awal ERD

Entitas dasar mengikuti bagian 15 analisis: users, analyses, analysis_inputs, evidences, url_results, ocr_jobs, anonymous_reports, community_targets, feedback, model_versions, dan audit_logs.

Penyempurnaan yang perlu dilakukan ketika menggambar:

- analyses.user_id dapat kosong untuk analisis anonim; satu pengguna dapat memiliki banyak analisis.
- Satu analisis dapat memiliki banyak evidences, url_results, dan feedback; analysis_inputs memakai analysis_id sebagai PK sekaligus FK bila hubungan satu-ke-satu dipakai.
- Model OCR berjalan sebelum hasil analisis final tersedia. Hubungan ocr_jobs ke analyses harus mendukung job yang belum menghasilkan analisis, misalnya FK analysis_id opsional.
- anonymous_reports perlu FK community_target_id yang jelas; relasi tidak cukup diwakili oleh teks fingerprint yang kebetulan sama.
- Laporan anonim tidak diberi kewajiban FK pengguna. Identitas anti-abuse memakai hash token sementara sesuai konsep.
- model_version pada analisis perlu konsisten dengan model_versions; jika satu hasil memakai beberapa model, dibutuhkan relasi penghubung analysis_models agar versi model teks dan URL tidak tercampur.
- Agregat jumlah laporan dibedakan dari laporan mentah dan hanya dihitung menurut status/kebijakan deduplikasi yang ditetapkan.
- Audit log perlu mengidentifikasi aktor dan objek tindakan; referensi resource_id polimorfik tidak digambar sebagai FK biasa ke semua tabel.
- Retensi screenshot, hasil OCR sementara, dan riwayat teredaksi perlu dibedakan. Angka retensi pada analisis masih contoh kebijakan, bukan persetujuan final.

Daftar ini adalah rancangan awal, belum ERD final.

## 7. Cakupan wireframe yang direncanakan

1. Beranda/analisis dengan pilihan Teks, URL, dan Screenshot.
2. Upload screenshot dengan status proses dan kegagalan validasi/OCR.
3. Review dan koreksi hasil OCR dengan tombol analisis.
4. Hasil: tingkat/skor risiko, indikator, reputasi URL, sinyal komunitas, rekomendasi, dan feedback.
5. Registrasi/login untuk akses riwayat.
6. Daftar riwayat, detail hasil, dan hapus riwayat.
7. Form laporan anonim dan konfirmasi status pengiriman.
8. Dashboard admin berisi statistik dan status layanan.
9. Daftar/detail moderasi laporan serta tinjauan feedback.

Wireframe akan berupa kotak, label, dan kontrol monokrom yang dapat diedit di draw.io. Layar hasil juga perlu menunjukkan kondisi pemeriksaan eksternal tidak tersedia; riwayat perlu memiliki keadaan kosong. Contoh konten memakai data dummy.

## 8. Ketidaksesuaian sumber dan keputusan kerja

| Temuan | Penanganan |
|---|---|
| Roadmap analisis 16 minggu; worksheet 12 pertemuan | Pertahankan 12 kolom pertemuan. Pemetaan kalender dibuat eksplisit, tidak menyamakan 12 pertemuan dengan 16 minggu tanpa dasar. |
| Modul 1 menyebut pemeriksaan redirect | Tafsirkan sebagai analisis parameter/karakteristik URL, mengikuti analisis final yang melarang fetch dan mengikuti redirect langsung. |
| Template Lab 2.3 bertuliskan “Lampiran pengerjaan Lab 2.2” | Ini tampak sebagai ketidakkonsistenan label; bukti yang diminta di bagian itu adalah GitHub Pages. |
| W2_24 memakai EcoPoint dan fitur gamifikasi | Ambil pola penyajian saja; tidak memasukkan poin, leaderboard, atau klasifikasi sampah. |
| W2_24 menjelaskan workflow Jekyll | Tidak menganggap workflow itu sudah menjadi workflow CERNO. Penjelasan akhir harus sesuai file sebenarnya. |
| Nilai skor, target performa, statistik dashboard dalam analisis berupa contoh | Tidak ditulis sebagai hasil uji atau capaian nyata. |
| Klaim statistik eksternal dan kompetitor berasal dari jawaban Modul 1 | Tidak diverifikasi ulang pada tahap kajian konsep ini; jika dipakai sebagai fakta dalam narasi final, perlu pemeriksaan sumber primer. |

## 9. Urutan pekerjaan berikutnya

1. Tahap 1 (dokumen ini): kajian konsep, pemetaan tugas, dan identifikasi keputusan desain.
2. Tahap 2: isi naratif Lab 2.4, matriks use case–FR, Gantt, dan breakdown sesuai tiga anggota.
3. Tahap 3: buat use case diagram, ERD, dan low-fidelity wireframe dalam .drawio; periksa konsistensi antarartefak.
4. Tahap 4: masukkan jawaban dan gambar ke salinan worksheet DOCX, render setiap halaman, lalu periksa keterbacaan/layout.
5. Tahap bukti praktik: lengkapi lampiran GitHub dengan bukti aktual yang tersedia. Bukti pengembangan satu minggu tetap menunggu kegiatan tersebut benar-benar terjadi.

Status saat ini: kajian teks keenam sumber selesai; worksheet DOCX dan diagram final belum dibuat pada tahap pertama ini.
