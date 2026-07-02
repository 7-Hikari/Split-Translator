package main

import (
	"encoding/json"
	"fmt"
	_ "image/png"
	"io"
	"net/http"
	"net/url"
	"runtime"
	"strings"
	"sync"
)

type Service struct {
	cache      map[int]string
	cacheMutex sync.RWMutex
}

func NewService() *Service {
	return &Service{cache: make(map[int]string)}
}

func (s *Service) LogikaProsesHalaman(
	nomorHal int, ctrl *Kontroller, src string, dst string,
	GoogleTr bool) (string, error) {

	s.cacheMutex.RLock()
	if hasilCache, ada := s.cache[nomorHal]; ada {
		s.cacheMutex.RUnlock()
		return hasilCache, nil
	}
	s.cacheMutex.RUnlock()

	if ctrl.docAktif == nil {
		return "", fmt.Errorf("Tidak ada dokumen aktif")
	}

	page, err := ctrl.docAktif.Text(nomorHal - 1)
	if err != nil {
		return "", fmt.Errorf("Gagal mengekstrak teks: %w", err)
	}

	text := strings.TrimSpace(page)

	if text == "" {
		base64G, err := ctrl.AmbilGambar(nomorHal)

		if err != nil {
			return "", fmt.Errorf("gagal mengambil gambar halaman: %w", err)
		}

		text, err = s.jalankanWindowsOCR(base64G)
		if err != nil {
			return "", fmt.Errorf("gagal memproses OCR: %w", err)
		}
		if strings.TrimSpace(text) == "" {
			return "(Tidak ada teks terdeteksi di sini)", nil
		}
	}

	text = strings.ReplaceAll(text, "-\n", "")

	var textTerjemahan string
	if ctrl.IsLokal(src, dst, GoogleTr) {
		textTerjemahan = text
	} else {
		if len(text) > 4500 {
			text = text[:4500]
		}
		var errTranslate error
		textTerjemahan, errTranslate = s.translateViaGoogle(text, src, dst)
		if errTranslate != nil {
			return "", fmt.Errorf("Gagal translasi: %w", errTranslate)
		}
	}

	s.cacheMutex.Lock()
	s.cache[nomorHal] = textTerjemahan
	s.cacheMutex.Unlock()

	return textTerjemahan, nil
}

func (s *Service) jalankanWindowsOCR(base64Gambar string) (string, error) {
	if runtime.GOOS == "windows" {
		// Kita panggil fungsi dari sub-folder lewat fungsi pembantu internal Go
		return panggilOcrSecaraDinamis(base64Gambar)
	}
	return "", fmt.Errorf("Windows OCR hanya dapat berjalan di sistem operasi Windows")
}

func (s *Service) translateViaGoogle(text string, src string, dst string) (string, error) {
	apiURL := fmt.Sprintf("https://translate.googleapis.com/translate_a/single?client=gtx&sl=%s&tl=%s&dt=t&q=%s",
		src, dst, url.QueryEscape(text))

	resp, err := http.Get(apiURL)
	if err != nil {
		return text, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return text, err
	}

	var raw []interface{}
	if err := json.Unmarshal(body, &raw); err != nil {
		return text, err
	}

	if len(raw) > 0 && raw[0] != nil {
		var result strings.Builder
		for _, item := range raw[0].([]interface{}) {
			if item != nil {
				translatedLine := item.([]interface{})[0].(string)
				result.WriteString(translatedLine)
			}
		}
		return result.String(), nil
	}

	return text, fmt.Errorf("gagal memparsing data translasi")
}

func (s *Service) ClearCache() {
	s.cacheMutex.Lock()
	s.cache = make(map[int]string)
	s.cacheMutex.Unlock()
}

type AvailableLanguages struct{
	Lang map[string]string `json:"sl"`
}
func (s *Service) GetSupportedLanguages() (map[string]string, error){
	resp, err := http.Get("https://translate.google.com/translate_a/l?client=gtx")
	if err != nil{return nil, err}
	defer resp.Body.Close()

	var data AvailableLanguages
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {return nil, err}

	var langCodes map[string]string = make(map[string]string)
	for code, name := range data.Lang{
		langCodes[code] = name
	}
	return langCodes, nil
}
