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

garis("2. IDENTIFIKASI NODE BERNAMA VS NODE ANONIM")
print("Contoh pada Potongan 1 (Fungsi):")
tree_fungsi = parser.parse(potongan_kode["Potongan 1 (Fungsi)"])
func_node = tree_fungsi.root_node.children[0]

print(f"\nNode tingkat atas: {func_node.type} ({'bernama' if func_node.is_named else 'anonim'})")
print("Semua children langsung dari function_definition:")
for i, c in enumerate(func_node.children):
    kategori = "BERNAMA" if c.is_named else "ANONIM (tersembunyi)"
    field = func_node.field_name_for_child(i)
    field_str = f" [field: {field}]" if field else ""
    teks = repr(c.text.decode())
    print(f"  - Child {i}: {c.type:<22} -> {kategori:<20} {field_str:<16} | Teks: {teks}")

params_node = func_node.child_by_field_name("parameters")
print("\nChildren di dalam node 'parameters':")
for i, c in enumerate(params_node.children):
    kategori = "BERNAMA" if c.is_named else "ANONIM (tersembunyi)"
    teks = repr(c.text.decode())
    print(f"  - Child {i}: {c.type:<22} -> {kategori:<20} | Teks: {teks}")

garis("3. ERROR RECOVERY: RUSAK KODE SECARA SENGAJA")
kode_rusak_tanpa_titik_dua = b'''def sapa(nama)
    return "Halo " + nama
'''
print("\nKasus A: Menghapus tanda titik dua ':' pada def sapa(nama):")
print("Kode:")
print(kode_rusak_tanpa_titik_dua.decode().strip())
tree_rusak_a = parser.parse(kode_rusak_tanpa_titik_dua)
print("\nPohon hasil parse (perhatikan node ERROR / MISSING):")
print(tree_rusak_a.root_node)

kode_rusak_tanpa_tutup_kurung = b'''def sapa(nama:
    return "Halo"
'''
print("\nKasus B: Menghapus tanda tutup kurung ')' pada def sapa(nama:")
print("Kode:")
print(kode_rusak_tanpa_tutup_kurung.decode().strip())
tree_rusak_b = parser.parse(kode_rusak_tanpa_tutup_kurung)
print("\nPohon hasil parse (perhatikan node ERROR / MISSING):")
print(tree_rusak_b.root_node)

garis("4. PERBEDAAN 'children' DAN 'named_children'")
print(f"Pada node function_definition:")
print(f"  - Jumlah total node di children       : {len(func_node.children)}")
print(f"    Tipe: {[c.type for c in func_node.children]}")
print(f"  - Jumlah total node di named_children : {len(func_node.named_children)}")
print(f"    Tipe: {[c.type for c in func_node.named_children]}")
print("""
Penjelasan:
- `children`: Mengembalikan semua token konkret dari Concrete Syntax Tree (CST),
  termasuk node anonim seperti keyword 'def', operator, tanda kurung '(', ')', dan titik dua ':'.
- `named_children`: Hanya mengembalikan node yang berasal dari named rule di grammar tree-sitter,
  yaitu node yang memiliki identitas semantik/struktural seperti 'identifier', 'parameters', dan 'block'.
""")
