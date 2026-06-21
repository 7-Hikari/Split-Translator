import webbrowser
import threading
import time
from flask import Flask, render_template, jsonify, request
import logging
from kontroller import pdf_upload, ambil_gambar, logika_proses_halaman, hapus_cache, initiate

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.addHandler(logging.NullHandler())

# Route utama untuk menampilkan UI
@app.route('/')
def index():
    return render_template('index.html')

doc_aktif = None
local_translation = True

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

    global local_translation

    data = request.json
    nomor_halaman = data.get('halaman')
    is_local = data.get('local_translation', local_translation)

    local = cek_lang(is_local)
    hasil = logika_proses_halaman(nomor_halaman, doc_aktif, local)

    if hasil['status']:
        return jsonify(hasil)
    return jsonify(hasil), 500

@app.route('/reset-dokumen', methods=['POST'])
def reset_dokumen():
    global doc_aktif
    doc_aktif = None
    hapus_cache()
    return jsonify({'status': True})

def cek_lang(is_local):
    global local_translation

    if is_local != local_translation:
        print(f"switch to {"lokal machine" if is_local else "Google Translate"}")
        hapus_cache()
        local_translation = is_local
        return local_translation
    return local_translation

def buka_browser():
    # Beri jeda agar server Flask benar-benar siap
    time.sleep(1.5)
    # Membuka browser bawaan sistem ke alamat local server
    webbrowser.open("http://127.0.0.1:5000")

@app.route('/exit', methods=['POST'])
def exit_app():
    import os
    import signal

    os.kill(os.getpid(), signal.SIGINT)
    return {'status': True, 'message': 'Aplikasi berhasil dimatikan.'}

if __name__ == '__main__':
    # Jalankan fungsi buka browser di thread terpisah agar tidak memblokir Flask
    threading.Thread(target=buka_browser, daemon=True).start()

    # Jalankan server Flask
    # debug=False direkomendasikan saat pakai threading buka browser agar tidak trigger 2 kali
    app.run(port=5000, debug=False)

initiate()
