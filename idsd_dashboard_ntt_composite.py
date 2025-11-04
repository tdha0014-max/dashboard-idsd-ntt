# =======================================
# 📊 Dashboard Perbandingan IDSD NTT 2023 vs 2024
# =======================================

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit.components.v1 import html
from branca.colormap import linear
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# ⚙️ Konfigurasi halaman
# ---------------------------
st.set_page_config(page_title="Dashboard Perbandingan IDSD NTT", layout="wide")

st.title("📊 Dashboard Perbandingan IDSD Nusa Tenggara Timur (2023 vs 2024)")
st.markdown("Bandingkan skor IDSD antar kabupaten/kota dan antar tahun untuk setiap pilar dan indikator.")

# ---------------------------
# 📂 Load Data
# ---------------------------
@st.cache_data
def load_data():
    df_2023 = pd.read_csv("data_2023_lengkap.csv")
    df_2024 = pd.read_csv("data_2024_lengkap.csv")

    # Normalisasi nama kabupaten
    df_2023["kabupaten"] = df_2023["kabupaten"].str.upper().str.strip()
    df_2024["kabupaten"] = df_2024["kabupaten"].str.upper().str.strip()

    # Samakan kolom antar tahun
    semua_kolom = sorted(set(df_2023.columns) | set(df_2024.columns))
    for df in [df_2023, df_2024]:
        for kol in semua_kolom:
            if kol not in df.columns:
                df[kol] = None
        df = df[semua_kolom]

    return df_2023, df_2024

df_2023, df_2024 = load_data()

# ---------------------------
# 🗺️ Load GeoJSON
# ---------------------------
@st.cache_resource
def load_geojson():
    gdf = gpd.read_file("NTT_Kabupaten_All.geojson")
    gdf["kabupaten"] = gdf["kabupaten"].str.upper().str.strip()
    return gdf

gdf = load_geojson()

# ---------------------------
# 📋 Mapping Nama Pilar
# ---------------------------
nama_pilar = {
    f"pilar_{i}": f"Pilar {i}" for i in range(1, 13)
}

# ---------------------------
# 🎯 Filter Pilihan
# ---------------------------
col1, col2 = st.columns(2)
with col1:
    indikator = st.selectbox("🎯 Pilih Pilar IDSD:", [f"pilar_{i}" for i in range(1, 13)],
                             format_func=lambda x: nama_pilar.get(x, x))
with col2:
    mode = st.radio("📅 Mode Perbandingan:", ["Antar Tahun", "Antar Kabupaten"], horizontal=True)

# ---------------------------
# 🔄 Gabung Data dan Sinkronisasi
# ---------------------------
gdf_merged_2023 = gdf.merge(df_2023[["kabupaten", indikator]], on="kabupaten", how="left")
gdf_merged_2024 = gdf.merge(df_2024[["kabupaten", indikator]], on="kabupaten", how="left")

# ---------------------------
# 🎨 Peta Perbandingan
# ---------------------------
colmap1, colmap2 = st.columns(2)
colormap = linear.YlGnBu_09.scale(
    min(df_2023[indikator].min(), df_2024[indikator].min()),
    max(df_2023[indikator].max(), df_2024[indikator].max())
)

with colmap1:
    st.subheader(f"🗺️ Peta {nama_pilar[indikator]} - 2023")
    m1 = folium.Map(location=[-8.6, 121.1], zoom_start=7, tiles="CartoDB positron")

    for _, row in gdf_merged_2023.iterrows():
        val = row[indikator]
        warna = colormap(val) if pd.notna(val) else "#d3d3d3"
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda x, fc=warna: {"fillColor": fc, "color": "black", "weight": 1, "fillOpacity": 0.7},
            tooltip=f"<b>{row['kabupaten']}</b><br>{nama_pilar[indikator]}: {val if pd.notna(val) else 'N/A'}"
        ).add_to(m1)
    colormap.add_to(m1)
    html(m1._repr_html_(), height=450)

