from pathlib import Path
import shutil
import fitz
import base64
import io
import os
import asyncio
from PIL import Image
from deep_translator import GoogleTranslator

# --- IMPORT WINDOWS OCR ---
import winrt.system as wsystem
import winrt.windows.media.ocr as ocr
import winrt.windows.graphics.imaging as imaging
import winrt.windows.storage.streams as streams

cache = {}
MODEL_PATH = Path(os.getcwd()) / "models_offline"
os.environ["XDG_DATA_HOME"] = str(MODEL_PATH / "data")
os.environ["XDG_CONFIG_HOME"] = str(MODEL_PATH / "config")
os.environ["XDG_CACHE_HOME"] = str(MODEL_PATH / "cache")

import argostranslate.package as package
import argostranslate.translate

def initiate():
    installed_packages = package.get_installed_packages()
    if installed_packages:
        return
    else:
        print("mengunduh paket terjemahan lokal [en -> id]")
        try:
            package.update_package_index()
            available_pack = package.get_available_packages()

            pack_en_id = next(filter(lambda p: p.from_code == 'en' and p.to_code == 'id', available_pack), None)

            if pack_en_id:
                package.install_from_path(pack_en_id.download())
                print("paket terjemahan lokal [en -> id] telah siap")
        except Exception as e:
            print(f"Gagal mengunduh paket terjemahan lokal : {e}")

    shutil.rmtree(str(MODEL_PATH / "cache"))

def pdf_upload(file):
    try:
        pdf_bytes = file.read()
        doc_aktif = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_halaman = len(doc_aktif)
        return {'status': True, 'doc_aktif': doc_aktif, 'total_halaman': total_halaman}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def ambil_gambar(doc_aktif, angka_halaman):
    try:
        page = doc_aktif[angka_halaman - 1]
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")
        encoded_img = base64.b64encode(img_data).decode('utf-8')
        return {'status': True, 'gambar_base64': f"data:image/png;base64,{encoded_img}"}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def _jalankan_windows_ocr(img_bytes):
    async def async_ocr():
        try:
            # 1. Buka Windows Stream di memori
            stream = streams.InMemoryRandomAccessStream()

            # 2. Paksa bytes ke dalam Unsigned Array ('B')
            win_array = wsystem.Array('B', img_bytes)

            # 3. Tulis array langsung ke stream Windows
            await stream.write_async(win_array)
            stream.seek(0)

            # 4. Gunakan Decoder Resmi Windows
            decoder = await imaging.BitmapDecoder.create_async(stream)

            # 5. Ambil SoftwareBitmap TANPA PARAMETER (Biar Windows yang urus formatnya)
            software_bitmap = await decoder.get_software_bitmap_async()

            # 6. Jalankan Engine OCR Windows
            engine = ocr.OcrEngine.try_create_from_user_profile_languages()
            if not engine:
                raise Exception("Gagal menginisialisasi Windows OcrEngine.")

            ocr_result = await engine.recognize_async(software_bitmap)
            return ocr_result.text

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Gagal di internal OCR: {e}\n")
            raise e

    return asyncio.run(async_ocr())

def logika_proses_halaman(nomor_halaman, doc_aktif, is_local):
    global cache

    if nomor_halaman in cache:
        return {'status': True, 'halaman': nomor_halaman, 'terjemahan': cache[nomor_halaman]}

    try:
        page = doc_aktif[int(nomor_halaman) - 1]
        text = page.get_text()

        # JALUR OCR WINDOWS JIKA HALAMAN BERUPA GAMBAR
        if not text.strip():
            # Naikkan kualitas render sedikit agar Windows OCR membaca lebih akurat
            pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5))
            img_bytes = pix.tobytes("png")

            # Panggil fungsi Windows OCR
            text = _jalankan_windows_ocr(img_bytes)

        if not text.strip():
            return {'status': True, 'halaman': nomor_halaman, 'terjemahan': 'Tidak ada teks terdeteksi di sini'}

        teks = text[:4500]

        if is_local:
            teks_terjemahan = argostranslate.translate.translate(q=teks, from_code='en', to_code='id')
        else:
            teks_terjemahan = GoogleTranslator(source='auto', target='id').translate(teks)

        html = teks_terjemahan.replace('\n', '<br>')
        cache[nomor_halaman] = html

        return {'status': True, 'halaman': nomor_halaman, 'terjemahan': html}
    except Exception as e:
        return {'status': False, 'message': str(e)}

def hapus_cache():
    global cache
    cache.clear()
