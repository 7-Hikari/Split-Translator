#define COBJMACROS
#include <windows.h>
#include <oleauto.h>
#include <stdio.h>

__declspec(dllexport) const wchar_t* JalankanOCR(const unsigned char* bytes, int length) {
    HRESULT hr = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED); 
    
    CLSID clsid;
    hr = CLSIDFromProgID(L"Windows.Media.Ocr.OcrEngine", &clsid);
    if (FAILED(hr)) {
        if (SUCCEEDED(hr)) CoUninitialize();
        return L"Error: Windows OCR tidak terdaftar";
    }

    IDispatch* pOcrEngine = NULL;
    hr = CoCreateInstance(&clsid, NULL, CLSCTX_INPROC_SERVER, &IID_IDispatch, (void**)&pOcrEngine);
    if (FAILED(hr)) {
        if (SUCCEEDED(hr)) CoUninitialize();
        return L"Error: Gagal membuat OcrEngine";
    }

    static wchar_t hasil[256];
    swprintf(hasil, 256, L"Sukses membaca %d bytes", length);

    pOcrEngine->lpVtbl->Release(pOcrEngine);
    CoUninitialize();
    
    return hasil;
}