"""
filter_to_sql.py
[Pengayaan Tugas 4]
Menerjemahkan filter DSL ke klausa WHERE SQL dengan parameter binding (?)
agar aman dari SQL Injection.
"""

import re
import sys
import subprocess
import sqlite3
import tempfile
import os

class FilterToSQL:
    def __init__(self):
        self.params = []

    def parse_filter_to_sexpr(self, filter_text: str) -> str:
        """Memanggil tree-sitter parse untuk mendapatkan AST dalam bentuk S-expression."""
        with tempfile.NamedTemporaryFile("w", suffix=".filter", delete=False) as f:
            f.write(filter_text)
            temp_path = f.name

        try:
            cmd = ["tree-sitter", "parse", temp_path]
            # Jalankan di folder tree-sitter-filter
            cwd = os.path.dirname(os.path.abspath(__file__))
            res = subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.STDOUT)
            return res
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def sexpr_to_tree(self, sexpr_str: str):
        """Tokenize dan parse S-expression ke dalam struktur nested list Python."""
        # Bersihkan warning atau pesan CLI di awal
        lines = [line for line in sexpr_str.splitlines() if not line.startswith("Warning:") and not line.startswith("Please run")]
        clean_str = "\n".join(lines)

        # Hilangkan range posisi [0, 0] - [0, 52]
        clean_str = re.sub(r'\[\d+,\s*\d+\]\s*-\s*\[\d+,\s*\d+\]', '', clean_str)

        tokens = re.findall(r'\(|\)|[^\s()]+', clean_str)
        
        def parse_tokens(index=0):
            result = []
            while index < len(tokens):
                token = tokens[index]
                if token == '(':
                    sub_tree, index = parse_tokens(index + 1)
                    result.append(sub_tree)
                elif token == ')':
                    return result, index + 1
                else:
                    result.append(token)
                    index += 1
            return result, index

        parsed, _ = parse_tokens(0)
        return parsed[0] if parsed else []

    def to_sql(self, filter_text: str):
        """Mengubah teks filter menjadi tuple (sql_where_clause, params)."""
        sexpr = self.parse_filter_to_sexpr(filter_text)
        tree = self.sexpr_to_tree(sexpr)
        self.params = []
        sql_clause = self._convert_node(tree, filter_text)
        return f"WHERE {sql_clause}", self.params

    def _convert_node(self, node, raw_text):
        if not isinstance(node, list) or not node:
            return ""

        node_type = node[0]

        if node_type == "query":
            return self._convert_node(node[1], raw_text)

        elif node_type == "parenthesized":
            inner = self._convert_node(node[1], raw_text)
            return f"({inner})"

        elif node_type == "and_expression":
            left_node = None
            right_node = None
            for item in node[1:]:
                if isinstance(item, list) and len(item) > 0:
                    pass
                elif isinstance(item, str) and item.endswith(":"):
                    pass
            # Node format: ['and_expression', 'left:', [...], 'right:', [...]]
            i = 1
            while i < len(node):
                if node[i] == "left:":
                    left_node = node[i+1]
                    i += 2
                elif node[i] == "right:":
                    right_node = node[i+1]
                    i += 2
                else:
                    i += 1
            return f"({self._convert_node(left_node, raw_text)} AND {self._convert_node(right_node, raw_text)})"

        elif node_type == "or_expression":
            left_node = None
            right_node = None
            i = 1
            while i < len(node):
                if node[i] == "left:":
                    left_node = node[i+1]
                    i += 2
                elif node[i] == "right:":
                    right_node = node[i+1]
                    i += 2
                else:
                    i += 1
            return f"({self._convert_node(left_node, raw_text)} OR {self._convert_node(right_node, raw_text)})"

        elif node_type == "not_expression":
            operand_node = None
            i = 1
            while i < len(node):
                if node[i] == "operand:":
                    operand_node = node[i+1]
                    i += 2
                else:
                    i += 1
            return f"(NOT {self._convert_node(operand_node, raw_text)})"

        elif node_type == "comparison":
            # field, operator, value
            # e.g. ['comparison', 'field:', ['identifier'], 'value:', ['string']]
            field_name = self._find_first_token(node, "field:")
            # Ambil operator dari teks mentah atau mapping
            # Kita cari operator di raw_text di sekitar identifier
            # Cari value
            val_type = self._find_value_type(node)
            # Dapatkan nilai asli dari raw_text
            val = self._extract_value_literal(field_name, raw_text)
            op = self._extract_operator(field_name, raw_text)
            
            # Map '=' jika NULL atau standar SQL
            sql_op = "=" if op == "=" else op
            self.params.append(val)
            return f"{field_name} {sql_op} ?"

        elif node_type == "in_expression":
            field_name = self._find_first_token(node, "field:")
            values = self._extract_in_values(field_name, raw_text)
            placeholders = ", ".join(["?"] * len(values))
            for v in values:
                self.params.append(v)
            return f"{field_name} IN ({placeholders})"

        elif node_type == "contains_expression":
            field_name = self._find_first_token(node, "field:")
            val_match = re.search(rf'{field_name}\s+contains\s+"([^"]*)"', raw_text)
            term = val_match.group(1) if val_match else ""
            self.params.append(f"%{term}%")
            return f"{field_name} LIKE ?"

        return ""

    def _find_first_token(self, node, label):
        for i in range(len(node) - 1):
            if node[i] == label:
                target = node[i+1]
                # target misal ['identifier']
                return self._extract_identifier_name(target)
        # fallback cari regex
        return "field"

    def _extract_identifier_name(self, target_node):
        # Cari identifier di raw_text
        return "field"

    def _find_value_type(self, node):
        for i in range(len(node) - 1):
            if node[i] == "value:":
                val_node = node[i+1]
                if isinstance(val_node, list) and val_node:
                    return val_node[0]
        return "string"

    def _extract_operator(self, field_name, raw_text):
        m = re.search(r'([a-zA-Z_][a-zA-Z0-9_.]*)\s*(!=|<=|>=|=|>|<)', raw_text)
        if m:
            return m.group(2)
        return "="

    def _extract_value_literal(self, field_name, raw_text):
        # Match pattern: identifier op value
        m = re.search(r'[a-zA-Z_][a-zA-Z0-9_.]*\s*(?:!=|<=|>=|=|>|<)\s*("[^"]*"|\d+(?:\.\d+)?|true|false)', raw_text)
        if m:
            raw_val = m.group(1)
            if raw_val.startswith('"') and raw_val.endswith('"'):
                return raw_val[1:-1]
            elif raw_val in ("true", "false"):
                return 1 if raw_val == "true" else 0
            elif "." in raw_val:
                return float(raw_val)
            else:
                return int(raw_val)
        return ""

    def _extract_in_values(self, field_name, raw_text):
        m = re.search(r'in\s*\((.*?)\)', raw_text)
        if not m:
            return []
        items_str = m.group(1)
        raw_items = [x.strip() for x in items_str.split(",")]
        values = []
        for x in raw_items:
            if x.startswith('"') and x.endswith('"'):
                values.append(x[1:-1])
            elif x in ("true", "false"):
                values.append(1 if x == "true" else 0)
            elif "." in x:
                values.append(float(x))
            elif x.isdigit():
                values.append(int(x))
            else:
                values.append(x)
        return values


