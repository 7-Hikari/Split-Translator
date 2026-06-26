import tkinter as tk
from tkinter import ttk

def buat_ui_utama(root, router):
    # Header Toolbar
    header_frame = tk.Frame(root, bg="#2c3e50", padx=10, pady=10)
    header_frame.pack(side=tk.TOP, fill=tk.X)

    title_label = tk.Label(header_frame, text="PDF Translator App", font=("Arial", 12, "bold"), fg="white", bg="#2c3e50")
    title_label.pack(side=tk.LEFT, padx=10)

    router['btn_reset'] = tk.Button(header_frame, text="Reset", command=router['aksi_reset'], bg="#7f8c8d", fg="white", relief=tk.FLAT, state=tk.DISABLED)
    router['btn_reset'].pack(side=tk.LEFT, padx=10)

    frame_indicator = tk.Frame(header_frame, bg="#2c3e50")
    frame_indicator.pack(side=tk.LEFT, padx=15)
    router['page_checkbox_var'] = tk.BooleanVar(value=False)
    router['cek_btn'] = tk.Checkbutton(
        frame_indicator, text="var GoogleT",
        variable=router['page_checkbox_var'],
        fg="white", bg="#2c3e50", activebackground="#2c3e50",
        activeforeground="white", selectcolor="#3498db",
    )
    router['cek_btn'].pack(side=tk.LEFT)

    frame_nav = tk.Frame(header_frame, bg="#2c3e50")
    frame_nav.pack(side=tk.LEFT, padx=15)
    router['input_halaman'] = tk.Entry(frame_nav, width=5, justify="center")
    router['input_halaman'].insert(0, "1")
    router['input_halaman'].pack(side=tk.LEFT, padx=5)
    router['label_total_halaman'] = tk.Label(frame_nav, text="dari 0", fg="white", bg="#2c3e50")
    router['label_total_halaman'].pack(side=tk.LEFT, padx=5)
    router['btn_go'] = tk.Button(frame_nav, text="Go", command=router['aksi_go'], bg="#3498db", fg="white", relief=tk.FLAT, state=tk.DISABLED)
    router['btn_go'].pack(side=tk.LEFT, padx=5)

    frame_lang = tk.Frame(header_frame, bg="#2c3e50")
    frame_lang.pack(side=tk.LEFT, padx=20)
    router['cb_from_lang'] = ttk.Combobox(frame_lang, values=[], width=20, state="readonly")
    router['cb_from_lang'].set("English")
    router['cb_from_lang'].pack(side=tk.LEFT, padx=5)
    tk.Label(frame_lang, text="To", fg="white", bg="#2c3e50").pack(side=tk.LEFT, padx=5)
    router['cb_to_lang'] = ttk.Combobox(frame_lang, values=[], width=20, state="readonly")
    router['cb_to_lang'].set("Indonesian")
    router['cb_to_lang'].pack(side=tk.LEFT, padx=5)

    btn_exit = tk.Button(header_frame, text="Exit", command=router['aksi_exit'], bg="#dc3545", fg="white", relief=tk.FLAT)
    btn_exit.pack(side=tk.RIGHT, padx=10)

    # Panel Utama
    main_container = tk.Frame(root, bg="#f5f6fa")
    main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    panel_kiri = tk.Frame(main_container, bg="#7f8c8d", bd=1, relief=tk.SOLID)
    panel_kiri.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    router['panel_kiri'] = panel_kiri
    canvas_pdf = tk.Canvas(panel_kiri, bg="#7f8c8d")
    canvas_pdf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

    scrollbar_pdf = ttk.Scrollbar(panel_kiri, orient=tk.VERTICAL, command=canvas_pdf.yview)
    scrollbar_pdf.pack(side=tk.RIGHT, fill=tk.Y)

    canvas_pdf.config(yscrollcommand=scrollbar_pdf.set)
    router['canvas_pdf'] = canvas_pdf
    router['output_gambar'] = canvas_pdf.create_image(0, 0, anchor=tk.NW)

    router['drop_zone'] = tk.Frame(panel_kiri, bg="white", highlightbackground="#3498db", highlightthickness=3)
    router['drop_zone'].place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=350, height=150)

    router['lbl_drop_1'] = tk.Label(router['drop_zone'], text="Menyiapkan komponen mesin...", font=("Arial", 11, "bold"), fg="#e67e22", bg="white")
    router['lbl_drop_1'].pack(pady=(45, 5))
    router['lbl_drop_2'] = tk.Label(router['drop_zone'], text="Mohon jangan tutup aplikasi.", font=("Arial", 9), fg="#7f8c8d", bg="white")
    router['lbl_drop_2'].pack()

    panel_kanan = tk.Frame(main_container, bg="white", pady=20, padx=20)
    panel_kanan.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    scrollbar_translate = ttk.Scrollbar(panel_kanan, orient=tk.VERTICAL)
    scrollbar_translate.pack(side=tk.RIGHT, fill=tk.Y)

    tk.Label(panel_kanan, text="Hasil Terjemahan", font=("Arial", 12, "bold"), fg="#2c3e50", bg="white").pack(anchor=tk.W)
    tk.Frame(panel_kanan, height=1, bg="#eee").pack(fill=tk.X, pady=10)

    router['output_teks'] = tk.Text(
        panel_kanan, font=("Arial", 10),
        fg="#2c3e50", bg="white", relief=tk.FLAT,
        wrap=tk.WORD, yscrollcommand=scrollbar_translate.set)
    router['output_teks'].insert(tk.END, "Membuat sistem terjemahan lokal. Mohon tunggu...")
    router['output_teks'].pack(fill=tk.BOTH, expand=True)

    scrollbar_translate.config(command=router['output_teks'].yview)
