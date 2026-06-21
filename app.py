import threading
import multiprocessing
import sys
import os
from flask import Flask, render_template, jsonify, request
import logging

print("Memuat terjemahan lokal. Mohon tunggu...", flush=True)

from kontroller import pdf_upload, ambil_gambar, logika_proses_halaman, hapus_cache, initiate, get_language_keys, is_local

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

app = Flask(
    __name__,
    template_folder=get_resource_path("templates"),
    static_folder=get_resource_path("static")
)

log = logging.getLogger('werkzeug')
log.addHandler(logging.NullHandler())

doc_aktif = None
translation = {'src': 'en', 'dst': 'id'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/languages')
def get_languages():
    return jsonify({'status': True, 'languages': get_language_keys()})

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    global doc_aktif

    if 'pdf_file' not in request.files:
        return jsonify({'status': False, 'message': 'Tidak ada file dikirim'})

    file = request.files['pdf_file']

    if file.filename is None:
        return jsonify({'status': False, 'message': 'Nama file kosong'})
    if file.filename == '':
        return jsonify({'status': False, 'message': 'Nama file kosong'})

    if file and file.filename.endswith('.pdf'):
        hasil = pdf_upload(file)

        if hasil['status']:
            doc_aktif = hasil['doc_aktif']
            hapus_cache()

            return jsonify({
                'status': True,
                'message': 'File berhasil diproses',
                'total_halaman': hasil['total_halaman']
            })
        else:
            return jsonify(hasil), 500

    return jsonify({'status': False, 'message': 'Format harus PDF'})

@app.route('/ambil-gambar-halaman/<int:angka_halaman>', methods=['GET'])
def ambil_gambar_halaman(angka_halaman):
    global doc_aktif
    if doc_aktif is None:
        return jsonify({'status': False, 'message': 'Belum ada dokumen yang dibuka'}), 400

    hasil = ambil_gambar(doc_aktif, angka_halaman)
    if hasil['status']:
        return jsonify(hasil)
    else:
        return jsonify(hasil), 500

# Kerangka Route untuk memproses halaman PDF nanti (Controller)
@app.route('/proses-halaman', methods=['POST'])
def proses_halaman():

    global translation

    data = request.json
    nomor_halaman = data.get('halaman')
    src = data.get('source')
    dst = data.get('dest')
    GoogleTr = data.get('Google', False)

    if src == dst:
        return jsonify({'status': False, 'message': 'apasih'})

    lang = cek_lang({'src': src, 'dst': dst})

    hasil = logika_proses_halaman(nomor_halaman, doc_aktif, lang, GoogleTr)

    if hasil['status']:
        return jsonify(hasil)
    return jsonify(hasil), 500

@app.route('/reset-dokumen', methods=['POST'])
def reset_dokumen():
    global doc_aktif
    doc_aktif = None
    hapus_cache()
    return jsonify({'status': True})

def cek_lang(lang):
    global translation
    is_changed = lang != translation

    if is_changed:
        print(f"switch to {"lokal machine" if is_local(lang) else "Google Translate"}")
        hapus_cache()
        translation = lang
        return translation
    return translation

@app.route('/exit', methods=['POST'])
def exit_app():
    import os
    import signal

    os.kill(os.getpid(), signal.SIGINT)
    return {'status': True, 'message': 'Aplikasi berhasil dimatikan.'}

if __name__ == '__main__':
    multiprocessing.freeze_support()
    threading.Thread(target=initiate, daemon=True).start()

    sys.stdout.write("[SISTEM] Menjalankan Server...\n")
    sys.stdout.flush()
    app.run(debug=False, port=5000, use_reloader=False)
