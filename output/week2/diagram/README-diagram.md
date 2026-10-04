# Diagram CERNO untuk Worksheet Week 2

## Berkas

- `CERNO-Use-Case.drawio`: dua halaman, **Analisis** dan **Akun dan Administrasi**.
- `CERNO-ERD.drawio`: dua halaman, **Analisis dan Riwayat** dan **Komunitas dan Moderasi**.
- Empat PNG merupakan pratinjau dengan geometri dan isi yang sama, dibuat dari sumber diagram. PNG bukan pengganti berkas draw.io yang dapat diedit.

Buka file `.drawio` dari menu **File > Open From > Device** di diagrams.net/draw.io, lalu pilih tab halaman di bagian bawah. Bentuk, teks, baris atribut, dan konektor merupakan objek native yang dapat diedit, bukan gambar yang ditempel. ERD memakai grup tabel; klik dua kali atau masuk ke grup untuk mengedit atribut.

## Dasar rancangan

Rancangan mengikuti jawaban `Modul 1_26.pdf`, scope final versi 2.0 `cerno-in-depth-analysis.md`, serta kebutuhan Lab 2.4 pada Modul 2. Diagram tidak memasukkan fitur EcoPoint dari referensi W2_24. Pembagian halaman hanya untuk keterbacaan: semua halaman menggambarkan satu sistem CERNO.

Ini adalah rancangan logis untuk tugas, bukan pernyataan bahwa sistem atau database sudah diimplementasikan. Wireframe dan pengisian DOCX belum termasuk hasil tahap ini.

## Daftar use case

| ID | Use case | Aktor utama |
|---|---|---|
| UC01 | Menganalisis teks pesan | Pengguna umum |
| UC02 | Menganalisis URL | Pengguna umum |
| UC03 | Menganalisis screenshot | Pengguna umum |
| UC04 | Meninjau dan mengoreksi teks hasil OCR | Pengguna umum melalui UC03 |
| UC05 | Melihat hasil dan rekomendasi tindakan | Pengguna umum |
| UC06 | Memberikan feedback | Pengguna umum |
| UC07 | Memeriksa reputasi URL | Provider threat intelligence sebagai aktor pendukung |
| UC08 | Mendaftar akun | Pengguna umum |
| UC09 | Login / logout | Pengguna yang mengakses akun |
| UC10 | Menyimpan hasil ke riwayat pribadi | Pengguna berakun |
| UC11 | Melihat riwayat dan detail analisis | Pengguna berakun |
| UC12 | Menghapus riwayat pribadi | Pengguna berakun |
| UC13 | Mengirim laporan anonim | Pengguna umum |
| UC14 | Memoderasi laporan komunitas | Moderator, Admin |
| UC15 | Memantau dashboard operasional dan model | Admin |
| UC16 | Meninjau feedback pengguna | Moderator, Admin |

`Pengguna umum` berarti semua orang yang memakai fungsi publik, baik tanpa maupun dengan akun. `Pengguna berakun` mewarisi akses umum. `Admin` mewarisi akses moderator. Login dan otorisasi merupakan prasyarat fungsi privat, bukan include yang memaksa login ulang setiap kali fungsi dijalankan. Logout hanya tersedia untuk sesi yang sudah login. Admin/moderator memakai mekanisme autentikasi akun yang sama.

Relasi penting:

- UC03 **include** UC04: pengguna wajib mendapat tahap review hasil OCR sebelum melanjutkan analisis; mengubah teksnya sendiri opsional.
- UC02 **include** UC07: pemeriksaan reputasi termasuk alur analisis URL. Bila provider tidak tersedia, hasil menandai pemeriksaan tidak lengkap.
- UC07 **extend** UC01 dengan kondisi URL ditemukan; analisis teks tanpa URL tidak membutuhkan pemeriksaan URL.
- UC06 **extend** UC05 ketika pengguna memilih memberi feedback.

UC01/UC03 mencakup validasi, redaksi, ekstraksi URL, penilaian sinyal yang relevan, dan keluaran risiko. Semua detail pipeline tidak dijadikan use case terpisah. UC05 mencakup risk score, tingkat risiko, evidence, hasil URL, sinyal komunitas, rekomendasi, dan arah verifikasi/pelaporan resmi. UC13 mencakup konfirmasi pengiriman dan status awal, bukan daftar laporan publik.

## ERD dan kardinalitas

ERD memiliki **14 entitas unik**. `users` dan `analyses` ditampilkan lagi sebagai referensi pada halaman kedua, bukan tabel duplikat.

| Relasi | Makna |
|---|---|
| users — analyses | Pengguna memiliki 0..* analisis; analisis memiliki 0..1 pemilik akun. |
| analyses — analysis_inputs | Analisis memiliki 0..1 input tersimpan; setiap input milik tepat satu analisis. |
| analyses — evidences | Analisis memiliki 0..* indikator; setiap indikator milik tepat satu analisis. |
| analyses — url_results | Analisis memiliki 0..* hasil URL; setiap hasil URL milik tepat satu analisis. |
| analyses — feedback | Analisis memiliki 0..* feedback; setiap feedback merujuk tepat satu analisis. |
| analyses — ocr_jobs | Kedua sisi 0..1; analisis teks/URL tidak memakai job OCR dan job yang belum selesai dapat belum memiliki analisis. |
| analyses — analysis_models — model_versions | Banyak-ke-banyak melalui PK gabungan: mencatat setiap versi model yang dipakai pada hasil tersebut. |
| community_targets — anonymous_reports | Target memiliki 0..* laporan; setiap laporan menunjuk tepat satu target. |
| anonymous_reports — report_moderations | Laporan memiliki 0..* riwayat keputusan moderasi. |
| users — report_moderations | Setiap keputusan dibuat satu akun moderator/admin; satu akun dapat membuat banyak keputusan. |
| users — audit_logs | Akun dapat menghasilkan banyak audit; audit sistem dapat tidak memiliki akun aktor. |
| analyses — analysis_community_matches — community_targets | Banyak-ke-banyak: mencatat target komunitas yang relevan dan snapshot sinyal saat analisis. |

