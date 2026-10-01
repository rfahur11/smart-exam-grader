"""
Smart Exam Grader - Image Preprocessor
Menangani load gambar, enhancement kontras, binarisasi, dan segmentasi zona lembar ujian.
"""

import os
import cv2
import numpy as np
from typing import Tuple, Dict, Any

class ExamPreprocessor:
    def __init__(self, debug_dir: str = "data/outputs"):
        self.debug_dir = debug_dir
        os.makedirs(self.debug_dir, exist_ok=True)

    def load_image(self, image_path: str) -> np.ndarray:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File gambar tidak ditemukan: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Gagal membaca gambar dari: {image_path}")
        return img

    def enhance_contrast(self, gray: np.ndarray) -> np.ndarray:
        """Menerapkan CLAHE (Contrast Limited Adaptive Histogram Equalization) untuk meratakan pencahayaan."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def binarize(self, gray: np.ndarray) -> np.ndarray:
        """Binarisasi inversi menggunakan Otsu Thresholding (Tinta hitam menjadi putih/255)."""
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return thresh

    def extract_rois(self, img: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Mengekstrak 3 area kunci lembar ujian berdasarkan tata letak proporsional:
        1. identity_box: Area Nama & No Peserta (Kanan Atas)
        2. section_1: Area Tabel PG 1 s/d 25
        3. section_2: Area Tabel PGK 1 s/d 5
        """
        h, w = img.shape[:2]

        # 1. Identity Box (Kanan Atas)
        # y: 4% s/d 16%, x: 55% s/d 98%
        id_y1, id_y2 = int(h * 0.04), int(h * 0.16)
        id_x1, id_x2 = int(w * 0.55), int(w * 0.98)
        identity_roi = img[id_y1:id_y2, id_x1:id_x2]

        # 2. Section 1 (Pilihan Ganda 1-25)
        # y: 27% s/d 65%, x: 4% s/d 98%
        sec1_y1, sec1_y2 = int(h * 0.27), int(h * 0.65)
        sec1_x1, sec1_x2 = int(w * 0.04), int(w * 0.98)
        sec1_roi = img[sec1_y1:sec1_y2, sec1_x1:sec1_x2]

        # 3. Section 2 (Pilihan Ganda Kompleks 1-5)
        # y: 62% s/d 98%, x: 4% s/d 55%
        sec2_y1, sec2_y2 = int(h * 0.62), int(h * 0.98)
        sec2_x1, sec2_x2 = int(w * 0.04), int(w * 0.55)
        sec2_roi = img[sec2_y1:sec2_y2, sec2_x1:sec2_x2]

        return {
            "identity": identity_roi,
            "section_1": sec1_roi,
            "section_2": sec2_roi
        }
