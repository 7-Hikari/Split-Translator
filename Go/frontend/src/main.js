const panelPdf = document.getElementById("panel-pdf");
const pageIndicator = document.getElementById("page-indicator");
const outputTeks = document.getElementById("output-teks");
const sourceLang = document.getElementById("from-language");
const destLang = document.getElementById("to-language");

let GoogleTr = false;
window.GoogleTr = GoogleTr;
let src = "en";
let dst = "id";
let halamanSekarang = 1;
let isJumpingPage = false;
let totalHalamanGlobal = 0;
let siap = false;

let library = null;

document.addEventListener("DOMContentLoaded", async () => {
    window.go.main.App.Languages().then((data) => {
      library = data.languages;
      console.log("data : "+data.languages)
        if (library) {
            sourceLang.innerHTML = destLang.innerHTML = "";
            Object.entries(library).forEach(([value, key]) => {
                sourceLang.innerHTML += `<option value="${value}">${key}</option>`;
                destLang.innerHTML += `<option value="${value}">${key}</option>`;
            });
        }
        sourceLang.value = src;
        destLang.value = dst;
    });

    await window.go.main.App.CekKesiapan().then((data)=>{
        if(data.status){
            kembalikanInput(true);
        }else{
            kembalikanInput(false);
        }
    })
});

sourceLang.addEventListener("change", (e) => {
    src = e.target.value;
    if (src === dst) return;
    ambilTerjemahan(halamanSekarang);
});
destLang.addEventListener("change", (e) => {
    dst = e.target.value;
    if (src === dst) return;
    ambilTerjemahan(halamanSekarang);
});

const observerGambar = new IntersectionObserver(
    (entries, observer) => {
        entries.forEach((entry) => {
            // Jika elemen halaman sudah mendekati atau masuk layar (viewport)
            if (entry.isIntersecting) {
                const elemenHalaman = entry.target;
                const nomorHalaman = elemenHalaman.getAttribute("data-page");

                // Periksa apakah halaman ini sudah pernah dimuat gambarnya atau belum
                if (!elemenHalaman.querySelector("img")) {
                    elemenHalaman.innerHTML = `<p style="padding: 20px; color:#7f8c8d;">Memuat gambar halaman ${nomorHalaman}...</p>`;
                    muatGambarHalaman(nomorHalaman, elemenHalaman);
                }

                // Setelah gambar dimuat, kita bisa lepas pengawasan untuk halaman ini agar hemat performa
                observer.unobserve(elemenHalaman);
            }
        });
    },
    {
        root: document.getElementById("panel-pdf"), // Di dalam panel scroll PDF Anda
        rootMargin: "200px 0px", // Muat gambar 200px sebelum halamannya benar-benar terlihat di layar (agar tidak kaget)
    },
);

function kembalikanInput(param = true){
    if (param){
	siap = true;
        document.getElementById("drop-zone-text-1").innerText =
            "File PDF di Sini";
        document.getElementById("drop-zone-text-2").innerText =
            "klik untuk memilih file";
    }else{
	siap = false;
        document.getElementById("drop-zone-text-1").innerText =
            "Gagal";
        document.getElementById("drop-zone-text-2").innerText =
            "Mesin ocr gagal dimuat";
    }
}

function resetApp() {
    const fileInput = document.getElementById("file-input");
    if (fileInput) {
        fileInput.value = ""; // Sekarang ini berfungsi karena elemennya tidak pernah hilang
    }

    // Kembalikan teks asli drop zone
    kembalikanInput(true);

    dropZone.style.display = "flex";
    pdfContainer.style.display = "none";
    pdfContainer.innerHTML = "";
    pageIndicator.innerText = "1";
    outputTeks.innerText = "Unggah dokumen PDF untuk memulai.";
    halamanSekarang = 1;
    currentPDF = null;

    window.go.main.App.ResetDokumen().catch((err) => console.error(err));
}

document.getElementById("reset").addEventListener("click", () => {
    resetApp();
})

// Deteksi halaman mana yang sedang dilihat user berdasarkan posisi scroll
panelPdf.addEventListener("scroll", () => {
    if (
        pdfContainer.style.display === "none" ||
        pdfContainer.innerHTML === ""
    ) {
        return;
    }

    if (isJumpingPage) return;

    const pages = document.querySelectorAll(".pdf-page-mock");
    let pageInView = 1;

    pages.forEach((page) => {
        const rect = page.getBoundingClientRect();
        // Jika bagian atas halaman sudah melewati setengah layar komputer
        if (rect.top < window.innerHeight / 2) {
            pageInView = page.getAttribute("data-page");
        }
    });

    // Jika halaman berubah, panggil fungsi untuk ambil data dari Flask
    if (pageInView !== halamanSekarang) {
        halamanSekarang = pageInView;
        document.getElementById("page-indicator").innerText = halamanSekarang;
        ambilTerjemahan(halamanSekarang);
    }
});

