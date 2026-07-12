package main

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"log"
	"fmt"
	_ "image/png"
	"time"
	"io"
	"net/http"
	"net/url"
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

type PythonResponse struct {
	Status     bool   `json:"status"`
	Terjemahan string `json:"terjemahan"`
	Message    string `json:"message"`
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
		log.Printf("Tidak ada dokumen aktif")
		return "", fmt.Errorf("Tidak ada dokumen aktif")
	}

	page, err := ctrl.docAktif.Text(nomorHal - 1)
	if err != nil {
		log.Printf("Gagal mengekstrak teks: %w", err)
		return "", fmt.Errorf("Gagal mengekstrak teks: %w", err)
	}

	lokal := ctrl.IsLokal(src, dst, GoogleTr)
	text := strings.TrimSpace(page)

	if text == "" {
		base64G, err := ctrl.AmbilGambar(nomorHal)

		if err != nil {
			log.Printf("gagal mengambil gambar halaman: %w", err)
			return "", fmt.Errorf("gagal mengambil gambar halaman: %w", err)
		}

		text, err = s.jalankanWindowsOCR(base64G, lokal)
		if err != nil {
			log.Printf("gagal memproses OCR: %w", err)
			return "", fmt.Errorf("gagal memproses OCR: %w", err)
		}
		if strings.TrimSpace(text) == "" {
			return "(Tidak ada teks terdeteksi di sini)", nil
		}
	}

	text = strings.ReplaceAll(text, "-\n", "")

	var textTerjemahan string
	if lokal {
		textTerjemahan = text
	} else {
		if len(text) > 4500 {
			text = text[:4500]
		}
		var errTranslate error
		textTerjemahan, errTranslate = s.translateViaGoogle(text, src, dst)
		if errTranslate != nil {
			log.Printf("Gagal translasi: %w", errTranslate)
			return "", fmt.Errorf("Gagal translasi: %w", errTranslate)
		}
	}

	s.cacheMutex.Lock()
	s.cache[nomorHal] = textTerjemahan
	s.cacheMutex.Unlock()

	return textTerjemahan, nil
}

func (s *Service) CekKesiapanPy() (bool){
	maxPercobaan := 10
	jeda := 2 * time.Second

for i := 0; i < maxPercobaan; i++ {
		resp, err := http.Get("http://127.0.0.1:5000/cek")
		if err == nil {
			if resp.StatusCode == http.StatusOK {
				resp.Body.Close()
				return true
			}
			resp.Body.Close()
		}
		time.Sleep(jeda)
	}
	return false
}

func (s *Service) jalankanWindowsOCR(base64Gambar string, lokal bool) (string, error) {
	stringData := base64Gambar
	if strings.Contains(stringData, ","){stringData = strings.Split(stringData, ",")[1]}

	binerGambar, err := base64.StdEncoding.DecodeString(stringData)
	if err != nil {
		log.Printf("gagal decode base64 gambar: %w", err)
		return "", fmt.Errorf("gagal decode base64 gambar: %w", err)}

	urlPython := fmt.Sprintf("http://127.0.0.1:5000/services?lokal=%t", lokal)

	resp, err := http.Post(urlPython, "application/octet-stream", bytes.NewReader(binerGambar))
	if err != nil{
		log.Printf("gagal terhubung ke python service: %w", err)
		return "", fmt.Errorf("gagal terhubung ke python service: %w", err)}

	defer resp.Body.Close()
	
	var pyResp PythonResponse
	if err := json.NewDecoder(resp.Body).Decode(&pyResp); err != nil {return "", fmt.Errorf("gagal membaca json python: %w", err)}
	if !pyResp.Status {
		log.Printf("error dari python: %s", pyResp.Message)
		return "", fmt.Errorf("error dari python: %s", pyResp.Message)}

	return pyResp.Terjemahan, nil
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

	log.Printf("gagal memparsing data translasi")
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
