"""
Smart Exam Grader - Main CLI Orchestrator
Mengotomatisasi penilaian lembar jawaban kertas ujian (OMR Grid + OCR) dan ekspor ke Excel.
"""

import os
import sys
import argparse
from typing import Dict, Any

from src.preprocessor import ExamPreprocessor
from src.identity_reader import IdentityReader
from src.omr_grid_engine import OMRGridEngine
from src.scoring_engine import ScoringEngine
from src.excel_exporter import ExcelExporter
from src.annotator import VisualAnnotator

def process_exam_sheet(image_path: str,
                       template_path: str = "data/templates/daftar_nilai_template.xlsx",
                       output_excel: str = "data/outputs/daftar_nilai_terkoreksi.xlsx",
                       output_img: str = "data/outputs/annotated_sample_lembar_jawab.jpg") -> Dict[str, Any]:
    print("\n" + "="*65)
    print("[*] SMART EXAM GRADER: SISTEM PENILAIAN LEMBAR UJIAN OTOMATIS")
    print("="*65)

    # 1. Inisialisasi Modul
    preprocessor = ExamPreprocessor()
    identity_reader = IdentityReader()
    omr_engine = OMRGridEngine()
    scoring_engine = ScoringEngine()
    excel_exporter = ExcelExporter(template_path=template_path)
    annotator = VisualAnnotator()

    # 2. Preprocessing & Ekstraksi ROI
    print(f"\n[1/5] Memuat dan mensegmentasi lembar ujian: {image_path}...")
    img = preprocessor.load_image(image_path)
    rois = preprocessor.extract_rois(img)

    # 3. Pembacaan Identitas Siswa & Matching Roster
    print("[2/5] Membaca kotak identitas siswa (OCR & Fuzzy Roster Match)...")
    roster = excel_exporter.get_student_roster()
    identity = identity_reader.read_identity(rois["identity"], student_roster=roster)
    
    print(f"      -> Nama Terbaca    : {identity['nama']}")
    print(f"      -> No Peserta      : {identity['no_peserta']}")
    print(f"      -> Status Matching : {'COCOK DENGAN DAFTAR KELAS' if identity['is_matched_with_roster'] else 'SISWA BARU'} (Skor: {identity['match_confidence']}%)")

    # 4. Deteksi Pilihan Ganda (Bagian I: Q1-25) & Kompleks (Bagian II: Q1-5)
    print("\n[3/5] Menganalisis densitas tanda silang (OMR Grid Engine)...")
    sec1_tables = omr_engine.find_section1_tables(rois["section_1"])
    answers_pg = {}
    for table_box, start_q in sec1_tables:
        x, y, w, h = table_box
        table_crop = rois["section_1"][y:y+h, x:x+w]
        table_res = omr_engine.extract_pg_table(table_crop, start_q)
        answers_pg.update(table_res)

    sec2_box = omr_engine.find_section2_table(rois["section_2"])
    x2, y2, w2, h2 = sec2_box
    sec2_crop = rois["section_2"][y2:y2+h2, x2:x2+w2]
    answers_pgk = omr_engine.extract_pgk_table(sec2_crop)

    print(f"      -> Terdeteksi {len(answers_pg)} nomor Pilihan Ganda.")
    print(f"      -> Terdeteksi {len(answers_pgk)} nomor Pilihan Ganda Kompleks.")

    # 5. Penilaian & Kalkulasi Skor
    print("\n[4/5] Menghitung nilai berdasarkan Kunci Jawaban...")
    grade_res = scoring_engine.grade(answers_pg, answers_pgk)
    print(f"      -> Skor PG     : {grade_res['pg_correct']}/{grade_res['pg_max']}")
    print(f"      -> Skor PGK    : {grade_res['pgk_points']}/{grade_res['pgk_max']}")
    print(f"      -> Nilai Akhir : {grade_res['final_grade_100']} / 100")
    print(f"      -> Status      : {grade_res['status']}")

    if grade_res['review_flags']:
        print(f"      [!] PERHATIAN: {len(grade_res['review_flags'])} nomor ambigu terdeteksi!")
        for flag in grade_res['review_flags']:
            print(f"          - {flag}")

    # 6. Ekspor ke File Excel & Visual Audit
    print("\n[5/5] Menginjeksi data ke Excel dan menghasilkan bukti koreksi visual...")
    excel_res = excel_exporter.export_grade(identity, grade_res, output_path=output_excel)
    print(f"      -> File Excel berhasil diperbarui : {excel_res['output_file']}")
    print(f"      -> Baris Diperbarui               : Baris {excel_res['row_updated']} ({excel_res['matched_by']})")

    annotated_path = annotator.annotate_exam_sheet(img, identity, grade_res, output_path=output_img)
    print(f"      -> Bukti visual koreksi tersimpan : {annotated_path}")

    print("\n" + "="*65)
    print("[SUCCESS] PROSES SELESAI DENGAN SUKSES!")
    print("="*65 + "\n")

    return {
        "identity": identity,
        "grade_res": grade_res,
        "excel_res": excel_res,
        "annotated_path": annotated_path
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smart Exam Grader CLI")
    parser.add_argument("--image", default="data/sample_inputs/sample_lembar_jawab.jpg", help="Path ke foto lembar ujian")
    parser.add_argument("--template", default="data/templates/daftar_nilai_template.xlsx", help="Path template Excel")
    parser.add_argument("--output-excel", default="data/outputs/daftar_nilai_terkoreksi.xlsx", help="Path output Excel")
    parser.add_argument("--output-img", default="data/outputs/annotated_sample_lembar_jawab.jpg", help="Path output gambar anotasi")

    args = parser.parse_args()
    process_exam_sheet(args.image, args.template, args.output_excel, args.output_img)
