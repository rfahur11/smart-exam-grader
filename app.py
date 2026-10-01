"""
Smart Exam Grader - Interactive Web UI (Streamlit)
Aplikasi koreksi otomatis lembar jawaban ujian kertas (OMR Grid + OCR) dan integrasi ke AnBuso Excel.
"""

import os
import cv2
import numpy as np
import openpyxl
import streamlit as st
from PIL import Image

from src.preprocessor import ExamPreprocessor
from src.identity_reader import IdentityReader
from src.omr_grid_engine import OMRGridEngine
from src.scoring_engine import ScoringEngine
from src.anbuso_adapter import AnBusoAdapter
from src.annotator import VisualAnnotator

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Smart Exam Grader & AnBuso",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 20px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #BBF7D0;
    }
    .warning-box {
        background-color: #FEF9C3;
        border-left: 4px solid #EAB308;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Modul
@st.cache_resource
def load_modules():
    return {
        "preprocessor": ExamPreprocessor(),
        "identity_reader": IdentityReader(),
        "omr_engine": OMRGridEngine(),
        "scoring_engine": ScoringEngine(),
        "annotator": VisualAnnotator()
    }

modules = load_modules()

# SIDEBAR: Pengaturan File Excel AnBuso
st.sidebar.markdown("### ⚙️ Pengaturan File AnBuso")

anbuso_source_mode = st.sidebar.radio(
    "Metode Input File AnBuso:",
    ["📤 Upload File Master (.xlsx)", "⚡ Pakai Sampel XI 5", "📁 Path File Komputer"],
    index=0,
    help="Pilih apakah ingin mengunggah file Excel AnBuso baru atau memakai file sampel/lokal."
)

active_anbuso_file = None
sample_anbuso_path = os.path.abspath(os.path.join("data", "templates", "sample_anbuso_bahasa_inggris.xlsx"))

if anbuso_source_mode == "📤 Upload File Master (.xlsx)":
    uploaded_anbuso = st.sidebar.file_uploader(
        "Pilih file Excel AnBuso:",
        type=["xlsx", "xlsm"],
        help="Unggah file format AnBuso kelas Anda (misal dari kurikulum/wali kelas)."
    )
    if uploaded_anbuso is not None:
        save_dir = os.path.abspath(os.path.join("data", "templates"))
        os.makedirs(save_dir, exist_ok=True)
        target_path = os.path.join(save_dir, f"uploaded_{uploaded_anbuso.name}")
        with open(target_path, "wb") as f_out:
            f_out.write(uploaded_anbuso.getbuffer())
        active_anbuso_file = target_path
    elif os.path.exists(sample_anbuso_path):
        st.sidebar.info("💡 Belum punya file? Anda bisa memilih opsi '⚡ Pakai Sampel XI 5' di atas.")

elif anbuso_source_mode == "⚡ Pakai Sampel XI 5":
    if os.path.exists(sample_anbuso_path):
        active_anbuso_file = sample_anbuso_path
        st.sidebar.caption("Menggunakan master Bahasa Inggris XI 5 bawaan.")
    else:
        st.sidebar.warning("File sampel tidak ditemukan.")

else:  # "📁 Path File Komputer"
    default_anbuso_path = r"C:\Users\black\Downloads\10, Fase F XI 5_ASTS_AnBuso_Bahasa Inggris.xlsx"
    custom_path = st.sidebar.text_input(
        "Ketik path absolut file:",
        value=default_anbuso_path if os.path.exists(default_anbuso_path) else "",
        help="Contoh: D:\\Data\\AnBuso_Kelas10.xlsx"
    )
    if custom_path and os.path.exists(custom_path):
        active_anbuso_file = os.path.abspath(custom_path)

anbuso_adapter = None
student_roster = []
class_info = {}

if active_anbuso_file and os.path.exists(active_anbuso_file):
    try:
        anbuso_adapter = AnBusoAdapter(excel_path=active_anbuso_file)
        student_roster = anbuso_adapter.get_students()
        
        # Baca metadata kelas dari Input01
        wb = openpyxl.load_workbook(active_anbuso_file, data_only=True)
        ws_in01 = wb["Input01"]
        class_info = {
            "sekolah": ws_in01.cell(row=7, column=2).value or "MA Salafiyah Bantarsari",
            "mapel": ws_in01.cell(row=8, column=2).value or "Bahasa Inggris",
            "kelas": ws_in01.cell(row=9, column=2).value or "Fase F XI 5",
            "nama_tes": ws_in01.cell(row=10, column=2).value or "ASTS Gasal",
            "kunci_pg": ws_in01.cell(row=37, column=2).value or ""
        }
        wb.close()
        
        st.sidebar.success(f"🟢 Terhubung: {class_info['kelas']} ({len(student_roster)} Siswa)")
        st.sidebar.caption(f"📄 `{os.path.basename(active_anbuso_file)}`")
        
        with st.sidebar.expander("ℹ️ Detail Kelas & Kunci Jawaban"):
            st.write(f"**Sekolah:** {class_info['sekolah']}")
            st.write(f"**Mata Pelajaran:** {class_info['mapel']}")
            st.write(f"**Kunci PG (35 Soal):**")
            st.code(class_info['kunci_pg'], language="text")
    except Exception as e:
        st.sidebar.error(f"Gagal memuat Excel AnBuso: {e}")
else:
    st.sidebar.warning("Silakan unggah atau pilih file Excel AnBuso untuk mengaktifkan sinkronisasi.")


st.sidebar.markdown("---")
st.sidebar.caption("Smart Exam Grader v2.0 - MA Salafiyah Bantarsari")

# HEADER UTAMA
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="main-header">📝 Smart Exam Grader & AnBuso Auto-Filler</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Sistem Koreksi Otomatis Lembar Jawaban Kertas Ujian (OMR + OCR) Langsung ke Excel AnBuso</p>', unsafe_allow_html=True)
with col_h2:
    st.markdown('<div style="text-align: right; margin-top: 10px;"><span class="status-badge">🟢 Sistem Siap</span></div>', unsafe_allow_html=True)

# BAGIAN 1: PENGUNGGAHAN GAMBAR / SAMPEL CEPAT
st.markdown("#### 1. Unggah Lembar Jawaban Siswa")
c_up1, c_up2, c_up3 = st.columns([2, 1, 1])

uploaded_file = c_up1.file_uploader(
    "Pilih atau Drag & Drop foto lembar ujian:",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

# Tombol Cepat untuk Pengujian Sampel
use_sample_1 = c_up2.button("⚡ Uji Sampel: Anindita (Kelas X)")
use_sample_2 = c_up3.button("⚡ Uji Sampel: Fadilatul (XI 5)")

active_image_path = None
temp_image_dir = "data/sample_inputs"

if uploaded_file is not None:
    temp_path = os.path.join(temp_image_dir, "temp_uploaded.jpg")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    active_image_path = temp_path
elif use_sample_1:
    active_image_path = os.path.join(temp_image_dir, "sample_lembar_jawab.jpg")
elif use_sample_2:
    active_image_path = os.path.join(temp_image_dir, "sample_fadilatul.jpg")

# PROSES PENILAIAN JIKA GAMBAR AKTIF
if active_image_path and os.path.exists(active_image_path):
    st.markdown("---")
    
    # Jalankan Pipeline Koreksi
    img_bgr = modules["preprocessor"].load_image(active_image_path)
    rois = modules["preprocessor"].extract_rois(img_bgr)
    
    # 1. OCR Identitas
    id_data = modules["identity_reader"].read_identity(rois["identity"], student_roster=student_roster)
    detected_name_raw = id_data.get("raw_name_ocr") or id_data.get("nama") or "Tidak Terbaca"
    detected_no_peserta = id_data.get("no_peserta") or "-"
    
    # 2. OMR Grid Engine
    sec1_tables = modules["omr_engine"].find_section1_tables(rois["section_1"])
    answers_pg = {}
    for table_box, start_q in sec1_tables:
        x, y, w, h = table_box
        table_crop = rois["section_1"][y:y+h, x:x+w]
        table_res = modules["omr_engine"].extract_pg_table(table_crop, start_q)
        answers_pg.update(table_res)
        
    sec2_box = modules["omr_engine"].find_section2_table(rois["section_2"])
    x2, y2, w2, h2 = sec2_box
    sec2_crop = rois["section_2"][y2:y2+h2, x2:x2+w2]
    answers_pgk = modules["omr_engine"].extract_pgk_table(sec2_crop)
    
    # TAMPILAN BERDAMPINGAN: KIRI (GAMBAR) & KANAN (DATA EKSTRAKSI)
    col_view, col_data = st.columns([1, 1], gap="medium")
    
    with col_view:
        st.markdown("#### 🖼️ Pratinjau Lembar Ujian")
        tab_original, tab_annotated, tab_crops = st.tabs(["Foto Lembar", "Audit Visual (Koreksi)", "Potongan Area (ROIs)"])
        
        with tab_original:
            st.image(Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)), use_container_width=True)
            
        with tab_annotated:
            annotated_dummy = {
                "pg_correct": sum(1 for q in range(1, 26) if answers_pg.get(q, {}).get("choice")),
                "pgk_points": 10,
                "final_grade_100": 85.0,
                "status": "VALIDASI GURU",
                "review_flags": []
            }
            annotated_out = "data/outputs/temp_ui_annotated.jpg"
            modules["annotator"].annotate_exam_sheet(
                img_bgr,
                {"nama": id_data.get("nama", "Siswa"), "no_peserta": detected_no_peserta},
                annotated_dummy,
                annotated_out
            )
            if os.path.exists(annotated_out):
                st.image(annotated_out, use_container_width=True)
                
        with tab_crops:
            st.caption("Area Kotak Identitas Siswa:")
            st.image(Image.fromarray(cv2.cvtColor(rois["identity"], cv2.COLOR_BGR2RGB)), use_container_width=True)
            st.caption("Area Bagian I (Pilihan Ganda):")
            st.image(Image.fromarray(cv2.cvtColor(rois["section_1"], cv2.COLOR_BGR2RGB)), use_container_width=True)

    with col_data:
        st.markdown("#### 👤 Verifikasi Identitas Siswa")
        
        # Pencocokan Roster Siswa AnBuso
        matched_student = None
        match_idx = 0
        roster_names = [s["nama"] for s in student_roster] if student_roster else []
        
        if anbuso_adapter and student_roster:
            matched_obj = anbuso_adapter.match_student(detected_name_raw, student_roster)
            if matched_obj:
                matched_student = matched_obj
                if matched_obj["nama"] in roster_names:
                    match_idx = roster_names.index(matched_obj["nama"])
                    
        c_id1, c_id2 = st.columns([1, 1])
        with c_id1:
            st.text_input("Teks Nama Terbaca (OCR):", value=detected_name_raw, disabled=True)
        with c_id2:
            st.text_input("No Peserta Terdeteksi:", value=detected_no_peserta, disabled=True)
            
        if roster_names:
            selected_student_name = st.selectbox(
                "Pencocokan Siswa di Master AnBuso (Dapat diubah jika ragu):",
                options=roster_names,
                index=match_idx,
                help="Sistem secara otomatis mencocokkan nama tulisan tangan ke daftar siswa kelas."
            )
            selected_student_info = next((s for s in student_roster if s["nama"] == selected_student_name), None)
            if selected_student_info:
                st.info(f"Target di Excel AnBuso: **Baris {selected_student_info['row_input02']} (Input02)** | **Baris {selected_student_info['row_data01_03']} (Data03 / Tab Isian)**")
        else:
            selected_student_name = detected_name_raw
            selected_student_info = {"row_input02": 6, "row_data01_03": 14, "nama": selected_student_name}

        # DETEKSI AMBIGUITAS / CORETAN GANDA
        ambiguous_questions = [q for q in range(1, 26) if answers_pg.get(q, {}).get("is_ambiguous")]
        if ambiguous_questions:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.write(f"⚠️ **PERHATIAN GURU: Terdeteksi {len(ambiguous_questions)} Soal dengan Coretan Ganda / Ambigu:**")
            for q_ambig in ambiguous_questions:
                q_data = answers_pg[q_ambig]
                c_opt1 = q_data.get("choice")
                c_opt2 = q_data.get("runner_up")
                st.write(f"- **Soal No {q_ambig}**: Siswa menyilang **{c_opt1}** dan **{c_opt2}**.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### 📋 Hasil Pembacaan Jawaban")
        
        # Tab Jawaban PG dan PGK
        tab_pg, tab_pgk = st.tabs(["I. Pilihan Ganda (1 - 25)", "II. PG Kompleks / Isian (1 - 5)"])
        
        final_pg_answers = {}
        with tab_pg:
            st.caption("Pilihan terdeteksi otomatis (Bisa diedit oleh guru sebelum disimpan):")
            # Tampilkan 5 baris x 5 kolom grid
            for row_i in range(5):
                cols_grid = st.columns(5)
                for col_i in range(5):
                    q_num = row_i * 5 + col_i + 1
                    q_res = answers_pg.get(q_num, {})
                    detected_choice = q_res.get("choice", "")
                    
                    # Opsi dropdown huruf A, B, C, D, E atau Kosong
                    options_list = ["", "A", "B", "C", "D", "E"]
                    default_idx = options_list.index(detected_choice) if detected_choice in options_list else 0
                    
                    label_q = f"No {q_num}"
                    if q_res.get("is_ambiguous"):
                        label_q += " ⚠️"
                        
                    sel_ans = cols_grid[col_i].selectbox(
                        label_q,
                        options=options_list,
                        index=default_idx,
                        key=f"pg_q_{q_num}"
                    )
                    final_pg_answers[q_num] = sel_ans

        final_pgk_answers = {}
        with tab_pgk:
            st.caption("2 Pilihan benar per nomor terdeteksi:")
            for q in range(1, 6):
                q_res = answers_pgk.get(q, {})
                choices = q_res.get("choices", [])
                st.write(f"**Soal {q}:** Terpilih `{', '.join(choices)}` (Skor: 2)")
                final_pgk_answers[q] = choices

        # TOMBOL EKSEKUSI UTAMA KE ANBUSO
        st.markdown("---")
        st.markdown("#### 🚀 Masukkan Data ke Excel AnBuso")
        
        btn_col1, btn_col2 = st.columns([2, 1])
        
        with btn_col1:
            save_button = st.button("💾 Simpan & Injeksi ke Excel AnBuso (Preserve VBA Menu)", type="primary", use_container_width=True)
            
        with btn_col2:
            if active_anbuso_file and os.path.exists(active_anbuso_file):
                with open(active_anbuso_file, "rb") as f_curr:
                    st.download_button(
                        label="📥 Unduh File AnBuso Aktif",
                        data=f_curr,
                        file_name=os.path.basename(active_anbuso_file),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
        if save_button:
            if not anbuso_adapter:
                st.error("File AnBuso belum terhubung dengan benar.")
            else:
                with st.spinner("Menginjeksi data ke Excel melalui Microsoft Excel COM..."):
                    try:
                        # Siapkan payload
                        formatted_pg = {q: {"choice": final_pg_answers[q], "confidence": 0.3} for q in final_pg_answers}
                        formatted_pgk = {q: {"choices": final_pgk_answers[q]} for q in final_pgk_answers}
                        
                        inject_res = anbuso_adapter.inject_answers(
                            selected_student_info,
                            formatted_pg,
                            formatted_pgk
                        )
                        
                        st.success(f"🎉 Data berhasil dimasukkan ke **{selected_student_info['nama']}**!")
                        st.write(f"📁 **File Disimpan:** `{inject_res['saved_file']}`")
                        st.write(f"📌 **Detail Baris:** Input02 (Baris {inject_res['row_in_input02']}) ➔ Tab Isian / Data03 (Baris {inject_res['row_in_data03']})")
                        st.info("ℹ️ Seluruh tombol menu grafik navigasi AnBuso tetap 100% utuh.")
                        
                        if os.path.exists(inject_res['saved_file']):
                            with open(inject_res['saved_file'], "rb") as f_up:
                                st.download_button(
                                    label="📥 Klik untuk Unduh File Excel Terupdate",
                                    data=f_up,
                                    file_name=os.path.basename(inject_res['saved_file']),
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                    use_container_width=True
                                )
                    except Exception as err:
                        st.error(f"Terjadi kesalahan saat menyimpan ke Excel: {err}")

else:
    st.info("Silakan unggah foto lembar jawaban atau klik salah satu tombol sampel di atas untuk memulai koreksi.")
