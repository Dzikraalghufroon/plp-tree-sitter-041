"""
Modul Uji Query Tree-sitter (Tugas 3)
Berisi fungsi dengan berbagai parameter, pemanggilan print, import, dan docstring
untuk diverifikasi secara manual.
"""

import os
import math
from datetime import datetime
from collections import defaultdict
import json as format_json

def fungsi_tanpa_param():
    """Docstring: fungsi ini tidak menerima parameter sama sekali."""
    x = 10
    print("Menjalankan fungsi tanpa param:", x)
    return x

def hitung_luas_persegi(sisi):
    """Docstring: menghitung luas persegi."""
    print(f"Menghitung sisi: {sisi}")
    return sisi * sisi

def hitung_volume_balok(panjang, lebar, tinggi):
    """Docstring: menghitung volume balok dari 3 parameter."""
    hasil = panjang * lebar * tinggi
    print(f"Volume = {hasil}")
    return hasil

def fungsi_tanpa_docstring(a, b):
    # Hanya komentar biasa, bukan docstring
    return a + b

def main():
    print("Mulai pengujian...")
    p = fungsi_tanpa_param()
    l = hitung_luas_persegi(5)
    v = hitung_volume_balok(2, 3, 4)
    print("Selesai pengujian.")

if __name__ == "__main__":
    main()
