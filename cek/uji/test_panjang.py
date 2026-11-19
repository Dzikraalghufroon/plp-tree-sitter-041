def fungsi_pendek(x, y):
    """Fungsi pendek yang tidak melanggar aturan 30 baris."""
    return x + y

def proses_laporan_bulanan(tahun, bulan):
    """
    Fungsi panjang dengan lebih dari 30 baris kode
    untuk menguji fitur deteksi fungsi terlalu panjang.
    """
    print(f"Mulai pemrosesan laporan periode {bulan}/{tahun}")
    total_pendapatan = 0
    total_pengeluaran = 0
    daftar_transaksi = []

    # Baris 1
    total_pendapatan += 1000
    # Baris 2
    total_pengeluaran += 400
    # Baris 3
    daftar_transaksi.append("Transaksi 1")
    # Baris 4
    total_pendapatan += 2500
    # Baris 5
    total_pengeluaran += 1200
    # Baris 6
    daftar_transaksi.append("Transaksi 2")
    # Baris 7
    total_pendapatan += 3000
    # Baris 8
    total_pengeluaran += 900
    # Baris 9
    daftar_transaksi.append("Transaksi 3")
    # Baris 10
    total_pendapatan += 1500
    # Baris 11
    total_pengeluaran += 300
    # Baris 12
    daftar_transaksi.append("Transaksi 4")
    # Baris 13
    total_pendapatan += 4000
    # Baris 14
    total_pengeluaran += 2000
    # Baris 15
    daftar_transaksi.append("Transaksi 5")
    # Baris 16
    laba_bersih = total_pendapatan - total_pengeluaran
    print(f"Laba bersih: {laba_bersih}")
    return laba_bersih
