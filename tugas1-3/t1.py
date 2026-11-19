import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def garis(judul=""):
    print("\n" + "=" * 60)
    if judul:
        print(f" {judul} ".center(60, "="))
        print("=" * 60)

# ============================================================
# TUGAS 1: MEMBACA POHON SINTAKS (SYNTAX TREE)
# ============================================================

potongan_kode = {
    "Potongan 1 (Fungsi)": b'''def hitung_diskon(harga, persen):
    return harga * (persen / 100)
''',
    "Potongan 2 (If/Else)": b'''if nilai >= 75:
    status = "lulus"
else:
    status = "remedial"
''',
    "Potongan 3 (Kelas dengan 1 method)": b'''class Rekening:
    def setor(self, jumlah):
        self.saldo += jumlah
'''
}

garis("1. PARSE 3 POTONGAN KODE & CETAK ROOT NODE")
for nama, kode in potongan_kode.items():
    print(f"\n--- {nama} ---")
    print("Kode Sumber:")
    print(kode.decode().strip())
    tree = parser.parse(kode)
    print("\nPohon Sintaks (root_node):")
    print(tree.root_node)
