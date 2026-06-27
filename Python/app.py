import threading
import multiprocessing
import io
import base64
import os
import customtkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

import home, panel_debug

ctrl = None #type : module
doc_aktif = None
gambar_halaman = None
total_halaman = 0
translation = {'src': 'en', 'dst': 'id'}
list_bahasa = {} # type: dict
ui = {}
halaman_saat_ini = 1
GoogleT = False

def cek_lang(lang):
    global translation, GoogleT
    is_changed = lang != translation
    is_local = ctrl.is_local(lang)

    if is_changed:
        print(f"switch to {"lokal machine" if is_local else "Google Translate"}")
        ctrl.hapus_cache()
        translation = lang
        return translation
    return translation

def teks_terjemahan(teks):
    ui['output_teks'].delete('1.0', tk.END)
    ui['output_teks'].insert(tk.END, teks)

def background_inisiasi():
    global ctrl
    import kontroller as modul
    ctrl = modul
    print("[SISTEM] Memuat model bahasa lokal...")
    inisiasi_selesai() if ctrl.jalankan_inisiasi() else print("Gagal memuat model")

def inisiasi_selesai():
    global list_bahasa
    ui['btn_reset'].configure(state=tk.NORMAL)
    ui['btn_go'].configure(state=tk.NORMAL)
    ui['drop_zone'].bind("<Button-1>", pilih_file)
    ui['lbl_drop_1'].configure(text="Klik untuk memilih file")
    ui['lbl_drop_2'].configure(text="Jika tidak merespon, tunggu beberapa saat")
    teks_terjemahan("Sistem siap. Silakan unggah dokumen PDF untuk memulai.")

    try:
        list_bahasa = ctrl.get_language_keys() #type: ignore
        bahasa = [nama.title() for nama in list_bahasa.keys()] # type: ignore
        bahasa.sort()

        ui['cb_from_lang'].configure(values=bahasa)
        ui['cb_to_lang'].configure(values=bahasa)
    except Exception as e:
        print(f'[SISTEM] Gagal memuat bahasa : {e}')

    print("[SISTEM] Semua Model AI Siap Digunakan!")

def on_canvas_scroll(event):
    global halaman_saat_ini, total_halaman, doc_aktif
    if doc_aktif is None: return
    if event.delta < 0:
        target = min(halaman_saat_ini + 1, total_halaman)
    else:
        target = max(1, halaman_saat_ini - 1)

    if target != halaman_saat_ini:
        halaman_saat_ini = target
        ui['input_halaman'].delete(0, tk.END)
        ui['input_halaman'].insert(0, str(halaman_saat_ini))
        ambil_terjemahan(halaman_saat_ini)

    return "break"

def pilih_file(event=None):
    global doc_aktif, total_halaman, halaman_saat_ini
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        print(f"[USER] Memilih file: {os.path.basename(file_path)}")
        ui['lbl_drop_1'].configure(text="Sedang memproses dokumen...")
        ui['lbl_drop_2'].configure(text="Mohon tunggu.")
        root.update_idletasks()

        hasil = ctrl.pdf_upload(file_path)

        if hasil['status']:
            doc_aktif = hasil['doc_aktif']
            ctrl.hapus_cache()
            total_halaman = hasil['total_halaman'] # Update global total_halaman
            halaman_saat_ini = 1
            ui['label_total_halaman'].configure(text=f"dari {total_halaman}")
            ui['input_halaman'].delete(0, tk.END)
            ui['input_halaman'].insert(0, str(halaman_saat_ini))
            ui['drop_zone'].place_forget()
            print(f"[SISTEM] Sukses memuat PDF. Total: {total_halaman} Halaman.")

            # Bind scroll event ke canvas
            ui['canvas_pdf'].bind("<MouseWheel>", on_canvas_scroll)

            ambil_terjemahan(1)
            muat_gambar(1) # Tambahkan ini untuk memuat gambar halaman pertama setelah PDF diunggah
        else:
            print(f"[ERROR] Gagal memproses PDF: {hasil.get('message', '')}")
            reset_app()

