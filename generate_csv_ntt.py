import geopandas as gpd
import pandas as pd
import numpy as np

# ===== Load GeoJSON =====
geojson_file = "ntt_kabupaten_full.geojson"
gdf = gpd.read_file(geojson_file)

# ===== Ambil nama kabupaten =====
geo_kab_col = [col for col in gdf.columns if 'name' in col.lower() or 'kabupaten' in col.lower()]
if not geo_kab_col:
    raise ValueError("Kolom nama kabupaten tidak ditemukan di GeoJSON")
geo_kab_col = geo_kab_col[0]

gdf['kabupaten_clean'] = gdf[geo_kab_col].astype(str).str.upper().str.strip()

# ===== Buat CSV lengkap dengan skor simulasi =====
num_pilar = 12
np.random.seed(42)  # agar hasil sama tiap kali dijalankan

data = {
    'kabupaten': gdf['kabupaten_clean']
}

for i in range(1, num_pilar+1):
    # Skor simulasi 60–95
    data[f'pilar_{i}'] = np.random.randint(60, 96, size=len(gdf))

df_csv = pd.DataFrame(data)

# ===== Simpan CSV =====
df_csv.to_csv("ntt_idsd_full.csv", index=False)
print("✅ CSV 'ntt_idsd_full.csv' berhasil dibuat dengan semua kabupaten/kota NTT")
