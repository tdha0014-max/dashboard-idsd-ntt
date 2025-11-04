# =======================================
# 📊 Dashboard IDSD Nusa Tenggara Timur
# =======================================
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit.components.v1 import html
import plotly.express as px
import plotly.graph_objects as go
from branca.colormap import linear
import io

# ===== Konfigurasi Halaman =====
st.set_page_config(page_title="Dashboard IDSD NTT", layout="wide")

# ---------------------------
# 📂 Load Data
# ---------------------------
@st.cache_data
def load_data():
    try:
        df_2023 = pd.read_csv("data_2023_lengkap.csv")
        df_2024 = pd.read_csv("data_2024_lengkap.csv")
        return df_2023, df_2024
    except FileNotFoundError:
        st.error("❌ File CSV lengkap tidak ditemukan.")
        st.stop()

df_2023, df_2024 = load_data()

# ==============================
# 🧩 Samakan struktur kolom antara 2023 & 2024
# ==============================
pilar_cols = [f'pilar_{i}' for i in range(1, 13)]

for col in pilar_cols:
    if col not in df_2023.columns:
        df_2023[col] = None
    if col not in df_2024.columns:
        df_2024[col] = None

# Samakan urutan kolom
df_2023 = df_2023[['kabupaten'] + pilar_cols + [c for c in df_2023.columns if c not in ['kabupaten'] + pilar_cols]]
df_2024 = df_2024[['kabupaten'] + pilar_cols + [c for c in df_2024.columns if c not in ['kabupaten'] + pilar_cols]]

# ---------------------------
# 🗺️ Load GeoJSON
# ---------------------------
@st.cache_resource
def load_geojson():
    try:
        gdf = gpd.read_file("NTT_Kabupaten_All.geojson")
        gdf["kabupaten"] = gdf["kabupaten"].str.upper().str.strip()
        return gdf
    except FileNotFoundError:
        st.error("❌ File GeoJSON tidak ditemukan: NTT_Kabupaten_All.geojson")
        st.stop()

gdf = load_geojson()

# ---------------------------
# 📋 Nama Pilar
# ---------------------------
nama_pilar = {
    f'pilar_{i}': f'Pilar {i}' for i in range(1, 13)
}

# ---------------------------
# 🎯 Header
# ---------------------------
st.title("📊 Dashboard IDSD Nusa Tenggara Timur")
st.markdown("Analisis **Indeks Daya Saing Daerah (IDSD)** dengan 12 Pilar dan 22 Kabupaten/Kota.")

# ---------------------------
# 🔽 Pilihan Tahun & Indikator
# ---------------------------
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    tahun = st.selectbox("📅 Pilih Tahun:", ["2023", "2024"])

with col2:
    kabupaten_selected = st.selectbox("🏛 Pilih Kabupaten (opsional):",
                                      ["(Semua)"] + sorted(df_2023['kabupaten'].unique().tolist()))

df_terpilih = df_2023 if tahun == "2023" else df_2024
df_terpilih["kabupaten"] = df_terpilih["kabupaten"].str.upper().str.strip()

with col3:
    indikator = st.selectbox("🎯 Pilih Pilar:", pilar_cols, format_func=lambda x: nama_pilar.get(x, x))

# ---------------------------
# 🔄 Gabung Data dengan GeoJSON
# ---------------------------
df_map = df_terpilih[['kabupaten', indikator]].copy()
gdf_merged = gdf.merge(df_map, on="kabupaten", how="left")

# ---------------------------
# 🎨 Buat Colormap
# ---------------------------
gdf_merged[indikator] = pd.to_numeric(gdf_merged[indikator], errors="coerce")
gdf_with_data = gdf_merged.dropna(subset=[indikator])

vmin = gdf_with_data[indikator].min()
vmax = gdf_with_data[indikator].max()
if vmin == vmax:
    vmax = vmin + 0.01

colormap = linear.YlGnBu_09.scale(vmin, vmax)
colormap.caption = f"Skor {nama_pilar.get(indikator, indikator)} ({tahun})"

# ---------------------------
# 🗺️ Buat Peta Folium (dengan highlight)
# ---------------------------
m = folium.Map(location=[-8.6, 121.1], zoom_start=7, tiles="CartoDB positron")

for _, row in gdf_merged.iterrows():
    nilai = row[indikator]
    warna = colormap(nilai) if pd.notna(nilai) else "#d3d3d3"

    if kabupaten_selected != "(Semua)" and row["kabupaten"] == kabupaten_selected:
        warna = "#ff6600"  # Warna highlight oranye

    popup_text = (
        f"<b>{row['kabupaten']}</b><br>"
        f"{nama_pilar.get(indikator, indikator)}: {nilai:.2f}" if pd.notna(nilai)
        else f"<b>{row['kabupaten']}</b><br>Data tidak tersedia"
    )

    folium.GeoJson(
        row["geometry"].__geo_interface__,
        style_function=lambda x, color=warna: {
            "fillColor": color,
            "color": "black",
            "weight": 1.2 if row["kabupaten"] == kabupaten_selected else 0.8,
            "fillOpacity": 0.75 if row["kabupaten"] == kabupaten_selected else 0.6,
        },
        tooltip=folium.Tooltip(popup_text),
    ).add_to(m)

colormap.add_to(m)

# Render peta ke HTML
buffer = io.BytesIO()
m.save(buffer, close_file=False)
buffer.seek(0)
map_html = buffer.getvalue().decode()
html(map_html, height=550, scrolling=True)

# ---------------------------
# 📊 Ranking Bar Chart
# ---------------------------
st.markdown("---")
st.subheader(f"📊 Ranking {nama_pilar.get(indikator, indikator)} per Kabupaten/Kota ({tahun})")

df_sorted = df_terpilih[['kabupaten', indikator]].sort_values(by=indikator, ascending=False)
fig = px.bar(df_sorted, x="kabupaten", y=indikator, color=indikator, color_continuous_scale="YlGnBu")
fig.update_layout(xaxis_tickangle=-45, height=500, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 📈 Statistik Deskriptif
# ---------------------------
st.markdown("---")
st.subheader("📈 Statistik Deskriptif")

colA, colB, colC, colD = st.columns(4)
colA.metric("📈 Max", f"{df_terpilih[indikator].max():.2f}")
colB.metric("📉 Min", f"{df_terpilih[indikator].min():.2f}")
colC.metric("📊 Rata-rata", f"{df_terpilih[indikator].mean():.2f}")
colD.metric("🎯 Median", f"{df_terpilih[indikator].median():.2f}")
