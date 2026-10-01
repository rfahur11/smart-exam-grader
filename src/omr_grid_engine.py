"""
Smart Exam Grader - OMR Grid Engine
Mendeteksi tabel pilihan ganda (Section 1: No 1-25) dan pilihan ganda kompleks (Section 2: No 1-5),
menghitung densitas piksel tinta/silang, serta mendeteksi multi-marked/jawaban ambigu.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

class OMRGridEngine:
    def __init__(self, debug: bool = True):
        self.debug = debug
        self.options = ["No", "A", "B", "C", "D", "E"]

    def find_section1_tables(self, sec1_img: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Mendeteksi 5 kotak tabel di Bagian I secara morfologis:
        - Kolom 1 (Kiri)  : Q1-5 (Atas), Q6-10 (Bawah)
        - Kolom 2 (Tengah): Q11-15 (Atas), Q16-20 (Bawah)
        - Kolom 3 (Kanan) : Q21-25 (Atas)
        """
        gray = cv2.cvtColor(sec1_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 1))
        vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))

        horiz = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel)
        vert = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vert_kernel)
        grid = cv2.add(horiz, vert)

        contours, _ = cv2.findContours(grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 150 and h > 80:
                boxes.append((x, y, w, h))

        # Jika morfologi mendeteksi tepat 5 tabel, kelompokkan berdasarkan posisi spasial
        if len(boxes) >= 5:
            # Urutkan berdasarkan koordinat X (kolom) lalu Y (baris)
            col1 = sorted([b for b in boxes if b[0] < 120], key=lambda b: b[1])
            col2 = sorted([b for b in boxes if 150 <= b[0] < 350], key=lambda b: b[1])
            col3 = sorted([b for b in boxes if b[0] >= 350], key=lambda b: b[1])

            sorted_tables = []
            if len(col1) >= 2:
                sorted_tables.append((col1[0], 1))   # Q1-5
                sorted_tables.append((col1[1], 6))   # Q6-10
            if len(col2) >= 2:
                sorted_tables.append((col2[0], 11))  # Q11-15
                sorted_tables.append((col2[1], 16))  # Q16-20
            if len(col3) >= 1:
                sorted_tables.append((col3[0], 21))  # Q21-25

            return sorted_tables

        # Fallback koordinat statis terkalibrasi jika kontur terhalang noise
        return [
            ((16, 17, 202, 127), 1),    # Q1-5
            ((13, 157, 205, 126), 6),   # Q6-10
            ((235, 24, 186, 124), 11),  # Q11-15
            ((234, 161, 186, 121), 16), # Q16-20
            ((437, 31, 179, 120), 21)   # Q21-25
        ]

    def find_section2_table(self, sec2_img: np.ndarray) -> Tuple[int, int, int, int]:
        """Mendeteksi tabel Bagian II (Pilihan Ganda Kompleks)."""
        gray = cv2.cvtColor(sec2_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 1))
        vert_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))
        grid = cv2.add(cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel),
                       cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vert_kernel))

        contours, _ = cv2.findContours(grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 150 and h > 150:
                return (x, y, w, h)

        # Fallback terkalibrasi
        return (9, 16, 206, 255)

    def extract_pg_table(self, table_img: np.ndarray, start_q: int) -> Dict[int, Dict[str, Any]]:
        """Mengekstrak jawaban 5 soal pilihan ganda reguler."""
        gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        h, w = thresh.shape

        cols = 6
        rows = 5
        cell_w = w / cols
        cell_h = h / rows

        results = {}
        for r in range(rows):
            q_num = start_q + r
            densities = {}
            for c in range(1, cols):
                opt = self.options[c]
                # Margin dalam 15% untuk membuang garis batas tabel
                y1 = int(r * cell_h + cell_h * 0.15)
                y2 = int((r + 1) * cell_h - cell_h * 0.15)
                x1 = int(c * cell_w + cell_w * 0.15)
                x2 = int((c + 1) * cell_w - cell_w * 0.15)

                cell_roi = thresh[y1:y2, x1:x2]
                ink = cv2.countNonZero(cell_roi)
                density = ink / max(1, (cell_roi.shape[0] * cell_roi.shape[1]))
                densities[opt] = density

            sorted_opts = sorted(densities.items(), key=lambda x: x[1], reverse=True)
            top1_opt, top1_val = sorted_opts[0]
            top2_opt, top2_val = sorted_opts[1]

            # Cek apakah nomor ini kosong / tidak dijawab (densitas hanya huruf cetak < 0.16)
            is_unanswered = (top1_val < 0.16)
            final_choice = "" if is_unanswered else top1_opt

            # Ambiguity check: jika ada 2 opsi dengan densitas tinggi (> 0.20) dan selisih < 0.08
            is_ambiguous = (not is_unanswered and top1_val > 0.20 and top2_val > 0.20 and (top1_val - top2_val) < 0.08)

            results[q_num] = {
                "choice": final_choice,
                "confidence": float(top1_val),
                "is_unanswered": is_unanswered,
                "is_ambiguous": is_ambiguous,
                "runner_up": top2_opt if is_ambiguous else None,
                "densities": {k: float(v) for k, v in densities.items()}
            }

        return results

    def extract_pgk_table(self, table_img: np.ndarray) -> Dict[int, Dict[str, Any]]:
        """Mengekstrak jawaban 5 soal pilihan ganda kompleks (2 pilihan per nomor)."""
        gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        h, w = thresh.shape

        cols = 6
        rows = 10 # 5 soal * 2 baris sub-pilihan
        cell_w = w / cols
        cell_h = h / rows

        results = {}
        for q_idx in range(5):
            q_num = q_idx + 1
            choices = []
            row_details = []

            for sub_r in range(2):
                r = q_idx * 2 + sub_r
                densities = {}
                for c in range(1, cols):
                    opt = self.options[c]
                    y1 = int(r * cell_h + cell_h * 0.15)
                    y2 = int((r + 1) * cell_h - cell_h * 0.15)
                    x1 = int(c * cell_w + cell_w * 0.15)
                    x2 = int((c + 1) * cell_w - cell_w * 0.15)

                    cell_roi = thresh[y1:y2, x1:x2]
                    ink = cv2.countNonZero(cell_roi)
                    density = ink / max(1, (cell_roi.shape[0] * cell_roi.shape[1]))
                    densities[opt] = density

                sorted_opts = sorted(densities.items(), key=lambda x: x[1], reverse=True)
                top_opt, top_val = sorted_opts[0]
                choices.append(top_opt)
                row_details.append({"choice": top_opt, "confidence": float(top_val), "densities": densities})

            # Hilangkan duplikat jika tidak sengaja memilih huruf yang sama di kedua baris
            unique_choices = list(dict.fromkeys(choices))

            results[q_num] = {
                "choices": unique_choices,
                "raw_subrows": choices,
                "details": row_details
            }

        return results
