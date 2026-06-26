# PDF OCR & Translator

Aplikasi desktop sederhana yang memungkinkan Anda mengunggah file PDF, mengekstrak teks dari halaman (menggunakan OCR jika diperlukan), dan menerjemahkannya ke Bahasa Indonesia. Aplikasi ini mendukung terjemahan menggunakan layanan online (Google Translate) atau terjemahan lokal (Argos Translate) jika paket bahasa sudah terinstal.

## Fitur Utama

*   **Unggah PDF**: Memuat file PDF melalui antarmuka drag-and-drop atau pemilihan file.
*   **Tampilan PDF**: Menampilkan halaman PDF secara bertahap saat Anda menggulir.
*   **OCR Windows**: Menggunakan engine OCR bawaan Windows untuk mengekstrak teks dari gambar atau halaman PDF yang tidak dapat dibaca teksnya.
*   **Terjemahan Dua Arah**:
    *   **Terjemahan Lokal**: Menggunakan Argos Translate (memerlukan unduhan paket bahasa `en` ke `id`).
    *   **Terjemahan Online**: Menggunakan Google Translate dengan pilihan bahasa sumber (otomatis, Inggris, Prancis, Spanyol, dll.).
*   **Navigasi Halaman**: Pindah antar halaman PDF dengan mudah.
*   **Reset Aplikasi**: Mengulang proses dari awal.
*   **Exit Aplikasi**: Mematikan server backend Flask.

## Prasyarat

Untuk menjalankan aplikasi ini, Anda memerlukan:

*   **Python 3.8+**: Pastikan Anda memiliki Python terinstal di sistem Anda.
*   **Windows**: Aplikasi ini menggunakan modul `winrt` untuk OCR, yang spesifik untuk Windows.
*   **Perpustakaan Python**: Instal dependensi berikut menggunakan pip:

    ```bash
    pip install -r requirements.txt
    ```
    *Catatan*: Modul `winrt` mungkin memerlukan instalasi tambahan tergantung pada versi Windows Anda. Jika Anda mengalami masalah, pastikan Anda menggunakan versi Windows yang mendukungnya (Windows 10 versi 1809 atau lebih baru).

## Menjalankan Aplikasi

1.  **Clone Repository**:
    ```bash
    git clone <URL_REPOSITORY_ANDA>
    cd <NAMA_FOLDER_PROYEK>
    ```

2.  **Siapkan Lingkungan Virtual (Opsional tapi direkomendasikan)**:
    ```bash
    python -m venv venv
    # Aktifkan environment:
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Instal Dependensi**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Jika Anda memiliki file `requirements.txt`. Jika tidak, instal manual seperti di bagian Prasyarat)*

4.  **Unduh Paket Terjemahan Lokal (Argos Translate)**:
    Saat pertama kali dijalankan, aplikasi akan mencoba mengunduh paket terjemahan `en` ke `id` untuk Argos Translate. Pastikan Anda memiliki koneksi internet saat pertama kali menjalankan aplikasi jika Anda ingin menggunakan terjemahan lokal.

5.  **Jalankan Aplikasi**:
    ```bash
    python app.py
    ```

## Membangun Executable dengan PyInstaller

Untuk membuat file executable mandiri yang dapat dijalankan di Windows tanpa perlu instalasi Python, Anda dapat menggunakan `pyinstaller`.

1.  **Instal PyInstaller**:
    ```bash
    pip install pyinstaller
    ```

2.  **Bangun Executable**:
    Buka terminal di direktori root proyek Anda dan jalankan perintah berikut:

    ```bash
    pyinstaller --onedir --clean --collect-submodules winrt --name SplitTranslator app.py
    ```

    *   `--onedir`: Membuat file executable dengan folder dll.
    *   `--windowed` (`-w`): Agar tidak menampilkan jendela konsol saat aplikasi berjalan.
    *   `--clean`: Membersihkan cache `pyinstaller` sebelum build.
    *   `--add-data "templates;templates"`: Menyertakan folder `templates` dalam executable.
    *   `--add-data "static;static"`: Menyertakan folder `static` dalam executable.
    *   `--collect-submodules winrt`: Memastikan modul `winrt` dikumpulkan dengan benar.
    *   `--name PdfTranslator`: Menentukan nama file output executable.
    *   `app.py`: File skrip utama Flask Anda.

    Setelah proses build selesai, Anda akan menemukan file executable (`PdfTranslator.exe`) di dalam folder `dist` di direktori proyek Anda.

## Catatan Tambahan

*   **OCR Windows**: Fitur OCR hanya berfungsi pada sistem operasi Windows.
*   **Terjemahan Online**: Terjemahan menggunakan Google Translate memerlukan koneksi internet aktif.
*   **Argos Translate**: Untuk terjemahan lokal, pastikan paket bahasa yang diperlukan sudah terunduh saat pertama kali aplikasi dijalankan dengan opsi terjemahan lokal aktif.
