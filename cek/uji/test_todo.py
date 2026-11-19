def proses_transaksi(data):
    # TODO: implementasi validasi token JWT
    if not data:
        return None
    # FIXME: atasi potensi race condition saat update saldo
    saldo = data.get("saldo", 0)
    print("Memproses transaksi saldo:", saldo)
    # Catatan: komentar biasa ini tidak boleh ikut terdeteksi
    return saldo
