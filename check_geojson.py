import json

with open("data/geojson_kecamatan_ntt_official.geojson", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Tipe file:", data.get("type"))
print("Jumlah features:", len(data.get("features", [])))

# Cek keys feature pertama
if len(data.get("features", [])) > 0:
    print("Keys feature pertama:", data["features"][0].keys())
