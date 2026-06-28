# TikTok Live Comment Listener

Program ini menggunakan library [TikTokLive](https://github.com/isaackogan/TikTokLive) untuk terhubung ke live stream TikTok dan mencatat aktivitas seperti komentar, like, share, dan jumlah penonton. Semua data disimpan ke file JSON.

## 1. Persyaratan

Pastikan Anda telah menginstal dependensi berikut:

```bash
pip install TikTokLive python-dotenv
```

## 2. File yang Dibutuhkan

Buat file konfigurasi lingkungan dan file JSON konfigurasi sebelum menjalankan program.

### File .env

```env
CONFIG_FILE=config.json
TARGET=nama_user_tiktok
VIEWERS_FILE=viewers.json
KOMENTAR_FILE=komentar.json
LIKE_FILE=like.json
SHARE_FILE=share.json
```

### File config.json

```json
{
  "DURATION": 60,
  "DELAY": 60
}
```

- `DURATION`: Durasi dalam detik sebelum client memutus koneksi setelah terhubung.
- `DELAY`: Jeda waktu saat mengecek apakah target sedang live.

## 3. Alur Program

Skrip utama berada di [TiktokLive.py](TiktokLive.py). Program akan:

- Memeriksa apakah akun target sedang live secara berkala,
- Terhubung ke live stream saat akun sedang live,
- Mencatat event berikut:
  - Komentar lewat `CommentEvent`,
  - Like lewat `LikeEvent`,
  - Share lewat `SocialEvent`,
  - Total viewers lewat `RoomUserSeqEvent`,
- Menyimpan data ke file JSON yang telah ditentukan.

## 4. Output yang Dihasilkan

Saat program berjalan, file berikut akan dibuat atau diperbarui:

- [komentar.json](komentar.json)
- [like.json](like.json)
- [share.json](share.json)
- [viewers.json](viewers.json)

Setiap entri berisi timestamp dan data sesuai event yang diterima.

## 5. Menjalankan Program

```bash
python TiktokLive.py
```

Program akan terus memantau akun target sampai koneksi selesai sesuai `DURATION`, lalu menyimpan data terakhir ke file JSON.

## Lisensi

Proyek ini menggunakan lisensi MIT. Lihat [LICENSE](LICENSE) untuk detail lebih lanjut.
