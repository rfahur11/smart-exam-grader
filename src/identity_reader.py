"""
Smart Exam Grader - Identity Reader
Mengekstrak No Peserta dan Nama Siswa dari kotak identitas menggunakan OCR lokal (RapidOCR)
dan mencocokkan ke database/roster siswa menggunakan Fuzzy Matching.
"""

import re
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from thefuzz import process, fuzz

try:
    from rapidocr_onnxruntime import RapidOCR
    RAPID_OCR_AVAILABLE = True
except ImportError:
    RAPID_OCR_AVAILABLE = False

class IdentityReader:
    def __init__(self):
        if RAPID_OCR_AVAILABLE:
            self.engine = RapidOCR()
        else:
            self.engine = None

    def read_identity(self, id_roi: np.ndarray, student_roster: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Membaca teks dari gambar kotak identitas.
        student_roster: List dict [{'no_peserta': '...', 'nama': '...'}] dari Excel template.
        """
        raw_text_lines = []
        if self.engine is not None:
            results, _ = self.engine(id_roi)
            if results:
                for item in results:
                    text = item[1].strip()
                    conf = float(item[2])
                    raw_text_lines.append((text, conf))

        # Ekstraksi Nama & No Peserta dari hasil OCR
        detected_name = ""
        detected_no_peserta = ""

        for idx, (text, conf) in enumerate(raw_text_lines):
            clean_text = text.upper()
            if "NAMA" in clean_text:
                # Cek apakah ada teks nama di line yang sama atau line berikutnya
                parts = text.split(":", 1)
                if len(parts) > 1 and len(parts[1].strip()) > 2:
                    detected_name = parts[1].strip()
                elif idx + 1 < len(raw_text_lines):
                    next_text = raw_text_lines[idx + 1][0]
                    if "PESERTA" not in next_text.upper():
                        detected_name = next_text

            if "PESERTA" in clean_text or "NO" in clean_text:
                parts = text.split(":", 1)
                if len(parts) > 1 and len(parts[1].strip()) > 3:
                    detected_no_peserta = parts[1].strip()
                elif idx + 1 < len(raw_text_lines):
                    next_text = raw_text_lines[idx + 1][0]
                    detected_no_peserta = next_text

        # Bersihkan karakter aneh pada nama (misal separator titik tengah/simbol)
        cleaned_name = re.sub(r'[^a-zA-Z\s\.]', ' ', detected_name).strip()
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name)

        matched_student = None
        match_score = 0.0

        # Jika diberikan student_roster dari master Excel, lakukan pencocokan cerdas
        if student_roster:
            roster_names = [s["nama"] for s in student_roster]
            if cleaned_name:
                best_name, score = process.extractOne(cleaned_name, roster_names, scorer=fuzz.token_sort_ratio)
                match_score = score
                if score >= 65: # Threshold toleransi tulisan tangan
                    # Temukan objek siswa di roster
                    for s in student_roster:
                        if s["nama"] == best_name:
                            matched_student = s
                            break

        # Fallback jika tidak ada roster match tetapi nomor peserta terdeteksi
        final_name = matched_student["nama"] if matched_student else (cleaned_name or "Tidak Terbaca")
        final_no_peserta = matched_student["no_peserta"] if matched_student else detected_no_peserta

        return {
            "nama": final_name,
            "no_peserta": final_no_peserta,
            "raw_name_ocr": detected_name,
            "raw_no_peserta_ocr": detected_no_peserta,
            "match_confidence": match_score,
            "is_matched_with_roster": matched_student is not None
        }
