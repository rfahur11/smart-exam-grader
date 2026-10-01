"""
Smart Exam Grader - Scoring Engine
Mengevaluasi hasil deteksi jawaban siswa terhadap Kunci Jawaban (Master Answer Key),
menghitung bobot skor PG & PGK, mengonversi ke skala 100, dan mendeteksi review flag.
"""

from typing import Dict, Any, List, Optional

class ScoringEngine:
    def __init__(self,
                 kunci_pg: Optional[Dict[int, str]] = None,
                 kunci_pgk: Optional[Dict[int, List[str]]] = None,
                 kkm: float = 75.0):
        # Kunci Jawaban Default (dapat di-override via parameter)
        self.kunci_pg = kunci_pg or {
            1: 'B', 2: 'B', 3: 'B', 4: 'C', 5: 'B',
            6: 'C', 7: 'E', 8: 'B', 9: 'D', 10: 'E',
            11: 'B', 12: 'A', 13: 'C', 14: 'B', 15: 'E',
            16: 'E', 17: 'A', 18: 'C', 19: 'C', 20: 'D',
            21: 'B', 22: 'D', 23: 'C', 24: 'C', 25: 'A'
        }
        self.kunci_pgk = kunci_pgk or {
            1: ['A', 'C'],
            2: ['A', 'C'],
            3: ['A', 'C'],
            4: ['A', 'D'],
            5: ['B', 'E']
        }
        self.kkm = kkm

    def grade(self, answers_pg: Dict[int, Dict[str, Any]], answers_pgk: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Menilai jawaban siswa:
        - PG: 1 poin per nomor benar (Total Max: 25)
        - PGK: 2 poin jika kedua jawaban benar, 1 poin jika benar satu (Total Max: 10)
        """
        # 1. Evaluasi PG
        pg_correct_count = 0
        pg_details = {}
        review_flags = []

        for q_num in range(1, 26):
            q_res = answers_pg.get(q_num, {})
            student_choice = q_res.get("choice", "")
            correct_key = self.kunci_pg.get(q_num, "")
            is_ambiguous = q_res.get("is_ambiguous", False)
            runner_up = q_res.get("runner_up")

            is_correct = (student_choice == correct_key)
            if is_correct:
                pg_correct_count += 1

            if is_ambiguous:
                review_flags.append(f"PG No {q_num}: Terdeteksi 2 tanda silang ({student_choice} & {runner_up}).")

            pg_details[q_num] = {
                "student": student_choice,
                "key": correct_key,
                "is_correct": is_correct,
                "is_ambiguous": is_ambiguous
            }

        # 2. Evaluasi PGK
        pgk_points = 0
        pgk_details = {}

        for q_num in range(1, 6):
            q_res = answers_pgk.get(q_num, {})
            student_choices = set(q_res.get("choices", []))
            correct_keys = set(self.kunci_pgk.get(q_num, []))

            # Hitung jumlah pilihan yang cocok
            matched = len(student_choices.intersection(correct_keys))
            if matched == 2 and len(student_choices) == 2:
                points = 2
            elif matched >= 1:
                points = 1
            else:
                points = 0

            pgk_points += points
            pgk_details[q_num] = {
                "student": sorted(list(student_choices)),
                "key": sorted(list(correct_keys)),
                "points": points,
                "max_points": 2
            }

        # 3. Hitung Total Skor & Konversi Skala 100
        max_pg = 25
        max_pgk = 10
        total_score_raw = pg_correct_count + pgk_points
        max_score_raw = max_pg + max_pgk
        final_grade_100 = round((total_score_raw / max_score_raw) * 100, 1)

        status = "LULUS" if final_grade_100 >= self.kkm else "REMIDI"

        catatan = "Valid"
        if review_flags:
            catatan = "; ".join(review_flags)

        return {
            "pg_correct": pg_correct_count,
            "pg_max": max_pg,
            "pgk_points": pgk_points,
            "pgk_max": max_pgk,
            "total_score_raw": total_score_raw,
            "final_grade_100": final_grade_100,
            "status": status,
            "catatan": catatan,
            "review_flags": review_flags,
            "pg_details": pg_details,
            "pgk_details": pgk_details
        }
