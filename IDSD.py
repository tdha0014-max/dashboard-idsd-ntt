# =======================================
# 📊 Dashboard IDSD Nusa Tenggara Timur
# =======================================

import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from branca.colormap import linear

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard IDSD NTT", layout="wide")


# ---------------------------
# 📂 Load Data
# ---------------------------
@st.cache_data
def load_data():
    try:
        # Load data lengkap dengan semua indikator
        df_2023 = pd.read_csv("data_2023_lengkap.csv")
        df_2024 = pd.read_csv("data_2024_lengkap_fix.csv.csv")
        return df_2023, df_2024
    except FileNotFoundError:
        st.error("❌ File CSV lengkap tidak ditemukan. Jalankan script extract data terlebih dahulu!")
        st.stop()


df_2023, df_2024 = load_data()


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
# 📋 Mapping Nama Pilar
# ---------------------------
nama_pilar = {
    'pilar_1': 'Pilar 1: Institusi',
    'pilar_2': 'Pilar 2: Infrastruktur',
    'pilar_3': 'Pilar 3: Adopsi TIK',
    'pilar_4': 'Pilar 4: Stabilitas Ekonomi Makro',
    'pilar_5': 'Pilar 5: Kesehatan',
    'pilar_6': 'Pilar 6: Keterampilan',
    'pilar_7': 'Pilar 7: Pasar Produk',
    'pilar_8': 'Pilar 8: Pasar Tenaga Kerja',
    'pilar_9': 'Pilar 9: Sistem Keuangan',
    'pilar_10': 'Pilar 10: Ukuran Pasar',
    'pilar_11': 'Pilar 11: Dinamisme Bisnis',
    'pilar_12': 'Pilar 12: Kapabilitas Inovasi'
}

# ---------------------------
# 🎯 Header Dashboard
# ---------------------------
st.title("📊 Dashboard IDSD Nusa Tenggara Timur")
st.markdown("**Indeks Daya Saing Daerah (IDSD)** - Analisis 12 Pilar dengan Detail Indikator per Kabupaten/Kota")

# ---------------------------
# 🔽 Pilihan Tahun & Indikator
# ---------------------------
col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    tahun = st.selectbox("📅 Pilih Tahun:", ["2023", "2024"])

# Pilih dataframe berdasarkan tahun
df_terpilih = df_2023 if tahun == "2023" else df_2024

# Pastikan kolom kabupaten konsisten
df_terpilih["kabupaten"] = df_terpilih["kabupaten"].str.upper().str.strip()

# Ambil hanya kolom pilar utama (pilar_1 sampai pilar_12)
kolom_pilar = [col for col in df_terpilih.columns if
               col.startswith('pilar_') and col.split('_')[1].isdigit() and len(col.split('_')) == 2]

with col_filter2:
    indikator = st.selectbox(
        "🎯 Pilih Pilar IDSD:",
        kolom_pilar,
        format_func=lambda x: nama_pilar.get(x, x)
    )

# ---------------------------
# 🔄 Gabung Data dengan GeoJSON
# ---------------------------
# Untuk peta, kita hanya perlu kolom kabupaten dan pilar yang dipilih
df_map = df_terpilih[['kabupaten', indikator]].copy()
gdf_merged = gdf.merge(df_map, on="kabupaten", how="left")

# ---------------------------
# 🎨 Buat Colormap
# ---------------------------
gdf_merged[indikator] = pd.to_numeric(gdf_merged[indikator], errors="coerce")
gdf_with_data = gdf_merged.dropna(subset=[indikator])

if len(gdf_with_data) == 0:
    st.error(f"❌ Tidak ada data valid untuk: {nama_pilar.get(indikator, indikator)}")
    st.stop()

vmin = gdf_with_data[indikator].min()
vmax = gdf_with_data[indikator].max()
if vmin == vmax:
    vmax = vmin + 0.01

colormap = linear.YlGnBu_09.scale(vmin, vmax).to_step(n=10)
colormap.caption = f"Skor {nama_pilar.get(indikator, indikator)} ({tahun})"

