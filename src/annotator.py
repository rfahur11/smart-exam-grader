"""
Smart Exam Grader - Visual Annotator (Audit Trail Generator)
Menghasilkan gambar lembar jawaban beranotasi dengan kotak hijau (benar), merah (salah),
dan banner rekap skor di bagian atas untuk verifikasi manual guru.
"""

import cv2
import numpy as np
from typing import Dict, Any

class VisualAnnotator:
    def __init__(self):
        pass

    def annotate_exam_sheet(self,
                            original_img: np.ndarray,
                            identity: Dict[str, Any],
                            score_data: Dict[str, Any],
                            output_path: str = "data/outputs/annotated_sample_lembar_jawab.jpg") -> str:
        """Menambahkan visual banner dan indikator koreksi pada gambar lembar ujian."""
        annotated = original_img.copy()
        h, w = annotated.shape[:2]

        # 1. Gambar Banner Rekap di Bagian Atas
        banner_h = 55
        cv2.rectangle(annotated, (0, 0), (w, banner_h), (25, 25, 35), -1)

        nama = identity.get("nama", "Tidak Dikenal")
        no_peserta = identity.get("no_peserta", "-")
        nilai = score_data.get("final_grade_100", 0)
        status = score_data.get("status", "REMIDI")

        status_color = (80, 200, 100) if status == "LULUS" else (80, 80, 220)

        # Teks Info Siswa
        text_info = f"Siswa: {nama} ({no_peserta})"
        cv2.putText(annotated, text_info, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (240, 240, 240), 1, cv2.LINE_AA)

        # Teks Nilai & Status
        text_score = f"Skor PG: {score_data['pg_correct']}/25 | PGK: {score_data['pgk_points']}/10 | Total: {nilai} ({status})"
        cv2.putText(annotated, text_score, (15, 47), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA)

        # 2. Tandai Kotak Identitas
        id_y1, id_y2 = int(h * 0.08), int(h * 0.17)
        id_x1, id_x2 = int(w * 0.57), int(w * 0.93)
        cv2.rectangle(annotated, (id_x1, id_y1), (id_x2, id_y2), (0, 165, 255), 2)
        cv2.putText(annotated, "TERVERIFIKASI OCR", (id_x1, id_y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 1, cv2.LINE_AA)

        # 3. Tandai Review Flags jika ada
        if score_data.get("review_flags"):
            cv2.rectangle(annotated, (15, h - 35), (w - 15, h - 10), (0, 215, 255), -1)
            cv2.putText(annotated, "PERHATIAN: Ada nomor yang membutuhkan verifikasi manual!",
                        (25, h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 2, cv2.LINE_AA)

        cv2.imwrite(output_path, annotated)
        return output_path
