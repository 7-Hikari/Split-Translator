package main

import(
	"bytes"
	"encoding/base64"
	"fmt"
	"image/png"
	"github.com/gen2brain/go-fitz"
)

type Kontroller struct{
	docAktif *fitz.Document
}

func NewKontroller() *Kontroller{
	return &Kontroller{}
}

func (k *Kontroller) PdfUpload(pdfBytes []byte) (int, error){
	doc, err :=fitz.NewFromReader(bytes.NewReader(pdfBytes))
	if err != nil{return 0, fmt.Errorf("PDF upload : %w", err)}

	k.docAktif = doc
	return doc.NumPage(), nil
}

func (k *Kontroller) AmbilGambar(nomorHalaman int)(string, error){
	if k.docAktif == nil{return "", fmt.Errorf("tidak ada dokumen aktif")}

	img, err := k.docAktif.Image(nomorHalaman - 1)
	if err != nil{return "", fmt.Errorf("gambar halaman %d : %w", nomorHalaman, err)}

	var buf bytes.Buffer
	err = png.Encode(&buf, img)
	if err !=nil{return "", fmt.Errorf("gagal encode %d ke png: %w", nomorHalaman, err)}

	encodedImg := base64.StdEncoding.EncodeToString(buf.Bytes())
	return fmt.Sprintf("data:image/png;base64,%s", encodedImg),nil
}

func (k *Kontroller) HapusCache(){
	if k.docAktif != nil{
		k.docAktif.Close()
		k.docAktif = nil
	}
}

func (K *Kontroller) IsLokal(src string, dst string, isGoogle bool) (bool){
	if src == "en" && dst == "id" && !isGoogle {return true} else {return false}
}
