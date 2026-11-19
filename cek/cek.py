"""
cek.py
Mini Proyek: Pendeteksi TODO/FIXME, Fungsi Terlalu Panjang (>30 baris),
dan Berkas dengan Error Sintaks menggunakan Tree-sitter.
Mendukung berkas Python (.py) dan berkas JavaScript (.js) [Pengayaan].
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser, Query, QueryCursor

# Setup bahasa Python
PY_LANG = Language(tspython.language())
parser_py = Parser(PY_LANG)

# Setup bahasa JavaScript [Pengayaan]
JS_LANG = Language(tsjavascript.language())
parser_js = Parser(JS_LANG)

# Query untuk Python
Q_TODO_PY = Query(PY_LANG, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNC_PY = Query(PY_LANG, '(function_definition name: (identifier) @nama) @fungsi')

# Query untuk JavaScript [Pengayaan]
Q_TODO_JS = Query(JS_LANG, '((comment) @c (#match? @c "TODO|FIXME"))')
Q_FUNC_JS = Query(JS_LANG, '''
[
  (function_declaration name: (identifier) @nama) @fungsi
  (method_definition name: (property_identifier) @nama) @fungsi
]
''')

# Folder yang harus dilewati
IGNORED_DIRS = {
    "venv", ".venv", "env", ".env", "node_modules", ".git", "__pycache__",
    ".gemini", "brain", ".system_generated", "build", "dist"
}

def cari_node_error_pertama(node):
    """Mencari node pertama yang berstatus error atau missing secara rekursif (preorder)."""
    if node.is_error or node.is_missing:
        return node
    for child in node.children:
        err = cari_node_error_pertama(child)
        if err:
            return err
    return None

def cek_file_python(path: Path) -> dict:
    """Memeriksa satu berkas Python."""
    try:
        content = path.read_bytes()
    except Exception as e:
        return {"error_baca": str(e)}

    tree = parser_py.parse(content)
    hasil = {
        "todo": [],
        "fungsi_panjang": [],
        "syntax_error": None
    }

    # Fitur 1: Deteksi TODO dan FIXME
    try:
        captures = QueryCursor(Q_TODO_PY).captures(tree.root_node).get("c", [])
        for node in captures:
            teks = node.text.decode(errors="replace").strip()
            baris = node.start_point[0] + 1
            hasil["todo"].append((baris, teks))
    except Exception as e:
        pass

    # Fitur 2: Deteksi fungsi > 30 baris
    try:
        matches = QueryCursor(Q_FUNC_PY).matches(tree.root_node)
        for _, cap in matches:
            if "fungsi" in cap and "nama" in cap:
                fn_node = cap["fungsi"][0]
                fn_name = cap["nama"][0].text.decode(errors="replace")
                start_row = fn_node.start_point[0] + 1
                end_row = fn_node.end_point[0] + 1
                jumlah_baris = end_row - start_row + 1
                if jumlah_baris > 30:
                    hasil["fungsi_panjang"].append((start_row, fn_name, jumlah_baris))
    except Exception as e:
        pass

    # Fitur 3: Deteksi file yang pohonnya error
    if tree.root_node.has_error:
        err_node = cari_node_error_pertama(tree.root_node)
        if err_node:
            b, k = err_node.start_point
            tipe = "MISSING" if err_node.is_missing else ("ERROR" if err_node.is_error else err_node.type)
            hasil["syntax_error"] = (b + 1, k, tipe)
        else:
            hasil["syntax_error"] = (1, 0, "ERROR")

    return hasil

def cek_file_javascript(path: Path) -> dict:
    """Memeriksa satu berkas JavaScript [Pengayaan]."""
    try:
        content = path.read_bytes()
    except Exception as e:
        return {"error_baca": str(e)}

    tree = parser_js.parse(content)
    hasil = {
        "todo": [],
        "fungsi_panjang": [],
        "syntax_error": None
    }

    # Fitur 1: TODO & FIXME
    try:
        captures = QueryCursor(Q_TODO_JS).captures(tree.root_node).get("c", [])
        for node in captures:
            teks = node.text.decode(errors="replace").strip()
            baris = node.start_point[0] + 1
            hasil["todo"].append((baris, teks))
    except Exception:
        pass

    # Fitur 2: Fungsi > 30 baris
    try:
        matches = QueryCursor(Q_FUNC_JS).matches(tree.root_node)
        for _, cap in matches:
            if "fungsi" in cap and "nama" in cap:
                fn_node = cap["fungsi"][0]
                fn_name = cap["nama"][0].text.decode(errors="replace")
                start_row = fn_node.start_point[0] + 1
                end_row = fn_node.end_point[0] + 1
                jumlah_baris = end_row - start_row + 1
                if jumlah_baris > 30:
                    hasil["fungsi_panjang"].append((start_row, fn_name, jumlah_baris))
    except Exception:
        pass

    # Fitur 3: Syntax error
    if tree.root_node.has_error:
        err_node = cari_node_error_pertama(tree.root_node)
        if err_node:
            b, k = err_node.start_point
            tipe = "MISSING" if err_node.is_missing else ("ERROR" if err_node.is_error else err_node.type)
            hasil["syntax_error"] = (b + 1, k, tipe)
        else:
            hasil["syntax_error"] = (1, 0, "ERROR")

    return hasil

def main():
    if len(sys.argv) < 2:
        print("Penggunaan: python cek.py <folder>")
        sys.exit(1)

    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Error: Folder '{target_dir}' tidak ditemukan.")
        sys.exit(1)

    print("=" * 70)
    print(f"LAPORAN ANALISIS KODE SUMBER (TREE-SITTER LINTEK)")
    print(f"Direktori Target: {target_dir.resolve()}")
    print("=" * 70)

    total_files = 0
    total_todo = 0
    total_fungsi_panjang = 0
    total_error = 0

    daftar_laporan = []

    # Kumpulkan semua file .py dan .js
    for path in target_dir.rglob("*"):
        if not path.is_file():
            continue
        # Periksa apakah berada di folder yang diabaikan
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        ext = path.suffix.lower()
        if ext == ".py":
            total_files += 1
            res = cek_file_python(path)
            daftar_laporan.append((path, "Python", res))
        elif ext == ".js":
            total_files += 1
            res = cek_file_javascript(path)
            daftar_laporan.append((path, "JavaScript", res))

    # Tampilkan temuan
    for path, bahasa, res in daftar_laporan:
        todo_list = res.get("todo", [])
        fn_list = res.get("fungsi_panjang", [])
        err = res.get("syntax_error")

        if not todo_list and not fn_list and not err:
            continue

        rel_path = path.relative_to(target_dir) if path.is_relative_to(target_dir) else path
        print(f"\n[FILE] {rel_path} ({bahasa})")

        # 1. TODO
        for b, teks in todo_list:
            total_todo += 1
            print(f"  [TODO/FIXME] Baris {b}: {teks}")

        # 2. Fungsi Panjang
        for b, nama, baris_total in fn_list:
            total_fungsi_panjang += 1
            print(f"  [FUNGSI PANJANG] Baris {b}: Fungsi '{nama}' memiliki {baris_total} baris (> 30 baris)")

        # 3. Syntax error
        if err:
            total_error += 1
            b, k, tipe = err
            print(f"  [SYNTAX ERROR] Baris {b}:{k}: Terdeteksi node bermasalah '{tipe}'")

    print("\n" + "=" * 70)
    print("RINGKASAN STATISTIK PEMERIKSAAN:")
    print(f"  Total Berkas Dianalisis        : {total_files}")
    print(f"  Total Komentar TODO / FIXME    : {total_todo}")
    print(f"  Total Fungsi Terlalu Panjang   : {total_fungsi_panjang}")
    print(f"  Total Berkas dengan Error CST  : {total_error}")
    print("=" * 70)

if __name__ == "__main__":
    main()