async function ambilTerjemahan(nomorHalaman) {
    if (src === dst) return;
    const outputTeks = document.getElementById("output-teks");
    outputTeks.innerHTML = "<em>Menerjemahkan halaman... Mohon tunggu...</em>";

    try {
        const data = await window.go.main.App.Terjemahkan(
            parseInt(nomorHalaman),
            src,
            dst,
            window.GoogleTr,
        );

        if (data && data.status === true) {
            outputTeks.innerHTML = data.terjemahan;
        } else {
            outputTeks.innerHTML = `<span style="color:red;">Gagal: ${data.message || "Terjadi kesalahan sistem."}</span>`;
        }
    } catch (error) {
        outputTeks.innerHTML =
            "<span style='color:red;'>Gagal menghubungkan ke server lokal.</span>";
        console.error("Error pada fungsi Terjemahkan:", error);
    }
}

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const pdfContainer = document.getElementById("pdf-pages-container");

// 1. Klik area drop-zone untuk buka file manager komputer
dropZone.addEventListener("click", async () => {
    if (siap === false) {return;}
    try {
        // Panggil fungsi di Go untuk memilih file dan memprosesnya langsung via path
        const data = await window.go.main.App.UploadPDF();

        if (data && data.status === true) {
            dropZone.style.display = "none";
            pdfContainer.style.display = "block";
            pdfContainer.innerHTML = "";

            totalHalamanGlobal = data.total_halaman;
            const totalPageIndicator = document.getElementById("total-halaman");
            if (totalPageIndicator) totalPageIndicator.innerText = totalHalamanGlobal;

            for (let i = 1; i <= totalHalamanGlobal; i++) {
                const pageElement = document.createElement("div");
                pageElement.className = "pdf-page-mock";
                pageElement.setAttribute("data-page", i);
                pageElement.innerHTML = `<p id="loading-page-${i}" style="padding: 20px; color:#7f8c8d;">Memuat gambar halaman ${i}...</p>`;
                pdfContainer.appendChild(pageElement);

                observerGambar.observe(pageElement);
            }
            ambilTerjemahan(1);
        } else if (data && data.message !== "Dibatalkan") {
            alert("Gagal memproses PDF: " + data.message);
        }
    } catch (error) {
        console.error(error);
        alert("Terjadi kesalahan saat memproses dokumen.");
    }
});

// 2. Efek visual saat file diseret di atas drop-zone
dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.backgroundColor = "#ebf5fb";
});

dropZone.addEventListener("dragleave", () => {
    dropZone.style.backgroundColor = "#ffffff";
});


async function muatGambarHalaman(nomorHalaman, elemenInduk) {
    try {
        const data = await window.go.main.App.AmbilHalaman(parseInt(nomorHalaman));
        if (data && data.status === true) {
            // Pastikan data.gambar_base64 sudah menyertakan "data:image/png;base64," dari sisi Go nantinya
            elemenInduk.innerHTML = `<img src="${data.gambar_base64}" style="width: 100%; height: auto; display: block;">`;
        } else {
            elemenInduk.innerHTML = `<p style="color: red; padding: 20px;">Gagal memuat halaman ini</p>`;
        }
    } catch (error) {
        console.error(error);
    }
}

function lompatKeHalaman(targetPage) {
    const inputHalaman = document.getElementById("input-halaman");
    const targetElement = document.querySelector(
        `.pdf-page-mock[data-page="${targetPage}"]`,
    );

    if (!targetElement) return;

    // Kunci event listener scroll agar tidak men-trigger ambilTerjemahan ganda
    isJumpingPage = true;
    halamanSekarang = targetPage;
    pageIndicator.innerText = halamanSekarang;
    if (inputHalaman) inputHalaman.value = halamanSekarang;

    // Scroll halaman PDF ke viewport target secara halus (smooth)
    targetElement.scrollIntoView({ behavior: "smooth", block: "start" });

    // Panggil data terjemahan untuk halaman tujuan
    ambilTerjemahan(targetPage).finally(() => {
        // Beri jeda sedikit pasca-scroll selesai sebelum mengaktifkan deteksi scroll kembali
        setTimeout(() => {
            isJumpingPage = false;
        }, 500);
    });
}

const btnGo = document.getElementById("btn-go");
if (btnGo) {
    btnGo.addEventListener("click", () => {
        const inputHalaman = document.getElementById("input-halaman");
        const nilaiInput = parseInt(inputHalaman.value);

        if (nilaiInput >= 1 && nilaiInput <= totalHalamanGlobal) {
            lompatKeHalaman(nilaiInput);
        } else {
            alert(
                `Halaman tidak valid! Masukkan angka antara 1 sampai ${totalHalamanGlobal}`,
            );
            inputHalaman.value = halamanSekarang;
        }
    });
}

const inputHalamanElem = document.getElementById("input-halaman");
if (inputHalamanElem) {
    inputHalamanElem.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            if (btnGo) btnGo.click();
        }
    });
}
