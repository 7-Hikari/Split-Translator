//go:build windows

package main

import "Go/internal/winocr" // Sesuaikan dengan nama module go.mod Anda

func panggilOcrSecaraDinamis(base64Gambar string) (string, error) {
	return winocr.PanggilWinOCR(base64Gambar)
}
