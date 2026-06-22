from pathlib import Path
import time
import fitz
import base64
import os
from deep_translator import GoogleTranslator

MODEL_PATH = Path(os.getcwd()) / "models_offline"
os.environ["XDG_DATA_HOME"] = str(MODEL_PATH / "data")
os.environ["XDG_CONFIG_HOME"] = str(MODEL_PATH / "config")
os.environ["XDG_CACHE_HOME"] = str(MODEL_PATH / "cache")

cache = {}

def jalankan_inisiasi():
    from service import initiate
    initiate()

def get_language_keys():
    return GoogleTranslator().get_supported_languages(as_dict=True)

def memproses_halaman(nomor_halaman, doc_aktif, lang, GoogleTr):
    from service import logika_proses_halaman
    return logika_proses_halaman(nomor_halaman, doc_aktif, lang, GoogleTr)

def pdf_upload(file):
    try:
        pdf_bytes = file.read()
        doc_aktif = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_halaman = len(doc_aktif)
        return {'status': True, 'doc_aktif': doc_aktif, 'total_halaman': total_halaman}
    except Exception as e:
        return {'status': False, 'message': "[PDF upload] " + str(e)}

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
        return {'status': False, 'message': "[Ambil gambar] " + str(e)}

def shutdown_server():
    import signal
    time.sleep(1)
    os.kill(os.getpid(), signal.SIGINT)

def buka_browser():
    import webbrowser
    time.sleep(0.5)
    webbrowser.open("http://127.0.0.1:5000")

def is_local(lang) -> bool:
    return lang['src'] == 'en' and lang['dst'] == 'id'

def hapus_cache():
    global cache
    cache.clear()