def muat_gambar(angka_halaman):
    global doc_aktif
    if doc_aktif is None: return

    hasil = ctrl.ambil_gambar(doc_aktif, angka_halaman)
    if hasil['status']:
        try:
            data_base64 = hasil['gambar_base64']
            if "," in data_base64:
                data_base64 = data_base64.split(",")[1]
            biner_gambar = base64.b64decode(data_base64)
            stream = io.BytesIO(biner_gambar)
            pill_gambar = Image.open(stream)

            ui['canvas_pdf'].update_idletasks()
            lebar_panel = ui['canvas_pdf'].winfo_width() - 40
            if lebar_panel > 10:
                rasio = lebar_panel / float(pill_gambar.size[0])
                tinggi_baru = int((float(pill_gambar.size[1]) * float(rasio)))
                pill_gambar = pill_gambar.resize((lebar_panel, tinggi_baru), Image.Resampling.LANCZOS)

                gambar_laman = ImageTk.PhotoImage(pill_gambar)
                ui['canvas_pdf'].itemconfig(ui['output_gambar'], image=gambar_laman)
                ui['canvas_pdf'].image = gambar_laman
                ui['canvas_pdf'].configure(scrollregion=(0, 0, lebar_panel, tinggi_baru))
        except Exception as e:
            print(f"[ERROR] Gagal merender gambar: {e}")
    else:
        print(hasil['message'])

def ambil_terjemahan(nomor_halaman):
    global doc_aktif, list_bahasa, GoogleT
    src = list_bahasa.get(ui['cb_from_lang'].get().lower())
    dst = list_bahasa.get(ui['cb_to_lang'].get().lower())

    if src == dst: return

    teks_terjemahan("Menerjemahkan halaman... Mohon tunggu...")
    root.update_idletasks()

    lang = cek_lang({'src':src, 'dst': dst})
    hasil = ctrl.memproses_halaman(int(nomor_halaman), doc_aktif, lang, GoogleT)

    muat_gambar(nomor_halaman)

    if hasil['status']:
        teks_terjemahan(hasil['terjemahan'])
    else:
        teks_terjemahan(f"Gagal: {hasil.get('message', 'Terjadi kesalahan sistem.')}")
        print(f"[ERROR] Halaman {nomor_halaman} gagal: {hasil.get('message', '')}")

def reset_app():
    global doc_aktif
    doc_aktif = None
    ctrl.hapus_cache()
    ui['label_total_halaman'].configure(text="dari 0")
    ui['input_halaman'].delete(0, tk.END)
    ui['input_halaman'].insert(0, "1")
    teks_terjemahan("Silakan unggah dokumen PDF untuk memulai.")
    ui['canvas_pdf'].image=None
    ui['lbl_drop_1'].configure(text="Klik untuk memilih file")
    ui['lbl_drop_2'].configure(text="")
    ui['drop_zone'].place(relx=0.5, rely=0.5, anchor=tk.CENTER)

def aksi_navigasi_go():
    try:
        global halaman_saat_ini
        target = int(ui['input_halaman'].get())
        if 1 <= target <= total_halaman:
            halaman_saat_ini = target
            ambil_terjemahan(halaman_saat_ini)
        else:
            messagebox.showwarning("Peringatan", f"Masukkan 1 - {total_halaman}")
    except ValueError:
        messagebox.showwarning("Peringatan", "Input harus angka!")

def setGoogleTerjemahan(*args):
    global GoogleT, halaman_saat_ini
    GoogleT = not GoogleT
    print(f"Var Google Translate = {GoogleT}")
    ambil_terjemahan(halaman_saat_ini)

def exit_app():
    if messagebox.askyesno("Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?"):
        root.quit()

if __name__ == '__main__':
    multiprocessing.freeze_support()

    root = tk.CTk()
    root.title("PDF OCR & Translator Offline")
    root.geometry("1100x750")
    root.configure(bg="#f5f6fa")

    ui['aksi_reset'] = reset_app
    ui['aksi_go'] = aksi_navigasi_go
    ui['aksi_exit'] = exit_app

    panel_debug.buat_panel_debug(root)
    home.buat_ui_utama(root, ui)
    ui['page_checkbox_var'].trace_add('write', setGoogleTerjemahan)

    threading.Thread(target=background_inisiasi, daemon=True).start()
    root.mainloop()
