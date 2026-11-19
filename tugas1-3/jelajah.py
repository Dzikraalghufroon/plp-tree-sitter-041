import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY = Language(tspython.language())
parser = Parser(PY)

def jelajah_rekursif(node, kedalaman=0, field=None):
    """
    Menelusuri AST secara rekursif.
    Hanya mencetak named node dengan indentasi 2 spasi per tingkat kedalaman,
    disertai field name (jika ada), tipe node, dan posisi [baris:kolom] (1-indexed untuk baris).
    """
    baris, kolom = node.start_point
    label = f"{field}: " if field else ""
    print("  " * kedalaman + f"{label}{node.type} [{baris + 1}:{kolom}]")

    for i, child in enumerate(node.children):
        if not child.is_named:
            continue
        nama_field = node.field_name_for_child(i)
        jelajah_rekursif(child, kedalaman + 1, nama_field)
