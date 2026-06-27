import asyncio
import shutil
import fitz
from deep_translator import GoogleTranslator

import winrt.system as wsystem
import winrt.windows.media.ocr as ocr
import winrt.windows.graphics.imaging as imaging
import winrt.windows.storage.streams as streams

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

def logika_proses_halaman(nomor_halaman, doc_aktif, lang, GoogleTr = False):
    import argostranslate.translate
    import kontroller

    if nomor_halaman in kontroller.cache:
        return {'status': True, 'halaman': nomor_halaman, 'terjemahan': kontroller.cache[nomor_halaman]}

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
            return {'status': True, 'halaman': nomor_halaman, 'terjemahan': '(Tidak ada teks terdeteksi di sini)'}

        text = text.replace('-\n', '')

        if kontroller.is_local(lang) and not GoogleTr:
            teks_terjemahan = argostranslate.translate.translate(q=text, from_code='en', to_code='id')
        else:
            teks = text[:4500]
            teks_terjemahan = GoogleTranslator(source=lang['src'], target=lang['dst']).translate(teks)

        kontroller.cache[nomor_halaman] = teks_terjemahan

        return {'status': True, 'halaman': nomor_halaman, 'terjemahan': teks_terjemahan}
    except Exception as e:
        return {'status': False, 'message': "[Proses halaman] " + str(e)}


def initiate() -> bool:
    import argostranslate.package as package

    installed_packages = package.get_installed_packages()
    if installed_packages == []:
        print("mengunduh paket terjemahan lokal [en -> id]...")
        try:
            package.update_package_index()
            available_pack = package.get_available_packages()

            print("menelusuri paket yang tersedia...")
            pack_en_id = next(filter(lambda p: p.from_code == 'en' and p.to_code == 'id', available_pack), None)
            print("mengunduh...")
            if pack_en_id:
                package.install_from_path(pack_en_id.download())
                print("paket terjemahan lokal [en -> id] telah siap")
        except Exception as e:
            print(f"Gagal mengunduh paket terjemahan lokal : {e}")
            return False

    print("Membersihkan cache...")
    import kontroller
    shutil.rmtree(str(kontroller.MODEL_PATH / "cache/argos-translate"))
    return True
