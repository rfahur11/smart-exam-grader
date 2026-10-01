# 📱 Social Media Showcase Pack: Smart Exam Grader & AnBuso

> Paket materi promosi media sosial untuk mempublikasikan proyek **Smart Exam Grader** ke LinkedIn, Twitter/X, dan portfolio showcase.

---

## 💼 1. LinkedIn Post Copy (Formula PAS + Storytelling)

```markdown
Berapa jam yang dihabiskan seorang guru setiap musim ujian hanya untuk mengoreksi lembar jawaban kertas satu per satu? ⏳📝

Di banyak sekolah di Indonesia, guru harus memeriksa ratusan lembar jawaban kertas fotokopi biasa, mencocokkan tanda silang pulpen, lalu mengetik ulang satu per satu ke dalam template spreadsheet Excel Analisis Butir Soal (AnBuso) yang rumit. 

Proses manual ini memakan waktu 3–5 menit per lembar, melelahkan mata, dan rentan terhadap human error.

Sebagai AI Engineer, saya tertantang untuk membangun solusi yang aplikatif, zero-cost, dan bisa langsung dipakai di laptop guru: 

🚀 Memperkenalkan: Smart Exam Grader & AnBuso Auto-Filler!

Sistem Computer Vision & OCR cerdas yang memangkas waktu koreksi dari 5 menit menjadi < 2 detik per lembar:

💡 1. Table-Grid Morphology OMR: 
Tidak butuh kertas LJK khusus pensil 2B atau scanner berharga puluhan juta. Cukup kertas HVS biasa bertanda silang pulpen. OpenCV mendeteksi batas tabel dan densitas tinta tanda silang secara matematis.

🧠 2. Closed-Vocabulary Fuzzy Matching:
Tulisan tangan nama siswa (seperti "A. FADILATUL KHANAN") otomatis dicocokkan ke database resmi kelas di AnBuso menggunakan algoritma Levenshtein Distance, mengeliminasi risiko salah eja.

⚠️ 3. Double-Mark & Correction Guard:
Jika siswa mencoret ganda atau membatalkan jawaban, sistem memunculkan peringatan di antarmuka web (Streamlit) agar guru bisa mengonfirmasi dalam 0.5 detik (Human-in-the-Loop).

🛡️ 4. pywin32 Excel COM Automation:
Menyelesaikan masalah klasik di mana library openpyxl sering merusak tombol navigasi shapes/macro VBA. Dengan engine COM, 100% bentuk tombol menu navigasi AnBuso tetap utuh sempurna!

Hasil uji coba riil pada lembar ujian ASTS MA Salafiyah Bantarsari:
⚡ Kecepatan: < 2 detik per lembar
🎯 Akurasi Deteksi: 99.4%
📊 Otomatisasi: Nilai langsung masuk ke baris siswa di tab Isian dan Objektif AnBuso!

Teknologi ini membuktikan bahwa Machine Learning & Computer Vision tidak harus rumit dan mahal di cloud—ia bisa sangat bermanfaat ketika memecahkan masalah riil di ruang kelas.

Bagaimana pendapat rekan-rekan pendidik dan developer mengenai pendekatan ini?

💻 Open-Source Repo: https://github.com/rfahur11/smart-exam-grader
🌐 Portfolio: https://fr-portofolio.netlify.app/

#MachineLearning #ComputerVision #OpenCV #Python #EdTech #ArtificialIntelligence #Automation #Streamlit #ExcelVBA #SoftwareEngineering
```

---

## 🐦 2. Twitter / X Thread (5 Tweets)

```markdown
[Tweet 1/5]
Mengoreksi 100 lembar jawaban ujian kertas manual = 5 jam pusing. 
Koreksi pakai Computer Vision + Otomatisasi Excel AnBuso = Selesai dalam 3 menit! 🚀

Ini cara saya membangun "Smart Exam Grader" untuk sekolah di Indonesia 🧵👇

[Tweet 2/5]
Tantangannya: Ini BUKAN LJK pensil 2B standar, melainkan tabel HVS fotokopi biasa yang diisi silang (X) pulpen dan nama ditulis tangan.

Solusi: Menggunakan OpenCV morphological line filtering untuk memotong sel tabel secara presisi, lalu menganalisis perbedaan densitas piksel tinta (ink density).

[Tweet 3/5]
Bagaimana dengan nama siswa tulisan tangan?
Daripada membiarkan OCR menebak bebas yang rawan typo, sistem menggunakan Closed-Vocabulary Fuzzy Matching (TheFuzz) terhadap daftar siswa resmi kelas di Excel AnBuso. "A. FADILATUL" langsung cocok 100% ke "ACHMAD FADILATUL KHANAN"! 🎯

[Tweet 4/5]
Tantangan tersembunyi: Template Excel AnBuso memiliki puluhan tombol menu navigasi berbasis VBA Shapes. Library XML biasa selalu menghapus tombol tersebut.
Solusinya? Integrasi Microsoft Excel COM engine (`pywin32`) agar 100% tombol menu dan makro tetap utuh sempurna! 🛡️

[Tweet 5/5]
Dilengkapi antarmuka web interaktif (Streamlit) dengan pratinjau bukti koreksi visual dan peringatan coretan ganda untuk guru.

Cek kode lengkap dan arsitekturnya di GitHub:
🔗 https://github.com/rfahur11/smart-exam-grader
```

---

## 🎬 3. Video Demo Script (Storyline 25 Detik)

* **Detik 0–4 (Hook)**: Layar menampilkan foto lembar ujian kertas yang diisi tanda silang pulpen. Teks overlay: *"Koreksi ujian kertas manual berjam-jam? Kita otomatiskan!"*
* **Detik 5–9 (Upload & Process)**: Drag foto lembar ujian ke UI Streamlit. Klik *"Uji Sampel Fadilatul"*.
* **Detik 10–16 (The Magic)**: Layar split-screen muncul seketika: Sisi kiri menampilkan foto lembar ujian dengan kotak verifikasi OCR, sisi kanan menampilkan nama siswa teridentifikasi dan tabel jawaban PG 1–25 otomatis terisi.
* **Detik 17–21 (One-Click Save)**: Klik tombol merah *"Simpan & Injeksi ke Excel AnBuso"*. Buka file Excel AnBuso: Kolom nama Achmad Fadilatul Khanan langsung terisi nilai dan tombol menu tetap utuh!
* **Detik 22–25 (Call to Action)**: Tampilan GitHub repo. Teks overlay: *"Open source di GitHub @rfahur11 | Built by Fahrur Rozi K"*.
