"""
Modul Manajemen Antrean Pesanan (Order Queue Management)
Contoh berkas Python nyata dengan struktur kelas, method, fungsi pembantu,
kondisi, dan penanganan kesalahan untuk pengujian AST Tree-sitter.
"""

import os
import sys
import time
from typing import List, Dict, Optional
from datetime import datetime

# Konstanta status pesanan
STATUS_PENDING = "PENDING"
STATUS_PROCESSING = "PROCESSING"
STATUS_COMPLETED = "COMPLETED"
STATUS_CANCELLED = "CANCELLED"


class ItemPesanan:
    """Mewakili satu item di dalam pesanan."""

    def __init__(self, kode_produk: str, nama_produk: str, harga: float, kuantitas: int = 1):
        self.kode_produk = kode_produk
        self.nama_produk = nama_produk
        self.harga = float(harga)
        self.kuantitas = int(kuantitas)

    def subtotal(self) -> float:
        """Menghitung subtotal harga item."""
        return self.harga * self.kuantitas

    def to_dict(self) -> Dict[str, any]:
        """Konversi objek item ke format dictionary."""
        return {
            "kode": self.kode_produk,
            "nama": self.nama_produk,
            "harga": self.harga,
            "kuantitas": self.kuantitas,
            "subtotal": self.subtotal(),
        }


class Pesanan:
    """Mewakili pesanan pelanggan beserta daftar item."""

    def __init__(self, id_pesanan: str, pelanggan: str):
        self.id_pesanan = id_pesanan
        self.pelanggan = pelanggan
        self.daftar_item: List[ItemPesanan] = []
        self.status: str = STATUS_PENDING
        self.dibuat_pada: datetime = datetime.now()

    def tambah_item(self, item: ItemPesanan) -> None:
        """Menambahkan item ke dalam pesanan."""
        if self.status != STATUS_PENDING:
            raise ValueError(f"Pesanan {self.id_pesanan} sudah diproses, tidak bisa menambah item.")
        self.daftar_item.append(item)
        print(f"[INFO] Item {item.nama_produk} berhasil ditambahkan ke pesanan {self.id_pesanan}.")

    def hitung_total(self, diskon_persen: float = 0.0) -> float:
        """Menghitung total keseluruhan nilai pesanan setelah diskon."""
        total_kotor = sum(item.subtotal() for item in self.daftar_item)
        if diskon_persen > 0:
            potongan = total_kotor * (diskon_persen / 100.0)
            return max(0.0, total_kotor - potongan)
        return total_kotor

    def ubah_status(self, status_baru: str) -> None:
        """Memperbarui status pesanan."""
        status_valid = [STATUS_PENDING, STATUS_PROCESSING, STATUS_COMPLETED, STATUS_CANCELLED]
        if status_baru not in status_valid:
            raise ValueError(f"Status tidak valid: {status_baru}")
        self.status = status_baru
        print(f"[UPDATE] Status pesanan {self.id_pesanan} diubah menjadi {self.status}.")


class PengelolaAntrean:
    """Mengelola antrean proses banyak pesanan."""

    def __init__(self, nama_toko: str):
        self.nama_toko = nama_toko
        self.antrean: List[Pesanan] = []
        self.riwayat_selesai: List[Pesanan] = []

    def masuk_antrean(self, pesanan: Pesanan) -> int:
        """Memasukkan pesanan baru ke antrean."""
        self.antrean.append(pesanan)
        print(f"[ANTREAN] Pesanan {pesanan.id_pesanan} milik {pesanan.pelanggan} telah masuk.")
        return len(self.antrean)

    def proses_berikutnya(self) -> Optional[Pesanan]:
        """Memproses pesanan terdepan di antrean."""
        if not self.antrean:
            print("[INFO] Antrean kosong.")
            return None

        pesanan = self.antrean.pop(0)
        pesanan.ubah_status(STATUS_PROCESSING)
        print(f"[PROSES] Sedang memproses pesanan {pesanan.id_pesanan}...")
        
        # Simulasi kerja
        pesanan.ubah_status(STATUS_COMPLETED)
        self.riwayat_selesai.append(pesanan)
        return pesanan

    def tampilkan_ringkasan(self) -> None:
        """Mencetak ringkasan antrean ke konsol."""
        print(f"=== Ringkasan Toko {self.nama_toko} ===")
        print(f"Sisa antrean: {len(self.antrean)}")
        print(f"Selesai diproses: {len(self.riwayat_selesai)}")


def inisialisasi_demo():
    """Fungsi pembantu untuk menjalankan skenario uji."""
    pengelola = PengelolaAntrean("Elektronik Maju Jaya")
    
    p1 = Pesanan("ORD-001", "Budi Santoso")
    p1.tambah_item(ItemPesanan("PRD-1", "Mouse Nirkabel", 150000, 2))
    p1.tambah_item(ItemPesanan("PRD-2", "Keyboard Mekanikal", 450000, 1))

    p2 = Pesanan("ORD-002", "Siti Rahma")
    p2.tambah_item(ItemPesanan("PRD-3", "Monitor 24 Inci", 1850000, 1))

    pengelola.masuk_antrean(p1)
    pengelola.masuk_antrean(p2)

    pengelola.proses_berikutnya()
    pengelola.tampilkan_ringkasan()


if __name__ == "__main__":
    inisialisasi_demo()
