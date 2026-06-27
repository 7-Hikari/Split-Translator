import customtkinter as ctk

def buat_ui_utama(root, router):
    # Header Toolbar
    header_frame = ctk.CTkFrame(root, bg_color="white", fg_color="white")
    header_frame.pack(side=ctk.TOP, fill=ctk.X)

    title_label = ctk.CTkLabel(header_frame, text="PDF Translator App", font=("Arial", 16, "bold"), fg_color="white")
    title_label.pack(side=ctk.LEFT, padx=10)

    router['btn_reset'] = ctk.CTkButton(header_frame, text="Reset", command=router['aksi_reset'], bg_color="#7f8c8d", width=80, state=ctk.DISABLED)
    router['btn_reset'].pack(side=ctk.LEFT, padx=10)

    frame_indicator = ctk.CTkFrame(header_frame, bg_color="#2c3e50")
    frame_indicator.pack(side=ctk.LEFT, padx=15)
    router['page_checkbox_var'] = ctk.BooleanVar(value=False)
    router['cek_btn'] = ctk.CTkCheckBox(
        frame_indicator, text="var GoogleT",
        variable=router['page_checkbox_var'],
        text_color="blue", bg_color="transparent",
    )
    router['cek_btn'].pack(side=ctk.LEFT)

    frame_nav = ctk.CTkFrame(header_frame, bg_color="transparent")
    frame_nav.pack(side=ctk.LEFT, padx=20)
    router['input_halaman'] = ctk.CTkEntry(frame_nav, width=50, justify="center")
    router['input_halaman'].insert(0, "1")
    router['input_halaman'].pack(side=ctk.LEFT, padx=5)

    router['label_total_halaman'] = ctk.CTkLabel(frame_nav, text="dari 0", fg_color="white", bg_color="white", width=30)
    router['label_total_halaman'].pack(side=ctk.LEFT, padx=5)
    router['btn_go'] = ctk.CTkButton(frame_nav, text="Go", command=router['aksi_go'], width=50, text_color="black", state=ctk.DISABLED)
    router['btn_go'].pack(side=ctk.LEFT, padx=5)

    frame_lang = ctk.CTkFrame(header_frame, fg_color="transparent")
    frame_lang.pack(side=ctk.LEFT, padx=20)
    router['cb_from_lang'] = ctk.CTkComboBox(frame_lang, values=[], width=150, state="readonly")
    router['cb_from_lang'].set("English")
    router['cb_from_lang'].pack(side=ctk.LEFT, padx=5)
    ctk.CTkLabel(frame_lang, text="To", text_color="black").pack(side=ctk.LEFT, padx=5)
    router['cb_to_lang'] = ctk.CTkComboBox(frame_lang, values=[], width=150, state="readonly")
    router['cb_to_lang'].set("Indonesian")
    router['cb_to_lang'].pack(side=ctk.LEFT, padx=5)

    btn_exit = ctk.CTkButton(header_frame, text="Exit", command=router['aksi_exit'], fg_color="#dc3545", width=80)
    btn_exit.pack(side=ctk.RIGHT, padx=20)

    # Panel Utama
    main_container = ctk.CTkFrame(root, bg_color="#f5f6fa")
    main_container.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    panel_kiri = ctk.CTkFrame(main_container, bg_color="#7f8c8d")
    panel_kiri.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    router['panel_kiri'] = panel_kiri
    canvas_pdf = ctk.CTkCanvas(panel_kiri, bg="#7f8c8d")
    canvas_pdf.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, pady=10, padx=5)

    scrollbar_pdf = ctk.CTkScrollbar(panel_kiri, orientation=ctk.VERTICAL, command=canvas_pdf.yview)
    scrollbar_pdf.pack(side=ctk.RIGHT, fill=ctk.Y)

    canvas_pdf.configure(yscrollcommand=scrollbar_pdf.set)
    router['canvas_pdf'] = canvas_pdf
    router['output_gambar'] = canvas_pdf.create_image(0, 0, anchor=ctk.NW)

    router['drop_zone'] = ctk.CTkFrame(panel_kiri, bg_color="white", width=350, height=150)
    router['drop_zone'].place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    router['lbl_drop_1'] = ctk.CTkLabel(router['drop_zone'], text="Menyiapkan komponen mesin...", font=("Arial", 16, "bold"), text_color="#2c3e50")
    router['lbl_drop_1'].pack(pady=45)
    router['lbl_drop_2'] = ctk.CTkLabel(router['drop_zone'], text="Mohon jangan tutup aplikasi.", font=("Arial", 9), text_color="#7f8c8d", bg_color="white")
    router['lbl_drop_2'].pack()

    panel_kanan = ctk.CTkFrame(main_container, bg_color="white")
    panel_kanan.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, pady=20, padx=20)
    scrollbar_translate = ctk.CTkScrollbar(panel_kanan, orientation=ctk.VERTICAL)
    scrollbar_translate.pack(side=ctk.RIGHT, fill=ctk.Y)

    ctk.CTkLabel(panel_kanan, text="Hasil Terjemahan", font=("Arial", 14, "bold"), fg_color="#2c3e50", text_color="white").pack(anchor=ctk.W)
    ctk.CTkFrame(panel_kanan, height=1, bg_color="#eee").pack(fill=ctk.X, pady=10)

    router['output_teks'] = ctk.CTkTextbox(
        panel_kanan, font=("Arial", 14),
        fg_color="transparent", text_color="#2c3e50",
        wrap=ctk.WORD, yscrollcommand=scrollbar_translate.set)
    router['output_teks'].insert(ctk.END, "Membuat sistem terjemahan lokal. Mohon tunggu...")
    router['output_teks'].pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    scrollbar_translate.configure(command=router['output_teks'].yview)
