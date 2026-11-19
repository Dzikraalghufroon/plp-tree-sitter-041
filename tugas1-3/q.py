import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

def main():
    if len(sys.argv) < 3:
        print("Penggunaan: python q.py <file.py> <pola.scm>")
        sys.exit(1)

    file_kode = sys.argv[1]
    file_pola = sys.argv[2]

    with open(file_kode, "rb") as f:
        kode = f.read()

    with open(file_pola, "r", encoding="utf-8") as f:
        pola = f.read()

    tree = parser.parse(kode)
    query = Query(PY, pola)
    cursor = QueryCursor(query)

    print(f"Menjalankan query '{file_pola}' pada berkas '{file_kode}':\n")

    # Deteksi tipe query berdasarkan isi pola untuk formatting yang rapi
    if "@params" in pola and "@nama" in pola:
        print("--- DAFTAR FUNGSI DAN JUMLAH PARAMETER ---")
        matches = cursor.matches(tree.root_node)
        total = 0
        for _, cap in matches:
            if "nama" in cap and "params" in cap:
                nama = cap["nama"][0].text.decode()
                baris = cap["nama"][0].start_point[0] + 1
                jumlah_param = cap["params"][0].named_child_count
                total += 1
                print(f"[{total}] Fungsi: {nama:<25} | Baris: {baris:<4} | Jumlah Parameter: {jumlah_param}")
        print(f"\nTotal fungsi ditemukan: {total}")

    elif "@fn" in pola and "@args" in pola:
        print("--- DAFTAR PEMANGGILAN PRINT(...) ---")
        matches = cursor.matches(tree.root_node)
        total = 0
        for _, cap in matches:
            if "fn" in cap and "args" in cap:
                baris = cap["fn"][0].start_point[0] + 1
                args_text = cap["args"][0].text.decode().replace("\n", " ").strip()
                total += 1
                print(f"[{total}] Baris {baris:<4}: print{args_text}")
        print(f"\nTotal pemanggilan print ditemukan: {total}")

    elif "@modul" in pola:
        print("--- DAFTAR MODUL IMPORT ---")
        matches = cursor.matches(tree.root_node)
        total = 0
        for _, cap in matches:
            for n in cap.get("modul", []):
                baris = n.start_point[0] + 1
                nama_modul = n.text.decode()
                total += 1
                print(f"[{total}] Modul: {nama_modul:<25} | Baris: {baris}")
        print(f"\nTotal modul di-import: {total}")

    elif "@docstring" in pola and "@nama" in pola:
        print("--- DAFTAR DOCSTRING FUNGSI ---")
        matches = cursor.matches(tree.root_node)
        total = 0
        for _, cap in matches:
            nama = cap["nama"][0].text.decode()
            baris = cap["nama"][0].start_point[0] + 1
            doc = cap["docstring"][0].text.decode().strip()
            total += 1
            print(f"[{total}] Fungsi: {nama:<22} (baris {baris})")
            print(f"     Docstring: {doc}")
        print(f"\nTotal fungsi ber-docstring: {total}")

    else:
        # Fallback: cetak captures generik
        captures = cursor.captures(tree.root_node)
        total = 0
        for nama, nodes in captures.items():
            for n in nodes:
                total += 1
                print(f"@{nama:<15} baris {n.start_point[0] + 1:<4}: {n.text.decode().strip()}")
        print(f"\nTotal capture: {total}")


if __name__ == "__main__":
    main()
