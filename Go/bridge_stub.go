//go:build !windows

package main

import "fmt"

func panggilOcrSecaraDinamis(base64Gambar string) (string, error) {
	return "", fmt.Errorf("tidak didukung di OS ini")
}
