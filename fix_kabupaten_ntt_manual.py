import pandas as pd

# === 1️⃣ Baca CSV hasil konversi ===
csv_path = "Data_2024_fixed.csv"
df_csv = pd.read_csv(csv_path)
print(f"📄 CSV dimuat: {csv_path}, total {len(df_csv)} baris")

# === 2️⃣ Baca Excel (nama kabupaten nyata) ===
excel_path = "Data_2024_fixed.xls"
df_excel = pd.read_excel(excel_path)
print(f"📊 Excel dimuat: {excel_path}, total {len(df_excel)} baris")

# === 3️⃣ Deteksi otomatis kolom yang memuat nama kabupaten ===
possible_cols = [c for c in df_excel.columns if any(x in c.lower() for x in ["kab", "wilayah", "daerah", "lokasi", "nama"])]
print("🔎 Kolom terdeteksi di Excel:", possible_cols)

if not possible_cols:
    raise ValueError("❌ Tidak ditemukan kolom yang memuat nama kabupaten.")

kab_col = possible_cols[0]
print(f"✅ Menggunakan kolom '{kab_col}' untuk nama kabupaten.")

# === 4️⃣ Bersihkan nama kabupaten ===
kabupaten_series = (
    df_excel[kab_col]
    .astype(str)
    .str.replace(r'[^A-Za-z\s]', '', regex=True)
    .str.strip()
    .str.upper()
)

# === 5️⃣ Isi kolom kabupaten di CSV ===
min_len = min(len(kabupaten_series), len(df_csv))
df_csv.loc[:min_len-1, "kabupaten"] = kabupaten_series.iloc[:min_len].values

# === 6️⃣ Simpan hasil akhir ===
output_path = "ntt_idsd_2024_final_fixed.csv"
df_csv.to_csv(output_path, index=False)
print(f"✅ File final disimpan sebagai: {output_path}")
print(df_csv.head(10))
