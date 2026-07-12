package main

import (
	"context"
	"fmt"
	"os"
	"io"
	"log"
	"os/exec"
	"path/filepath"
	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App struct
type App struct {
	ctx context.Context
	Ctrl *Kontroller
	Srv *Service
	sourceLang string
	destLang string
}

func initLogger() {
	exePath, err := os.Executable()
	if err != nil {
		return
	}
	exeDir := filepath.Dir(exePath)
	logFilePath := filepath.Join(exeDir, "app.log")
	file, err := os.OpenFile(logFilePath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		fallbackPath := filepath.Join(os.TempDir(), "splittranslator_app.log")
		file, _ = os.OpenFile(fallbackPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	}

	if file != nil {
		mw := io.MultiWriter(os.Stdout, file)
		log.SetOutput(mw)
		log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)
	}
}

type LanguagesResponse struct {
	Status bool `json:"status"`
	Languages map[string]string `json:"languages"`
}
func (a *App) Languages() (LanguagesResponse, error){
	bahasa, err := a.Srv.GetSupportedLanguages()
	if err != nil {return LanguagesResponse{Status:false}, err}
	return LanguagesResponse{Status: true, Languages: bahasa}, nil
}

type KesiapanResponse struct{
	Status bool `json:"status"`
}
func (a *App) CekKesiapan() (KesiapanResponse){
	return KesiapanResponse{Status : a.Srv.CekKesiapanPy()}
}

type UploadResponse struct {
	Status bool `json:"status"`
	Message string `json:"message"`
	TotalHalaman int `json:"total_halaman"`
}
func (a *App) UploadPDF() (UploadResponse, error){
	a.Srv.ClearCache()

	filePath, err := runtime.OpenFileDialog(a.ctx, runtime.OpenDialogOptions{
			Title: "Pilih Dokumen PDF 170MB Anda",
			Filters: []runtime.FileFilter{
				{DisplayName: "PDF Documents (*.pdf)", Pattern: "*.pdf"},
			},
		})
	if err != nil {return UploadResponse{Status: false, Message: err.Error()}, nil}
	if filePath == "" {return UploadResponse{Status: false, Message: "Dibatalkan"}, nil}


	totalHal, err := a.Ctrl.PdfUpload(filePath)

	if err != nil {return UploadResponse{Status: false, Message: err.Error()}, nil}

	return UploadResponse{Status:true,
		Message: "File yang diproses " + filePath,
		TotalHalaman:totalHal}, nil
}

type GambarResponse struct{
	Status bool `json:"status"`
	Gambar string `json:"gambar_base64"`
}
func (a *App) AmbilHalaman(angkaHalaman int) (GambarResponse, error){
	strGambar, err := a.Ctrl.AmbilGambar(angkaHalaman)
	if err != nil {return GambarResponse{Status: false}, err}

	return GambarResponse{Status: true, Gambar: strGambar}, nil
}

type TerjemahanResponse struct {
	Status bool `json:"status"`
	Terjemahan string `json:"terjemahan"`
	IsLokal bool `json:"isLokal"`
	Message string `json:"message,omitempty"`
}
func (a *App) Terjemahkan(nomorHalaman int, src string, dst string, GoogleTr bool) (TerjemahanResponse, error){
	if src == dst {return TerjemahanResponse{Status: false, Message: "apasih"}, nil}

	//switchLang
	a.AreSwitch(src, dst)

	hasil, err := a.Srv.LogikaProsesHalaman(nomorHalaman, a.Ctrl, src, dst, GoogleTr)
	if err != nil{return TerjemahanResponse{Status:false, Message: err.Error()}, nil}

	return TerjemahanResponse{Status: true, Terjemahan: hasil, IsLokal: a.Ctrl.IsLokal(src, dst, GoogleTr)}, nil
}

func(a *App) AreSwitch(src string, dst string){
	if a.sourceLang != src || a.destLang != dst {
		a.sourceLang = src
		a.destLang = dst
		a.Srv.ClearCache()
	}
}

func (a *App) ResetDokumen() (map[string]bool, error){
	a.Ctrl.HapusCache()
	a.Srv.ClearCache()
	return map[string]bool{"status":true}, nil
}

// NewApp creates a new App application struct
func NewApp() *App {
	return &App{Ctrl: NewKontroller(), Srv: NewService()}
}

// startup is called when the app starts. The context is saved
// so we can call the runtime methods
var pythonCmd *exec.Cmd

func (a *App) startup(ctx context.Context) {
	a.ctx = ctx

	exePath, err := os.Executable()
	if err !=nil{log.Printf("Gagal mendapatkan path executable: %v\n", err)
		return
	}
	baseDir := filepath.Dir(exePath)
	prodPythonPath := filepath.Join(baseDir, "lib", "services.exe")

	if _, statErr := os.Stat(prodPythonPath); statErr == nil {
		pythonCmd = exec.Command(prodPythonPath)
		log.Println("prod")
		log.Println(prodPythonPath)
	} else {
		devPythonPath := filepath.Join(baseDir,"..","..", "service", "api.py")
		PyVenv := filepath.Join(devPythonPath, "..", "venv", "Scripts", "python.exe")
		pythonCmd = exec.Command(PyVenv, devPythonPath)
		log.Println("dev")
		log.Println(devPythonPath)
	}

	pythonCmd.Stderr = log.Writer()
	pythonCmd.Stdout = log.Writer()

	er := pythonCmd.Start()
	if er != nil {
		log.Printf("PERINGATAN: Gagal menjalankan Python Backend: %v\n", er)
	} else {
		log.Println("Python Backend berhasil dijalankan!")
	}

}

func (a *App) shutdown(ctx context.Context) {
	// Pastikan Python dimatikan saat aplikasi Go ditutup
	if pythonCmd != nil && pythonCmd.Process != nil {
		log.Println("Mematikan Python Backend...")
		
		// Matikan proses secara paksa
		err := pythonCmd.Process.Kill()
		if err != nil {
			log.Printf("Gagal mematikan Python: %v\n", err)
		}
	}
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}