# ---------------------------
# 🗺️ Buat Peta Folium
# ---------------------------
m = folium.Map(location=[-8.6, 121.1], zoom_start=7, tiles="CartoDB positron")

folium.GeoJson(
    gdf_merged,
    name="IDSD NTT",
    style_function=lambda x: {
        "fillColor": colormap(x["properties"][indikator])
        if x["properties"].get(indikator) is not None
        else "#d3d3d3",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=folium.features.GeoJsonTooltip(
        fields=["kabupaten", indikator],
        aliases=["Kabupaten/Kota:", f"{nama_pilar.get(indikator, indikator)}:"],
        localize=True,
    ),
).add_to(m)

colormap.add_to(m)

# ---------------------------
# 📊 Layout Dashboard - Peta & Tabel
# ---------------------------
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"🗺️ Peta {nama_pilar.get(indikator, indikator)} - Tahun {tahun}")
    st_folium(m, width=900, height=550)

with col2:
    st.subheader("📋 Tabel Skor Pilar")
    df_display = df_terpilih[['kabupaten'] + kolom_pilar].sort_values('kabupaten')
    st.dataframe(df_display, use_container_width=True, height=550)

# ---------------------------
# 📈 Grafik Ranking Pilar
# ---------------------------
st.markdown("---")
st.subheader(f"📊 Ranking {nama_pilar.get(indikator, indikator)} per Kabupaten/Kota ({tahun})")

df_sorted = df_terpilih[['kabupaten', indikator]].sort_values(by=indikator, ascending=False)

fig_pilar = px.bar(
    df_sorted,
    x="kabupaten",
    y=indikator,
    color=indikator,
    color_continuous_scale="YlGnBu",
    title=f"Skor {nama_pilar.get(indikator, indikator)} - Tahun {tahun}",
    labels={indikator: nama_pilar.get(indikator, indikator), "kabupaten": "Kabupaten/Kota"}
)
fig_pilar.update_layout(
    xaxis_tickangle=-45,
    height=500,
    showlegend=False
)
st.plotly_chart(fig_pilar, use_container_width=True)

# ---------------------------
# 📊 Detail Indikator per Pilar
# ---------------------------
st.markdown("---")
st.subheader(f"🔍 Detail Indikator: {nama_pilar.get(indikator, indikator)}")

# Ambil kolom indikator yang sesuai dengan pilar terpilih
kolom_indikator = [col for col in df_terpilih.columns if col.startswith(f"{indikator}_")]