with colmap2:
    st.subheader(f"🗺️ Peta {nama_pilar[indikator]} - 2024")
    m2 = folium.Map(location=[-8.6, 121.1], zoom_start=7, tiles="CartoDB positron")

    for _, row in gdf_merged_2024.iterrows():
        val = row[indikator]
        warna = colormap(val) if pd.notna(val) else "#d3d3d3"
        folium.GeoJson(
            row["geometry"].__geo_interface__,
            style_function=lambda x, fc=warna: {"fillColor": fc, "color": "black", "weight": 1, "fillOpacity": 0.7},
            tooltip=f"<b>{row['kabupaten']}</b><br>{nama_pilar[indikator]}: {val if pd.notna(val) else 'N/A'}"
        ).add_to(m2)
    colormap.add_to(m2)
    html(m2._repr_html_(), height=450)

# ---------------------------
# 📊 Perbandingan Skor
# ---------------------------
st.markdown("---")
st.subheader(f"📈 Perbandingan Skor {nama_pilar[indikator]} 2023 vs 2024")

df_compare = pd.merge(
    df_2023[["kabupaten", indikator]],
    df_2024[["kabupaten", indikator]],
    on="kabupaten",
    how="outer",
    suffixes=("_2023", "_2024")
)

df_compare["Δ (2024 - 2023)"] = df_compare[f"{indikator}_2024"] - df_compare[f"{indikator}_2023"]

fig = px.bar(
    df_compare.sort_values("Δ (2024 - 2023)", ascending=False),
    x="kabupaten",
    y="Δ (2024 - 2023)",
    color="Δ (2024 - 2023)",
    color_continuous_scale="RdYlGn",
    title=f"Δ Skor {nama_pilar[indikator]} (2024 - 2023)"
)
fig.update_layout(xaxis_tickangle=-45, height=450)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 🔍 Detail Indikator per Pilar
# ---------------------------
st.markdown("---")
st.subheader(f"🔍 Detail Indikator {nama_pilar[indikator]}")

# Ambil kolom indikator rinci
kolom_indikator = [c for c in df_2023.columns if c.startswith(f"{indikator}_")]

if len(kolom_indikator) > 0:
    kab = st.selectbox("🏛 Pilih Kabupaten/Kota:", sorted(df_2023["kabupaten"].unique()))

    df_2023_det = df_2023[df_2023["kabupaten"] == kab][kolom_indikator].T.reset_index()
    df_2024_det = df_2024[df_2024["kabupaten"] == kab][kolom_indikator].T.reset_index()

    df_2023_det.columns = ["Indikator", "2023"]
    df_2024_det.columns = ["Indikator", "2024"]

    df_merge_det = pd.merge(df_2023_det, df_2024_det, on="Indikator", how="outer")
    df_merge_det["Δ (2024-2023)"] = df_merge_det["2024"] - df_merge_det["2023"]

    st.dataframe(df_merge_det, use_container_width=True, height=450)

    # Grafik perbandingan indikator
    fig_ind = go.Figure()
    fig_ind.add_trace(go.Bar(y=df_merge_det["Indikator"], x=df_merge_det["2023"], orientation='h', name='2023'))
    fig_ind.add_trace(go.Bar(y=df_merge_det["Indikator"], x=df_merge_det["2024"], orientation='h', name='2024'))
    fig_ind.update_layout(
        barmode='group', height=500,
        title=f"Perbandingan Indikator {nama_pilar[indikator]} - {kab}"
    )
    st.plotly_chart(fig_ind, use_container_width=True)
else:
    st.info("ℹ️ Tidak ada indikator rinci untuk pilar ini.")

# ---------------------------
# 📈 Statistik Ringkas
# ---------------------------
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📈 Rata-rata 2023", f"{df_2023[indikator].mean():.2f}")
with col2:
    st.metric("📈 Rata-rata 2024", f"{df_2024[indikator].mean():.2f}")
with col3:
    delta_mean = df_2024[indikator].mean() - df_2023[indikator].mean()
    st.metric("Δ Rata-rata (2024 - 2023)", f"{delta_mean:.2f}",
              delta=f"{(delta_mean):+.2f}", delta_color="normal")

st.success("✅ Dashboard perbandingan siap digunakan – semua kolom sudah disinkronkan otomatis.")
