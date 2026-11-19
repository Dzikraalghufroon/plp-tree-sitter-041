# Code Quality Checker (Linter Mini Berbasis Tree-sitter)

Tool Command-Line Interface (CLI) berbasis **Tree-sitter** untuk menganalisis kualitas kode sumber secara deterministik dan cepat pada repositori Python (`.py`) dan JavaScript (`.js`).

Tool ini dibangun sebagai implementasi **Tugas 6 (Mini Proyek)** mata kuliah Perancangan Bahasa Pemrograman (PLP).

---

## 1. Fitur Utama

Tool ini memeriksa 3 aspek kualitas kode:

1. **Deteksi Komentar `TODO` dan `FIXME`**
   - Menggunakan query deklaratif tree-sitter dengan predikat `#match?`.
   - Menangkap seluruh komentar teknis yang menandai hutang teknis (*technical debt*) beserta nomor barisnya.
   - Mengabaikan komentar dokumentasi biasa.

2. **Deteksi Fungsi Terlalu Panjang (> 30 Baris)**
   - Menggunakan node matching pada `function_definition` (Python) serta `function_declaration` dan `method_definition` (JavaScript).
   - Menghitung rentang baris nyata dari `start_point` hingga `end_point`.
   - Melaporkan nama fungsi dan jumlah barisnya jika melebihi 30 baris (indikasi pelanggaran prinsip *Single Responsibility*).

3. **Pendeteksi Berkas dengan Error Sintaks (CST Error Recovery)**
   - Memanfaatkan properti `tree.root_node.has_error` tanpa perlu menjalankan atau mengkompilasi kode.
   - Menelusuri secara rekursif untuk menemukan node pertama yang mengalami `ERROR` atau `MISSING`.
   - Melaporkan lokasi persis baris dan kolom yang rusak.

4. **[Pengayaan] Dukungan Multi-bahasa (Python & JavaScript)**
   - Mendukung parsing dan analisis berkas JavaScript (`.js`) menggunakan grammar `tree-sitter-javascript`.

5. **Optimasi Pengabaian Direktori (Skip Ignored Folders)**
   - Otomatis mengabaikan folder dependensi dan metadata seperti `venv`, `node_modules`, `.git`, `__pycache__`, dan sejenisnya sehingga eksekusi tetap sangat cepat pada repositori besar.

---

## 2. Instalasi Dependensi

Pastikan Python 3.10+ telah terpasang. Pasang pustaka Tree-sitter dan grammar bahasa yang dibutuhkan:

```bash
pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

---

## 3. Cara Menjalankan

Jalankan perintah berikut di terminal:

```bash
python cek.py <jalur_ke_folder>
```

### Contoh Penggunaan

Memeriksa folder suite pengujian bawaan (`uji/`):
```bash
python cek.py uji
```

Memeriksa repositori atau folder proyek lain:
```bash
python cek.py ../tugas1-3
```

---

## 4. Contoh Output Eksekusi

```text
======================================================================
LAPORAN ANALISIS KODE SUMBER (TREE-SITTER LINTEK)
Direktori Target: D:\project\cek\uji
======================================================================

[FILE] test_error.py (Python)
  [SYNTAX ERROR] Baris 2:0: Terdeteksi node bermasalah 'ERROR'

[FILE] test_js.js (JavaScript)
  [TODO/FIXME] Baris 1: // TODO: hubungkan dengan socket io
  [TODO/FIXME] Baris 4: // FIXME: hitung pajak PPN 11%
  [FUNGSI PANJANG] Baris 12: Fungsi 'renderHalamanDashboard' memiliki 33 baris (> 30 baris)

[FILE] test_panjang.py (Python)
  [FUNGSI PANJANG] Baris 5: Fungsi 'proses_laporan_bulanan' memiliki 44 baris (> 30 baris)

[FILE] test_todo.py (Python)
  [TODO/FIXME] Baris 2: # TODO: implementasi validasi token JWT
  [TODO/FIXME] Baris 5: # FIXME: atasi potensi race condition saat update saldo

======================================================================
RINGKASAN STATISTIK PEMERIKSAAN:
  Total Berkas Dianalisis        : 4
  Total Komentar TODO / FIXME    : 4
  Total Fungsi Terlalu Panjang   : 2
  Total Berkas dengan Error CST  : 1
======================================================================
```

---

## 5. Mengapa Tree-sitter Lebih Unggul Dibandingkan Regex?

| Aspek | Pendekatan Regex Tradisional | Pendekatan Tree-sitter (Tool Ini) |
| --- | --- | --- |
| **Komentar TODO** | Sering keliru mencocokkan string di dalam variabel, misalnya `url = "http://api/TODO"` dianggap TODO. | Hanya mencocokkan node yang bertipe `comment` di syntax tree. |
| **Panjang Fungsi** | Sulit menentukan akhir sebuah fungsi karena blok kurung kurawal atau indentasi bersarang. | Pasti dan akurat melalui `start_point` dan `end_point` dari node fungsi. |
| **Pendeteksian Error** | Tidak dapat memvalidasi sintaks kode tanpa interpreter penuh. | Deterministik dan instan mendeteksi status `has_error` tanpa eksekusi kode. |
| **Kecepatan** | Parsing berulang lambat pada ribuan baris. | Sangat cepat (ribuan berkas per detik) berbasis parser C. |
