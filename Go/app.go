package main

import (
	"context"
	"fmt"
	"strings"
	"encoding/base64"
)

// App struct
type App struct {
	ctx context.Context
	Ctrl *Kontroller
	Srv *Service
	sourceLang string
	destLang string
}

type LanguagesResponse struct {
	Status bool `json:"status"`
	Languages map[string]string `json:"languages"`
}
func (a *App) Languages() (LanguagesResponse, error){
	bahasa := map[string]string{
		"English": "en",
		"Indonesian": "id",
	}
	return LanguagesResponse{Status: true, Languages: bahasa}, nil
}

type UploadResponse struct {
	Status bool `json:"status"`
	Message string `json:"message"`
	TotalHalaman int `json:"total_halaman"`
}
func (a *App) UploadPDF(fileName string, base64Str string) (UploadResponse, error){
	a.Srv.ClearCache()

	if !strings.HasSuffix(strings.ToLower(fileName), ".pdf"){
		return UploadResponse{Status: false, Message: "Format harus PDF"}, nil
	}
	if strings.Contains(base64Str, ","){
		base64Str = strings.Split(base64Str, ",")[1]
	}
	pdfBytes, err := base64.StdEncoding.DecodeString(base64Str)
	if err != nil {return UploadResponse{Status: false, Message: fmt.Sprintf("Gagal decode Base64: %v", err)}, nil}
	if len(pdfBytes) == 0 {return UploadResponse{Status: false, Message: "Data PDF kosong (0 bytes)"}, nil}

	totalHal, err := a.Ctrl.PdfUpload(pdfBytes)

	if err != nil {return UploadResponse{Status: false, Message: err.Error()}, nil}

	return UploadResponse{Status:true,
		Message: "File yang diproses " + fileName,
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
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// Greet returns a greeting for the given name
func (a *App) Greet(name string) string {
	return fmt.Sprintf("Hello %s, It's show time!", name)
}
