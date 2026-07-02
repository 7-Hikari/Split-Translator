//go:build windows

package winocr

import (
	"bytes"
	"fmt"
	"os/exec"
	"strings"
)

func PanggilWinOCR(base64Gambar string) (string, error) {
	if strings.Contains(base64Gambar, ",") {
		base64Gambar = strings.Split(base64Gambar, ",")[1]
	}

	// Gunakan tanda '-' agar PowerShell membaca skrip dari Stdin
	cmd := exec.Command("powershell", "-NoProfile", "-NonInteractive", "-Command", "-")

	// Masukkan skrip ke dalam buffer stdin
	var stdinBuf bytes.Buffer
	fmt.Fprintf(&stdinBuf, `
	$ErrorActionPreference = 'Stop'
	[void][Window.Media.Ocr.OcrEngine, Windows.Media.Ocr, ContentType = WindowsRuntime]
	[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
	[void][Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]

	$bytes = [System.Convert]::FromBase64String('%s')
	$stream = New-Object System.IO.MemoryStream(,$bytes)
	$randStream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream

	$asyncWrite = $randStream.AsStreamForWrite()
	$stream.CopyTo($asyncWrite)
	$asyncWrite.Flush()
	$randStream.Seek(0)

	$decoderOp = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($randStream)
	while ($decoderOp.Status -eq 'Started') { Start-Sleep -Milliseconds 10 }
	$decoder = $decoderOp.GetResults()

	$bitmapOp = $decoder.GetSoftwareBitmapAsync()
	while ($bitmapOp.Status -eq 'Started') { Start-Sleep -Milliseconds 10 }
	$bitmap = $bitmapOp.GetResults()

	$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
	if ($null -eq $engine) {
		throw "OcrEngine tidak dapat diinisialisasi"
	}

	$ocrOp = $engine.RecognizeAsync($bitmap)
	while ($ocrOp.Status -eq 'Started') { Start-Sleep -Milliseconds 10 }
	$res = $ocrOp.GetResults()

	Write-Output $res.Text
	`, base64Gambar)

	cmd.Stdin = &stdinBuf

	var out bytes.Buffer
	var errOut bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &errOut

	err := cmd.Run()
	if err != nil {
		return "", fmt.Errorf("PowerShell Error: %v | Detail: %s", err, errOut.String())
	}

	return strings.TrimSpace(out.String()), nil
}
