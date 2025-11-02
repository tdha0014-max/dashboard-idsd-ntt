import pandas as pd

# Baca file Excel 2024
df_2024_raw = pd.read_excel("Data_2024_fixed.xls")

print("EXTRACT DATA NTT 2024:")
print("=" * 70)

# Filter data NTT (kode 53xx di kolom 3)
df_2024_ntt = df_2024_raw[df_2024_raw.iloc[:, 3].astype(str).str.startswith('53', na=False)].copy()

print(f"Jumlah kabupaten NTT: {len(df_2024_ntt)}")

# Kolom "Indeks Pilar" yang merupakan skor agregat per pilar
kolom_indeks_pilar = {
    15: 'pilar_1',   # Indeks Pilar Institusi
    24: 'pilar_2',   # Indeks Pilar Infrastruktur
    28: 'pilar_3',   # Indeks Pilar Adopsi TIK
    34: 'pilar_4',   # Indeks Pilar Stabilitas Ekonomi Makro
    36: 'pilar_5',   # Indeks Pilar Kesehatan
    43: 'pilar_6',   # Indeks Pilar Keterampilan
    45: 'pilar_7',   # Indeks Pilar Pasar Produk
    49: 'pilar_8',   # Indeks Pilar Pasar Tenaga Kerja
    53: 'pilar_9',   # Indeks Pilar Sistem Keuangan
    55: 'pilar_10',  # Indeks Pilar Ukuran Pasar
    58: 'pilar_11',  # Indeks Pilar Dinamika Bisnis
    66: 'pilar_12'   # Indeks Pilar Kapabilitas Inovasi
}

# Mapping detail indikator per pilar
indikator_map = {
    'pilar_1': list(range(5, 16)),    # Pilar 1: kolom 5-15
    'pilar_2': list(range(16, 25)),   # Pilar 2: kolom 16-24
    'pilar_3': list(range(25, 29)),   # Pilar 3: kolom 25-28
    'pilar_4': list(range(30, 35)),   # Pilar 4: kolom 30-34
    'pilar_5': [35, 36],              # Pilar 5: kolom 35-36
    'pilar_6': list(range(37, 44)),   # Pilar 6: kolom 37-43
    'pilar_7': [44, 45],              # Pilar 7: kolom 44-45
    'pilar_8': list(range(46, 50)),   # Pilar 8: kolom 46-49
    'pilar_9': list(range(50, 54)),   # Pilar 9: kolom 50-53
    'pilar_10': [54, 55],             # Pilar 10: kolom 54-55
    'pilar_11': list(range(56, 59)),  # Pilar 11: kolom 56-58
    'pilar_12': list(range(59, 67))   # Pilar 12: kolom 59-66
}

# Extract nama indikator dari baris header
nama_indikator_2024 = {}
for i in range(5, 67):
    nama = str(df_2024_raw.iloc[2, i])  # Nama indikator di baris 2
    if nama != 'nan' and nama != '':
        nama_indikator_2024[i] = nama.strip()

# Buat dataframe hasil
data = {
    'kabupaten': df_2024_ntt.iloc[:, 4].values  # Nama kabupaten di kolom 4
}

# Extract skor pilar (dari kolom Indeks Pilar)
for col_idx, pilar_name in kolom_indeks_pilar.items():
    data[pilar_name] = df_2024_ntt.iloc[:, col_idx].values

# Extract detail indikator
for pilar_key, kolom_list in indikator_map.items():
    for i, col_idx in enumerate(kolom_list):
        nama = nama_indikator_2024.get(col_idx, f"indikator_{col_idx}")
        col_name = f"{pilar_key}_{i+1:02d}_{nama[:30]}"
        data[col_name] = df_2024_ntt.iloc[:, col_idx].values

df_2024_clean = pd.DataFrame(data)

# Bersihkan nama kabupaten
df_2024_clean['kabupaten'] = (df_2024_clean['kabupaten']
                               .str.upper()
                               .str.replace('KAB. ', '', regex=False)
                               .str.replace('KOTA ', '', regex=False)
                               .str.strip())

# Simpan
df_2024_clean.to_csv("data_2024_lengkap.csv", index=False)

print("\n✅ BERHASIL!")
print("=" * 70)
print(f"Data 2024: {len(df_2024_clean)} kabupaten, {len(df_2024_clean.columns)} kolom")

print("\nKabupaten NTT 2024:")
for kab in sorted(df_2024_clean['kabupaten'].unique()):
    print(f"  - {kab}")

print("\nPreview data 2024:")
print(df_2024_clean[['kabupaten', 'pilar_1', 'pilar_2', 'pilar_3', 'pilar_4', 'pilar_5']].head())

print("\nStatistik Pilar 1 (2024):")
print(df_2024_clean['pilar_1'].describe())