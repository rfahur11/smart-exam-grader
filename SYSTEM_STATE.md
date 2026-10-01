# 📋 SYSTEM STATE: Smart Exam Grader

> **Proyek**: Sistem Penilaian Otomatis Lembar Jawaban Kertas Ujian ke Excel  
> **Status**: Production-Ready / Complete  
> **Repository**: [github.com/rfahur11/smart-exam-grader](https://github.com/rfahur11/smart-exam-grader)  
> **Terakhir Diperbarui**: 2026-10-01  

---

## 🛠️ Tech Stack Aktif
- **Runtime**: Python 3.11.9
- **Computer Vision**: OpenCV (`cv2`) 5.0.0, NumPy 2.4.6, Pillow 12.3.0
- **Document & Spreadsheet**: OpenPyXL 3.1.5, Pandas 2.3.3
- **OCR / Recognition**: Classical Grid Line Filtering + Ink Density Analyzer, Regex & Fuzzy Matching

---

## 📌 Checklist Fitur & Modul

### Phase 1: Core Engine & Data Model
- [x] Scaffolding Layer 1 (`SYSTEM_STATE.md`, `architecture.md`, `AGENTS.md`, `.gitignore`, `.env.example`)
- [x] Setup direktori data (`sample_inputs`, `templates`, `outputs`)
- [x] Implementasi Preprocessor (`src/preprocessor.py`): Normalisasi gambar, rotasi, deteksi border kertas
- [x] Implementasi Identity Reader (`src/identity_reader.py`): Ekstraksi No Peserta & Nama dari kotak identitas (RapidOCR + Fuzzy Match)
- [x] Implementasi OMR Grid Engine (`src/omr_grid_engine.py`): Ekstraksi sel A-E tabel PG (1-25) & PG Kompleks (1-5), deteksi densitas tinta & multi-mark
- [x] Implementasi Scoring Engine (`src/scoring_engine.py`): Kalkulasi skor PG & PGK berdasarkan kunci jawaban
- [x] Implementasi Excel Exporter (`src/excel_exporter.py`): Injeksi nilai ke baris siswa yang cocok di Excel dengan status dan highlight warna
- [x] Implementasi Visual Annotator (`src/annotator.py`): Audit trail visual lembar koreksi

### Phase 2: Testing & Verification
- [x] Uji coba end-to-end pada sampel lembar jawaban riil (`ASTS Gasal MA Salafiyah Bantarsari`)
- [x] Verifikasi file Excel output (`data/outputs/daftar_nilai_terkoreksi.xlsx`)
- [x] Verifikasi audit annotated image (`data/outputs/annotated_sample_lembar_jawab.jpg`)
- [x] Penanganan edge-case jawaban ganda (Nomor 3 terdeteksi ambigu D & B)

### Phase 3: AnBuso VBA Integration
- [x] Backup file master AnBuso di Downloads
- [x] Implementasi AnBuso Adapter (`src/anbuso_adapter.py`): Pemetaan Input02, Data01 (Objektif), Data03 (Isian)
- [x] Toleransi framing smartphone camera pada preprocessor (`src/preprocessor.py`)
- [x] Deteksi nomor tidak dijawab (unanswered check threshold < 0.16)
- [x] Eksekusi injeksi jawaban siswa `ACHMAD FADILATUL KHANAN` ke file Excel AnBuso
- [x] Pembuatan bukti audit visual `data/outputs/annotated_fadilatul.jpg`
- [x] Preservasi 100% tombol menu dan shapes AnBuso via `pywin32` Excel COM

### Phase 4: Interactive Web UI (Streamlit)
- [x] Dashboard antarmuka guru (`app.py`)
- [x] Drag-and-drop uploader foto lembar ujian (single & batch)
- [x] Tampilan split-screen (Foto asli & audit visual vs Tabel hasil ekstrak)
- [x] Fitur Human-in-the-Loop: Review alert coretan ganda & dropdown koreksi nama siswa
- [x] Tombol 1-klik simpan ke Excel AnBuso dengan menu utuh

### Phase 5: Version Control & Executive Showcase
- [x] Inisialisasi Git local repo branch `main` & initial commit (`9f2dd86`)
- [x] Konfigurasi remote origin `git@github.com:rfahur11/smart-exam-grader.git`
- [x] Executive README kelas dunia (`README.md`) dengan diagram arsitektur Mermaid & ROI
- [x] Social Media Showcase Pack (`docs/SHOWCASE_PACK.md`): LinkedIn PAS post, Twitter thread 5-tweet, Video demo script 25s
- [x] LinkedIn Carousel 7-Slide HD 1080x1350 (`docs/carousel.html`) berstandar Personal Branding Fahrur Rozi K

---

## 🚀 Local Runbook
```bash
# 1. Jalankan Web UI Interaktif untuk Guru (atau double click Jalankan_Smart_Grader.bat)
streamlit run app.py

# 2. Atau jalankan via CLI langsung
python run_anbuso_grader.py

# 3. Buka Slide Carousel di Browser untuk Export ke PDF
start docs/carousel.html
```
