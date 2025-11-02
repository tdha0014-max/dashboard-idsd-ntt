#!/bin/bash

echo "=== Setup Dashboard IDSD NTT ==="

# -------------------------
# CSV Files
# -------------------------
echo "Memastikan CSV tersedia..."
[ -f data/idsd_data_2023.csv ] || cp data_2023_lengkap.csv data/idsd_data_2023.csv
[ -f data/idsd_data_2024.csv ] || cp data_2024_lengkap.csv data/idsd_data_2024.csv

# -------------------------
# GeoJSON Kabupaten
# -------------------------
echo "Memastikan GeoJSON Kabupaten tersedia..."
if [ ! -f NTT_Kabupaten_All.geojson ]; then
    echo "⚠️ File NTT_Kabupaten_All.geojson tidak ditemukan!"
    echo "Silakan taruh file GeoJSON kabupaten di folder project."
else
    echo "GeoJSON Kabupaten tersedia ✔️"
fi

# -------------------------
# GeoJSON Kecamatan
# -------------------------
echo "Memastikan GeoJSON Kecamatan tersedia..."
if [ ! -f data/geojson_kecamatan_ntt_official.geojson ]; then
    echo "⚠️ File geojson_kecamatan_ntt_official.geojson tidak ditemukan."
    echo "Bagian dashboard per kecamatan akan dikomentari sementara."
    # Optional: buat file dummy agar script tidak crash
    echo '{}' > data/geojson_kecamatan_ntt_official.geojson
fi

echo "Setup selesai! Dashboard siap dijalankan."
