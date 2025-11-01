import pandas as pd

# 1️⃣ Baca file CSV hasil konversi
csv_path = "Data_2024_fixed.csv"
df_csv = pd.read_csv(csv_path)

# 2️⃣ Baca Excel yang berisi nama kabupaten
excel_path = "Data_2024_fixed.xls"
df_excel = pd.read_excel(excel_path)

# 3️⃣ Deteksi kolom nama kabupaten
kab_col = [c for c in df_excel.columns if 'kab' in c.lower() or 'wilayah' in c.lower()]
if not kab_col:
    raise ValueError("❌ Tidak ditemukan kolom kabupaten di Excel.")
kab_col = kab_col[0]
print(f"✅ Kolom kabupaten ditemukan: {kab_col}")

# 4️⃣ Bersihkan nama kabupaten
kabupaten_series = (
    df_excel[kab_col]
    .astype(str)
    .str.replace(r'[^A-Za-z\s]', '', regex=True)
    .str.strip()
    .str.upper()
)

# 5️⃣ Sesuaikan panjang otomatis
n_excel = len(kabupaten_series)
n_csv = len(df_csv)
print(f"🧮 Baris di Excel: {n_excel}, baris di CSV: {n_csv}")

min_len = min(n_excel, n_csv)
df_csv.loc[:min_len-1, "kabupaten"] = kabupaten_series.iloc[:min_len].values

# 6️⃣ Simpan hasil akhir
output_path = "ntt_idsd_2024_final_fixed.csv"
df_csv.to_csv(output_path, index=False)
print(f"✅ File final disimpan sebagai: {output_path}")
print(df_csv.head(10))
