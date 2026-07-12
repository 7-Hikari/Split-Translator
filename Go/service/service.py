import asyncio
from pathlib import Path
import os
from transformers import MarianTokenizer
import ctranslate2
import re

import winrt.system as wsystem
import winrt.windows.media.ocr as ocr
import winrt.windows.graphics.imaging as imaging
import winrt.windows.storage.streams as streams

MODEL_PATH = Path(os.getcwd()) / "lib/model"
tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-id")
translator = ctranslate2.Translator(str(MODEL_PATH), device="cpu")

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
            raise e

    return asyncio.run(async_ocr())

def translate(q):
    teks_bersih = q.replace("\n", " ").replace("\r", " ")
    teks_bersih = re.sub(r'\s+', ' ', teks_bersih).strip()

    kalimat_list = re.split(r'(?<=[.!?])\s+', teks_bersih)

    kalimat_list = [k.strip() for k in kalimat_list if k.strip()]
    Hasil_terjemahan = []

    try:
        for kalimat in kalimat_list:
            input_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(kalimat))
            hasil = translator.translate_batch([input_tokens])

            output_tokens = hasil[0].hypotheses[0]
            terjemahan = tokenizer.decode(tokenizer.convert_tokens_to_ids(output_tokens))

            Hasil_terjemahan.append(terjemahan)

        return " ".join(Hasil_terjemahan)
    except Exception as e:
        raise e