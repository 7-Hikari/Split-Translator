//go:build windows

package winocr

import (
	"encoding/base64"
	"fmt"
	"strings"
	"syscall"
	"unsafe"
)

func PanggilWinOCR(base64Gambar string) (string, error) {
	if strings.Contains(base64Gambar, ",") {
		base64Gambar = strings.Split(base64Gambar, ",")[1]
	}

	imgBytes, err := base64.StdEncoding.DecodeString(base64Gambar)
	if err != nil {
		return "", fmt.Errorf("gagal decode base64: %w", err)
	}

	// Muat secara manual di dalam fungsi agar jika gagal, Go bisa menangkap error-nya
	handle, err := syscall.LoadLibrary("winocr.dll")
	if err != nil {
		return "", fmt.Errorf("DLL winocr.dll tidak ditemukan atau gagal dimuat: %w", err)
	}
	defer syscall.FreeLibrary(handle)

	proc, err := syscall.GetProcAddress(handle, "JalankanOCR")
	if err != nil {
		return "", fmt.Errorf("Fungsi JalankanOCR tidak ditemukan di dalam DLL: %w", err)
	}

	ret, _, _ := syscall.SyscallN(
		proc,
		uintptr(unsafe.Pointer(&imgBytes[0])),
		uintptr(len(imgBytes)),
	)

	if ret == 0 {
		return "", fmt.Errorf("gagal eksekusi fungsi OCR di dalam DLL")
	}

	return syscall.UTF16ToString((*[1 << 20]uint16)(unsafe.Pointer(ret))[:]), nil
}
