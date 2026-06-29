# Menggunakan image dasar Go berbasis Debian Trixie resmi dari Microsoft
FROM mcr.microsoft.com/devcontainers/go:2-1.26-trixie

# 1. Install semua dependensi Linux (GTK, WebKit, Tesseract, dll) dalam satu lapisan cache
RUN apt-get update && apt-get install -y \
    libgtk-3-dev \
    libgtk-3-0\
    libwebkit2gtk-4.1-dev \
    pkg-config \
    build-essential \
    libtesseract-dev \
    libleptonica-dev \
    tesseract-ocr-lat \
    && rm -rf /var/lib/apt/lists/*

# 2. Akali sistem pkg-config untuk mengelabui kebutuhan WebKit v4.0 milik Wails
RUN cp /usr/lib/x86_64-linux-gnu/pkgconfig/webkit2gtk-4.1.pc /usr/lib/x86_64-linux-gnu/pkgconfig/webkit2gtk-4.0.pc || true \
    && mkdir -p /usr/share/pkgconfig \
    && cp /usr/lib/x86_64-linux-gnu/pkgconfig/webkit2gtk-4.1.pc /usr/share/pkgconfig/webkit2gtk-4.0.pc || true

USER vscode
RUN go install github.com/wailsapp/wails/v2/cmd/wails@latest