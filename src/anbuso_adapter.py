"""
Smart Exam Grader - AnBuso Excel Adapter
Menangani injeksi data lembar jawaban ke format standar Analisis Butir Soal (AnBuso) VBA:
- Master sheet: 'Input02' (Kolom D-AB untuk PG 1-25, Kolom BB-BF untuk Isian/PGK 1-5)
- Otomatis memperbarui tab 'Data01' (Objektif), 'Data03' (Isian), dan 'Peserta' (Nilai) via formula AnBuso.
"""

import os
import openpyxl
from typing import Dict, Any, List, Optional
from thefuzz import process, fuzz

class AnBusoAdapter:
    def __init__(self, excel_path: str = r"C:\Users\black\Downloads\10, Fase F XI 5_ASTS_AnBuso_Bahasa Inggris.xlsx"):
        self.excel_path = excel_path

    def get_students(self) -> List[Dict[str, Any]]:
        """Membaca daftar nama siswa dari sheet Input02."""
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"File AnBuso Excel tidak ditemukan: {self.excel_path}")

        wb = openpyxl.load_workbook(self.excel_path, data_only=True)
        ws = wb["Input02"]

        students = []
        for r in range(6, ws.max_row + 1):
            nama = ws.cell(row=r, column=2).value
            gender = ws.cell(row=r, column=3).value
            if nama:
                students.append({
                    "row_input02": r,
                    "row_data01_03": r + 8, # Row 6 di Input02 memetakan ke Row 14 di Data01/Data03
                    "nama": str(nama).strip(),
                    "gender": str(gender or "").strip()
                })
        wb.close()
        return students

    def match_student(self, detected_name: str, students: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Mencocokkan nama hasil OCR dengan daftar siswa di AnBuso."""
        names = [s["nama"] for s in students]
        # Coba partial ratio dan token sort ratio
        match1, score1 = process.extractOne(detected_name, names, scorer=fuzz.token_set_ratio)
        match2, score2 = process.extractOne(detected_name, names, scorer=fuzz.partial_ratio)

        best_match = match1 if score1 >= score2 else match2
        best_score = max(score1, score2)

        if best_score >= 60:
            for s in students:
                if s["nama"] == best_match:
                    res = s.copy()
                    res["match_score"] = best_score
                    return res
        return None

    def inject_answers(self,
                       student_info: Dict[str, Any],
                       answers_pg: Dict[int, Dict[str, Any]],
                       answers_pgk: Dict[int, Dict[str, Any]],
                       save_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Mengisi jawaban siswa ke sheet Input02:
        - Kolom D (4) s/d AB (28): Jawaban PG 1 s/d 25
        - Kolom BB (54) s/d BF (58): Skor / Isian PGK 1 s/d 5
        """
        target_path = save_path or self.excel_path
        wb = openpyxl.load_workbook(self.excel_path, data_only=False)
        ws_in02 = wb["Input02"]

        row_in02 = student_info["row_input02"]
        student_name = student_info["nama"]

        # 1. Tulis Jawaban Pilihan Ganda (1 s/d 25)
        # Soal 1 ada di Kolom 4 (D)
        pg_injected = {}
        for q in range(1, 26):
            col_idx = 3 + q
            q_res = answers_pg.get(q, {})
            choice = q_res.get("choice", "")
            conf = q_res.get("confidence", 0)

            # Jika confidence rendah (< 0.15), anggap kosong
            val_to_write = choice if (conf >= 0.15 and choice != "-") else ""
            ws_in02.cell(row=row_in02, column=col_idx, value=val_to_write)
            pg_injected[q] = val_to_write

        # 2. Tulis Skor Isian Singkat / PGK (1 s/d 5)
        # Soal 1 isian ada di Kolom 54 (BB)
        pgk_injected = {}
        for q in range(1, 6):
            col_idx = 53 + q
            q_res = answers_pgk.get(q, {})
            choices = q_res.get("choices", [])

            # Format representasi isian: gabungan huruf pilihan (misal: "A, C") atau skor
            # Di AnBuso, jika soal isian dinilai skor angka (0/1/2) atau string
            pgk_str = ", ".join(choices)
            # Berikan skor default 2 jika dijawab
            skor_pgk = 2 if len(choices) >= 2 else (1 if len(choices) == 1 else 0)
            ws_in02.cell(row=row_in02, column=col_idx, value=skor_pgk)
            pgk_injected[q] = {"choices": pgk_str, "score": skor_pgk}

        # Gunakan pywin32 Excel COM jika tersedia agar seluruh tombol menu (Drawing Shapes/VBA) tidak hilang
        try:
            import win32com.client as win32
            excel = win32.Dispatch('Excel.Application')
            excel.Visible = False
            excel.DisplayAlerts = False
            try:
                wb_com = excel.Workbooks.Open(os.path.abspath(target_path))
                ws_in01_com = wb_com.Sheets('Input01')
                if ws_in01_com.Range('B27').Value is None or ws_in01_com.Range('B27').Value == '':
                    ws_in01_com.Range('B27').Value = 5

                ws_in02_com = wb_com.Sheets('Input02')
                for q in range(1, 26):
                    ws_in02_com.Cells(row_in02, 3 + q).Value = pg_injected.get(q, '')
                for q in range(1, 6):
                    ws_in02_com.Cells(row_in02, 53 + q).Value = pgk_injected.get(q, {}).get('score', 0)

                wb_com.Save()
                wb_com.Close(SaveChanges=True)
                saved_to = target_path
            finally:
                excel.Quit()
        except Exception as e:
            # Fallback ke openpyxl jika Excel COM terkunci/tidak tersedia
            try:
                wb.save(target_path)
                saved_to = target_path
            except PermissionError:
                fallback_path = target_path.replace(".xlsx", "_TERISI.xlsx")
                wb.save(fallback_path)
                saved_to = fallback_path

        return {
            "student_name": student_name,
            "row_in_input02": row_in02,
            "row_in_data03": student_info["row_data01_03"],
            "pg_injected": pg_injected,
            "pgk_injected": pgk_injected,
            "saved_file": saved_to
        }
