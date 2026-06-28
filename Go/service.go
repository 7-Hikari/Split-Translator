package main

import (
	"encoding/base64"
	"fmt"
	_ "image/png"
	"strings"
	"sync"

	"github.com/otiai10/gosseract/v2"
)

type Service struct{
	cache map[int]string
	cacheMutex sync.RWMutex
}

func NewService() *Service{
	return &Service{cache: make(map[int]string)}
}

func (s *Service) LogikaProsesHalaman(
	nomorHal int, ctrl *Kontroller, src string, dst string,
	GoogleTr bool) (string, error){

		s.cacheMutex.RLock()
		if hasilCache, ada := s.cache[nomorHal]; ada {
			s.cacheMutex.RUnlock()
			return hasilCache, nil
		}
		s.cacheMutex.RUnlock()

		if ctrl.docAktif == nil{return "", fmt.Errorf("Tidak ada dokumen aktif")}

		page, err := ctrl.docAktif.Text(nomorHal - 1)
		if err != nil{return "", fmt.Errorf("Gagal mengekstrak teks: %w", err)}

		text := strings.TrimSpace(page)

		if text == ""{
			base64G, err := ctrl.AmbilGambar(nomorHal)

			if err != nil{return "", fmt.Errorf("gagal mengambil gambar halaman: %w", err)}

			text, err = s.jalankanTesseractOCR(base64G)
			if err != nil{return "", fmt.Errorf("gagal memproses OCR: %w", err)}
			if strings.TrimSpace(text) == ""{
				return "(Tidak ada teks terdeteksi di sini)", nil
			}
		}

		text = strings.ReplaceAll(text, "-\n", "")

		var textTerjemahan string
		if ctrl.IsLokal(src, dst, GoogleTr){
			textTerjemahan = text
		}else{
			if len(text) > 4500 {
				text = text[:4500]
			}
			var errTranslate error
			textTerjemahan, errTranslate = s.translateViaGoogle(text, src, dst)
			if errTranslate != nil{
				return "", fmt.Errorf("Gagal translasi: %w", errTranslate)
			}
		}

		s.cacheMutex.Lock()
		s.cache[nomorHal] = textTerjemahan
		s.cacheMutex.Unlock()

		return textTerjemahan, nil
	}

	func (s *Service) jalankanTesseractOCR(base64Gambar string) (string, error){
		if strings.Contains(base64Gambar, ","){base64Gambar=strings.Split(base64Gambar, ",")[1]}

		imgBytes, err := base64.StdEncoding.DecodeString(base64Gambar)
		if err != nil{return "", fmt.Errorf("gagal decode base64: %w", err)}

		client := gosseract.NewClient()
		defer client.Close()

		client.SetLanguage("Latin")
		err= client.SetImageFromBytes(imgBytes)
		if err != nil{return "", fmt.Errorf("tesseract gagal menerima byte gambar: %w", err)}

		return client.Text()
	}

	func (s *Service) translateViaGoogle(text string, src string, dst string) (string, error){
		return text,nil
	}

	func (s *Service) ClearCache(){
		s.cacheMutex.Lock()
		s.cache = make(map[int]string)
		s.cacheMutex.Unlock()
	}
