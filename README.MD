# tesOcr

Aplikasi ini dirancang sebagai penerjemah dokumen PDF per halaman secara offline.

## Fitur utama
- Dua panel: kiri untuk dokumen asli, kanan untuk terjemahan.
- Penerjemahan halaman aktif secara otomatis.
- Menggunakan model dari Helsinki-NLP di Huggingface.
- Target awal: terjemahan bahasa Inggris ke Indonesia.
- Menggunakan win-ocr, untuk file pdf yang full gambar (seperti hasil scanner)

## Catatan projek
- Menggunakan ocr asli dari windows supaya ukuran aplikasi tidak besar
- Apabila Anda sebagai developer boleh membantu untuk update atau merampingkan ukuran aplikasi
- Lisensi MIT

## Prasyarat
- Windows
- Go (disarankan 1.20+)
- Node.js
- Python 3.10+ (untuk servis dan konversi model)
- `pyinstaller` untuk membungkus service Python
- `ct2-marian-converter` untuk mengonversi model Marian ke format CTranslate2
- Wails CLI untuk membangun aplikasi desktop

## Instalasi Wails
1. Pastikan Go dan Node.js sudah terpasang.
2. Pasang Wails CLI dengan perintah:

   ```powershell
   go install github.com/wailsapp/wails/v3/cmd/wails@latest
   ```

3. Tambahkan `%GOPATH%\bin` ke PATH apabila diperlukan.
4. Verifikasi instalasi:

   ```powershell
   wails doctor
   ```

## Langkah persiapan
1. Clone repositori ini.
2. Masuk ke folder `service`
3. Buat dan aktifkan virtual environment:
4. Install dependensi Python:

   ```powershell
   pip install -r requirements.txt
   ```

## Konversi model
1. Unduh model penerjemah dari Helsinki-NLP sesuai bahasa yang diinginkan.
2. Jalankan `ct2-marian-converter` untuk mengonversi model ke format CTranslate2.
3. Output converter sengaja ditempatkan di folder build Wails, yaitu:

   ```text
   Go/build/bin/lib/model
   ```

4. Contoh perintah:

   ```powershell
   ct2-marian-converter --model_path "path\to\model.npz" --vocab_paths "path\to\model.vocab.yml" --output_dir "Go\build\bin\lib\model" --quantization int8 --force
   ```

## Build service Python
1. Dari dalam folder `service`, jalankan pyinstaller untuk membuat executable service.
2. Contoh perintah umum:

   ```powershell
   pyinstaller --onedir --windowed --collect-submodules=winrt --name=services api.py
   ```

* onedir atau onefile: opsional (pilih salah satu)

3. Pastikan executable service yang dihasilkan dapat diakses oleh aplikasi Wails. Atau tempatkan hasil build seluruhnya di:
  
  ```text
  Go\build\bin\lib
  ```

## Build aplikasi Wails
1. Kembali ke direktori `Go`:

   ```powershell
   cd ..\Go
   ```

2. Jalankan perintah build Wails:

   ```powershell
   wails build -devtools
   ```

* devtools: opsional

3. Hasil build akan dihasilkan di folder `Go/build`.

## Catatan
- `ct2-marian-converter` memang sengaja ditempatkan di folder build Wails agar model siap dipaketkan.
- Jika ingin mengganti model, ulangi langkah konversi dan pastikan output tetap di `Go/build/bin/lib/model`.