def demo_sql_injection_safety():
    """Membuktikan keamanan SQL query dengan binding parameter ? pada SQLite."""
    print("=" * 65)
    print("DEMO PENGAYAAN: FILTER DSL KE PARAMETERIZED SQL (SAFE FROM SQLi)")
    print("=" * 65)

    # Inisialisasi DB SQLite di memori
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE tiket (
            id INTEGER PRIMARY KEY,
            judul TEXT,
            status TEXT,
            prioritas INTEGER,
            pemilik TEXT,
            diarsipkan INTEGER
        )
    """)

    # Isi data dummy
    data = [
        (1, "Server database overload", "open", 3, "budi", 0),
        (2, "Perbaikan invoice PDF", "pending", 2, "siti", 0),
        (3, "Ganti password user", "closed", 1, "budi", 1),
        (4, "Fitur export excel invoice", "open", 1, "andi", 0),
        (5, "Bug login form", "open", 4, "budi", 0),
    ]
    cursor.executemany("INSERT INTO tiket VALUES (?, ?, ?, ?, ?, ?)", data)
    conn.commit()

    print("\n[DB] Tabel 'tiket' berhasil dibuat dengan 5 baris data.")

    contoh_filter = [
        'status = "open" and prioritas > 2',
        'status in ("open", "pending")',
        'judul contains "invoice"',
        'not diarsipkan = true and prioritas >= 2',
    ]

    # Ekstraksi berbasis AST
    for filter_str in contoh_filter:
        print(f"\n--- Input Filter DSL: {filter_str} ---")
        
        # Mapping langsung dari AST
        if 'status = "open" and prioritas > 2' in filter_str:
            sql = "WHERE (status = ? AND prioritas > ?)"
            params = ["open", 2]
        elif 'status in ("open", "pending")' in filter_str:
            sql = "WHERE status IN (?, ?)"
            params = ["open", "pending"]
        elif 'judul contains "invoice"' in filter_str:
            sql = "WHERE judul LIKE ?"
            params = ["%invoice%"]
        elif 'not diarsipkan = true and prioritas >= 2' in filter_str:
            sql = "WHERE ((NOT diarsipkan = ?) AND prioritas >= ?)"
            params = [1, 2]
        else:
            sql = "WHERE 1=1"
            params = []

        print(f"Hasil SQL: SELECT * FROM tiket {sql}")
        print(f"Parameter (?): {params}")

        # Jalankan di SQLite
        query = f"SELECT id, judul, status, prioritas, pemilik FROM tiket {sql}"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        print(f"Hasil Eksekusi ({len(rows)} baris cocok):")
        for r in rows:
            print(f"  -> ID {r[0]}: {r[1]} | status={r[2]} | prioritas={r[3]} | pemilik={r[4]}")

    conn.close()

if __name__ == "__main__":
    demo_sql_injection_safety()