PK gabungan ditandai `PK,FK` pada masing-masing kolom anggotanya. `?` berarti nullable. ID referensi mengikuti nama FK: `moderator_id` dan `actor_user_id` menunjuk `users.id`; `report_id` menunjuk `anonymous_reports.id`; kolom penghubung lainnya menunjuk `id` tabel dengan nama yang sesuai.

## Keputusan desain dan constraint tambahan

1. **Scope AI:** hanya tingkat risiko, bukan jenis scam. `risk_score` menggunakan skala 0–100. Skor dan level boleh NULL ketika analisis belum selesai; analisis selesai wajib memiliki keduanya. Label risiko NULL berlaku untuk keseluruhan field, bukan hanya nilai `high`.
2. **Versi model:** `analysis_models` menormalisasi field model_version pada konsep awal karena satu hasil dapat memakai model teks dan URL yang berbeda. `model_versions` harus memiliki UNIQUE(model_name, version). Model aktif yang sama dapat dipakai pada banyak analisis. Versi OCR dicatat dalam job.
3. **Riwayat dan consent:** `consent_to_store` untuk menyimpan riwayat teredaksi dibedakan dari `consent_to_train`. Analisis anonim menggunakan penyimpanan sementara dengan TTL; tidak otomatis menjadi riwayat permanen. Input mentah diproses sementara. `analysis_inputs` hanya menyimpan bentuk yang telah diredaksi sesuai persetujuan dan retensi.
4. **OCR:** asumsi satu upload/job menghasilkan paling banyak satu analisis; percobaan ulang worker memperbarui job yang sama. `analysis_id` pada job memiliki FK opsional dan UNIQUE. Screenshot berada di object storage privat sementara, bukan BLOB dalam database. Setelah penghapusan file, object_key dapat dikosongkan. Akses job memakai token terbatas, disimpan sebagai hash. Masa retensi final ditentukan saat implementasi.
5. **Laporan anonim:** tidak ada FK reporter ke users. Token anonim bukan jaminan satu manusia unik; hitungan dan anti-abuse masih perlu kontrol moderasi. Network fingerprint berumur pendek dan dihapus sesuai network_expires_at.
6. **Deduplikasi:** gunakan UNIQUE(community_target_id, reporter_token_hash, dedupe_window_start). Pengiriman duplikat dalam jendela yang sama mengembalikan konfirmasi duplikat tanpa menambah row/hitungan. Status `duplicate` pada moderasi dapat digunakan untuk duplikasi yang ditemukan kemudian. Panjang jendela adalah konfigurasi implementasi, belum ditentukan oleh diagram.
7. **Hitungan komunitas:** accepted/rejected report count adalah agregat menurut status laporan; unique_report_count menghitung token berbeda pada jendela agregasi yang ditetapkan, bukan sekadar jumlah row. Sinyal yang digunakan untuk risiko berasal dari laporan valid dan dibatasi bobotnya. Tidak ada field untuk menuduh identitas tertentu sebagai pelaku.
8. **Snapshot:** `analysis_community_matches` ditambahkan agar perubahan agregat komunitas di masa depan tidak mengubah penjelasan hasil analisis lama. Target dapat berupa teks, URL, atau domain hasil normalisasi. Input laporan pengguna tetap teks atau URL.
9. **Moderasi:** `report_moderations` menyimpan sejarah keputusan, sementara `anonymous_reports.moderation_status` menyimpan status terkini. Perubahan status, agregat, catatan moderasi, dan audit harus konsisten dalam transaksi. Catatan alasan juga perlu redaksi jika mengandung data pribadi.
10. **Audit:** `resource_type` + `resource_id` adalah referensi polimorfik tingkat aplikasi. Tidak digambar sebagai FK SQL ke banyak tabel. `actor_type=system` dapat menggunakan actor_user_id NULL.
11. **Penghapusan:** detail analisis (inputs, evidences, URL, feedback, model links, community matches) mengikuti penghapusan/retensi analisis. Job OCR dapat mempertahankan metadata sementara dengan analysis_id NULL; file sementara tetap dihapus. Rekaman moderasi dan model yang masih direferensikan tidak boleh dihapus sembarangan.
12. **Dashboard:** jumlah analisis, distribusi risiko, latency, feedback, dan backlog dapat dihitung dari data terkait; model metrics berasal dari model_versions. Log monitoring rinci dapat disimpan oleh layanan observabilitas, sehingga tidak semua telemetry dijadikan tabel relasional.

## Pemeriksaan artefak

Struktur XML native, keunikan ID, dan referensi parent/source/target diperiksa oleh generator. Pratinjau PNG diperiksa secara visual, termasuk label, arah panah, dan area teks. Pratinjau berasal dari generator lokal yang sama; belum dilakukan ekspor ulang menggunakan aplikasi draw.io. Berkas sumber generator disimpan di `src/build_diagrams.py` untuk reproduksi.
