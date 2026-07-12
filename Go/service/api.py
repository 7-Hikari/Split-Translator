from flask import Flask, request, jsonify
import service
# import os

# os.environ["XDG_DATA_HOME"] = str(MODEL_PATH / "data")
# os.environ["XDG_CONFIG_HOME"] = str(MODEL_PATH / "config")
# os.environ["XDG_CACHE_HOME"] = str(MODEL_PATH / "cache")

app = Flask(__name__)

@app.route("/cek", methods=['GET'])
def cek():
    return "OK", 200

@app.route('/services', methods=['POST'])
def proses_gambar():
    try:
        img_bytes = request.data

        teks_asli = service._jalankan_windows_ocr(img_bytes)
        if not teks_asli.strip():
            return jsonify({'status': True, 'terjemahan': '(Tidak ada teks terdeteksi)'})
        
        if(request.args.get('lokal')):
            terjemahan = service.translate(q=teks_asli)
            return jsonify({'status': True, 'terjemahan': terjemahan})
            
        return jsonify({'status':True, 'terjemahan':teks_asli})

    except Exception as e:
        return jsonify({'status': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=False, threaded=True)