if len(kolom_indikator) > 0:
    # Tab untuk memilih kabupaten
    tab_mode = st.radio("Pilih Mode Tampilan:", ["Per Kabupaten", "Per Indikator"], horizontal=True)

    if tab_mode == "Per Kabupaten":
        # Pilih kabupaten
        kabupaten_terpilih = st.selectbox("Pilih Kabupaten:", sorted(df_terpilih['kabupaten'].unique()))

        # Ambil data kabupaten
        data_kab = df_terpilih[df_terpilih['kabupaten'] == kabupaten_terpilih].iloc[0]

        # Buat dataframe untuk indikator
        indikator_data = []
        for col in kolom_indikator:
            # Parse nama indikator dari nama kolom
            parts = col.split('_', 2)
            if len(parts) >= 3:
                nama_ind = parts[2].replace('_', ' ')
            else:
                nama_ind = col

            nilai = data_kab[col]
            indikator_data.append({'Indikator': nama_ind, 'Nilai': nilai})

        df_indikator = pd.DataFrame(indikator_data)

        # Tampilkan dalam 2 kolom
        col_detail1, col_detail2 = st.columns(2)

        with col_detail1:
            st.markdown(f"### 📍 {kabupaten_terpilih}")
            st.markdown(f"**Skor {nama_pilar.get(indikator, indikator)}:** `{data_kab[indikator]:.2f}`")

            # Tabel indikator
            st.dataframe(df_indikator, use_container_width=True, height=400)

        with col_detail2:
            # Grafik radar/bar untuk indikator
            fig_detail = go.Figure()

            fig_detail.add_trace(go.Bar(
                x=df_indikator['Nilai'],
                y=df_indikator['Indikator'],
                orientation='h',
                marker=dict(color=df_indikator['Nilai'], colorscale='YlGnBu')
            ))

            fig_detail.update_layout(
                title=f"Detail Indikator - {kabupaten_terpilih}",
                xaxis_title="Nilai",
                yaxis_title="Indikator",
                height=500,
                showlegend=False
            )

            st.plotly_chart(fig_detail, use_container_width=True)

    else:  # Per Indikator
        # Pilih indikator
        indikator_detail = st.selectbox("Pilih Indikator:", kolom_indikator,
                                        format_func=lambda x: x.split('_', 2)[2].replace('_', ' ') if len(
                                            x.split('_', 2)) >= 3 else x)

        # Nama indikator untuk tampilan
        nama_ind = indikator_detail.split('_', 2)[2].replace('_', ' ') if len(
            indikator_detail.split('_', 2)) >= 3 else indikator_detail

        # Data indikator untuk semua kabupaten
        df_ind_all = df_terpilih[['kabupaten', indikator_detail]].sort_values(by=indikator_detail, ascending=False)

        col_ind1, col_ind2 = st.columns(2)

        with col_ind1:
            st.markdown(f"### 📊 {nama_ind}")
            st.dataframe(df_ind_all, use_container_width=True, height=500)

        with col_ind2:
            # Grafik ranking indikator
            fig_ind = px.bar(
                df_ind_all,
                x='kabupaten',
                y=indikator_detail,
                color=indikator_detail,
                color_continuous_scale='YlGnBu',
                title=f"Ranking: {nama_ind}"
            )
            fig_ind.update_layout(
                xaxis_tickangle=-45,
                height=500,
                showlegend=False
            )
            st.plotly_chart(fig_ind, use_container_width=True)

else:
    st.info("ℹ️ Detail indikator tidak tersedia untuk pilar ini.")

# ---------------------------
# 📊 Statistik Deskriptif
# ---------------------------
st.markdown("---")
st.subheader("📈 Statistik Deskriptif")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric("📈 Nilai Tertinggi", f"{df_terpilih[indikator].max():.2f}")
with col_stat2:
    st.metric("📉 Nilai Terendah", f"{df_terpilih[indikator].min():.2f}")
with col_stat3:
    st.metric("📊 Rata-rata", f"{df_terpilih[indikator].mean():.2f}")
with col_stat4:
    st.metric("🎯 Median", f"{df_terpilih[indikator].median():.2f}")

# Info di sidebar
with st.sidebar:
    st.header("ℹ️ Info Dashboard")
    st.metric("Total Kabupaten/Kota", len(df_terpilih))
    st.metric("Total Pilar", len(kolom_pilar))
    st.metric("Total Indikator", len(kolom_indikator))

    st.markdown("---")
    st.markdown("### 📌 12 Pilar IDSD:")
    for i, (key, val) in enumerate(nama_pilar.items(), 1):
        st.markdown(f"{i}. {val.replace('Pilar ' + str(i) + ': ', '')}")

# ---------------------------
# 📌 Info Tambahan
# ---------------------------
st.markdown("---")
st.markdown(
    """
    ### 📌 Catatan:
    - **Sumber Data**: Indeks Daya Saing Daerah (IDSD) Nusa Tenggara Timur
    - **Tahun Data**: 2023 dan 2024
    - **Jumlah Kabupaten/Kota**: 22
    - **Jumlah Pilar IDSD**: 12
    - **Kabupaten berwarna abu-abu di peta**: Tidak memiliki data untuk indikator terpilih

    Dashboard ini menampilkan:
    - 🗺️ **Peta Interaktif**: Visualisasi spasial skor pilar per kabupaten
    - 📊 **Grafik Ranking**: Perbandingan skor antar kabupaten
    - 🔍 **Detail Indikator**: Breakdown indikator penyusun setiap pilar
    - 📈 **Statistik**: Analisis deskriptif data
    """
)