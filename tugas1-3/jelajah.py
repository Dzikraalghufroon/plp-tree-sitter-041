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


def jelajah_cursor(tree):
    """
    [Pengayaan] Menelusuri AST menggunakan TreeCursor (efisien memori).
    Menghasilkan urutan dan format output yang identik dengan versi rekursif.
    """
    cursor = tree.walk()
    named_depths = [0]
    visited_children = False

    while True:
        if not visited_children:
            curr_node = cursor.node
            field = cursor.field_name
            current_depth = named_depths[-1]

            if curr_node.is_named:
                label = f"{field}: " if field else ""
                baris, kolom = curr_node.start_point
                print("  " * current_depth + f"{label}{curr_node.type} [{baris + 1}:{kolom}]")

            if cursor.goto_first_child():
                new_depth = current_depth + 1 if curr_node.is_named else current_depth
                named_depths.append(new_depth)
                visited_children = False
                continue

        if cursor.goto_next_sibling():
            visited_children = False
            continue

        if cursor.goto_parent():
            named_depths.pop()
            visited_children = True
            continue

        break


def main():
    if len(sys.argv) < 2:
        print("Penggunaan: python jelajah.py <file.py> [--cursor | --compare]")
        sys.exit(1)

    file_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else ""

    with open(file_path, "rb") as f:
        tree = parser.parse(f.read())

    if mode == "--cursor":
        jelajah_cursor(tree)
    elif mode == "--compare":
        print("=== OUTPUT VERSI REKURSIF ===")
        jelajah_rekursif(tree.root_node)
        print("\n=== OUTPUT VERSI TREECURSOR ===")
        jelajah_cursor(tree)
    else:
        jelajah_rekursif(tree.root_node)


if __name__ == "__main__":
    main()
