# 🎯 Smart Exam Grader - Project Agent Protocol

> **Project**: Smart Exam Grader (Sistem Penilaian Otomatis Lembar Jawaban Kertas ke Excel)  
> **Path**: `d:\porto\smart-exam-grader`

---

## ⚡ 1. Pre-Flight Protocol
1. Sebelum mengubah logika penilaian atau pemrosesan gambar, periksa `docs/architecture.md` untuk skema kontrak data input/output.
2. Selalu uji dengan gambar sampel di `data/sample_inputs/` untuk memverifikasi akurasi deteksi tanda silang dan pembacaan No Peserta.

---

## ⚖️ 2. Adaptive Rigor
- **Level 1 (Perbaikan minor)**: Penyesuaian threshold binerisasi/densitas piksel silang.
- **Level 2 (Fitur modul)**: Penambahan format lembar baru atau modifikasi rumus nilai di `scoring_engine.py`.
- **Level 3 (Arsitektur)**: Penggantian engine OCR atau integrasi Vision-Language Model.

---

## 🔍 3. Root Cause Analysis (RCA) Protocol
Jika deteksi jawaban salah (misal false positive tanda silang, atau salah baca nomor peserta):
1. **Root Cause**: Analisis histogram piksel pada sel terkait atau kegagalan binarisasi adaptive threshold.
2. **Asumsi Kode Lama**: Mengapa threshold sebelumnya menganggap sel tersebut bertanda silang / kosong.
3. **Solusi Permanen**: Kalibrasi kontras lokal atau perbandingan diferensial antar sel dalam 1 baris soal.

---

## 🔄 4. State & Knowledge Sync
- Update `SYSTEM_STATE.md` setiap ada penambahan fitur atau perbaikan akurasi.
