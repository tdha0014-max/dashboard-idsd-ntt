import pandas as pd

# Baca Excel asli (sumber nama kabupaten)
df_excel = pd.read_excel("Data_2024_clean.xlsx")
print("Kolom di Excel:", df_excel.columns.tolist())

# Cari kolom kabupaten
kab_col = [c for c in df_excel.columns if 'kab' in c.lower() or 'wilayah' in c.lower()]
if kab_col:
    df_excel = df_excel.rename(columns={kab_col[0]: 'kabupaten'})
else:
    raise ValueError("❌ Tidak ditemukan kolom kabupaten di Excel!")

# Ambil kolom kabupaten saja
kabupaten_series = df_excel['kabupaten']

# Baca file CSV yang sudah difix
df_csv = pd.read_csv("ntt_idsd_2024_final_fixed.csv")

# Ganti kolom kabupaten di CSV dengan data dari Excel
df_csv['kabupaten'] = kabupaten_series

# Simpan hasil akhir
df_csv.to_csv("ntt_idsd_2024_final_complete.csv", index=False)
print("✅ Nama kabupaten berhasil digabungkan dari Excel.")
print(df_csv.head(10))
