# =======================================
# 🏆 Ultra-Polished Dashboard IDSD NTT (FIXED)
# =======================================
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from branca.colormap import linear
from io import BytesIO

# ===== Config halaman =====
st.set_page_config(page_title="Ultra-Polished Dashboard IDSD NTT",
                   layout="wide",
                   initial_sidebar_state="expanded")

# ===== Tema =====
theme = st.sidebar.radio("🎨 Tema Dashboard", ["Light", "Dark"], index=0)


# ===== Load Data =====
@st.cache_data
def load_data():
    df_2023 = pd.read_csv("data/idsd_data_2023_lengkap.csv")
    df_2024 = pd.read_csv("data/idsd_data_2024.csv")
    df_2023["kabupaten"] = df_2023["kabupaten"].str.upper().str.strip()
    df_2024["kabupaten"] = df_2024["kabupaten"].str.upper().str.strip()
    return df_2023, df_2024


df_2023, df_2024 = load_data()


# ===== Load GeoJSON =====
@st.cache_resource
def load_geojson():
    gdf = gpd.read_file("data/geojson_kabupaten.geojson")
    gdf["kabupaten"] = gdf["kabupaten"].str.upper().str.strip()
    return gdf


gdf = load_geojson()

# ===== Nama Pilar =====
nama_pilar = {f'pilar_{i}': f'Pilar {i}' for i in range(1, 13)}

# ===== Sidebar Filter =====
st.sidebar.header("📌 Filter Dashboard")
tahun_sel = st.sidebar.multiselect("📅 Tahun", ["2023", "2024"], default=["2023", "2024"])
kab_sel = st.sidebar.multiselect("🏛 Kabupaten/Kota", sorted(df_2023['kabupaten'].unique()), default=None)
indikator = st.sidebar.selectbox("🎯 Pilar IDSD",
                                 [f'pilar_{i}' for i in range(1, 13)],
                                 format_func=lambda x: nama_pilar.get(x, x))


# ===== Fungsi Merge Data =====
def merge_data(tahun):
    df = df_2023 if tahun == "2023" else df_2024

    # Cek apakah kolom indikator ada di dataframe
    if indikator not in df.columns:
        st.error(f"❌ Kolom '{indikator}' tidak ditemukan di data tahun {tahun}")
        st.info(f"Kolom yang tersedia: {', '.join(df.columns.tolist())}")
        # Kembalikan data kosong untuk menghindari crash
        gdf_empty = gdf.copy()
        gdf_empty[indikator] = 0
        return gdf_empty, df

    df_map = df[['kabupaten', indikator]].copy()
    gdf_merged = gdf.merge(df_map, on="kabupaten", how="left")
    gdf_merged[indikator] = pd.to_numeric(gdf_merged[indikator], errors="coerce")

    # Tambahkan nama pilar yang lebih deskriptif untuk tooltip
    gdf_merged['nama_pilar'] = nama_pilar.get(indikator, indikator)

    return gdf_merged, df


# ===== Tabs Tahun =====
tabs = st.tabs(tahun_sel)
for i, tahun in enumerate(tahun_sel):
    with tabs[i]:
        gdf_merged, df_terpilih = merge_data(tahun)

        # ===== Colormap =====
        vmin, vmax = gdf_merged[indikator].min(), gdf_merged[indikator].max()
        if pd.isna(vmin) or pd.isna(vmax):
            vmin, vmax = 0, 100
        if vmin == vmax: vmax = vmin + 0.01
        colormap = linear.YlGnBu_09.scale(vmin, vmax).to_step(n=10)
        colormap.caption = f"{nama_pilar.get(indikator, indikator)} ({tahun})"

        # ===== Peta Interaktif (ALTERNATIF - Menggunakan Plotly) =====
        st.subheader(f"🗺️ Peta {nama_pilar.get(indikator, indikator)} - Tahun {tahun}")

        # Konversi GeoDataFrame ke format yang bisa dibaca Plotly
        gdf_plot = gdf_merged.copy()
        gdf_plot['geometry'] = gdf_plot['geometry'].to_crs(epsg=4326)

        # Buat custom hover text dengan nama pilar
        gdf_plot['hover_text'] = (
                '<b>' + gdf_plot['kabupaten'] + '</b><br>' +
                nama_pilar.get(indikator, indikator) + ': ' +
                gdf_plot[indikator].round(2).astype(str)
        )

        fig_map = px.choropleth_mapbox(
            gdf_plot,
            geojson=gdf_plot.geometry.__geo_interface__,
            locations=gdf_plot.index,
            color=indikator,
            hover_name='kabupaten',
            hover_data={
                indikator: ':.2f',
                'kabupaten': False,
                'nama_pilar': True
            },
            color_continuous_scale='YlGnBu',
            mapbox_style="carto-positron" if theme == "Light" else "carto-darkmatter",
            center={"lat": -8.6, "lon": 121.1},
            zoom=6,
            opacity=0.7,
            labels={
                indikator: nama_pilar.get(indikator, indikator),
                'nama_pilar': 'Pilar'
            }
        )

        fig_map.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=550
        )

        st.plotly_chart(fig_map, use_container_width=True)

        # ===== Ranking Chart =====
        st.subheader("📊 Ranking Kabupaten")
        if kab_sel:
            df_sorted = df_terpilih[df_terpilih['kabupaten'].isin(kab_sel)][['kabupaten', indikator]].sort_values(
                by=indikator, ascending=False)
        else:
            df_sorted = df_terpilih[['kabupaten', indikator]].sort_values(by=indikator, ascending=False)

        fig = px.bar(df_sorted, x='kabupaten', y=indikator, color=indikator, color_continuous_scale='YlGnBu')
        fig.update_layout(xaxis_tickangle=-45, height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # ===== Radar Chart =====
        st.subheader("📈 Radar Chart 12 Pilar")
        df_radar = df_terpilih.set_index('kabupaten')[[f'pilar_{i}' for i in range(1, 13)]]
        if kab_sel:
            df_radar = df_radar.loc[df_radar.index.isin(kab_sel)]
        fig_radar = go.Figure()
        for idx, row in df_radar.iterrows():
            fig_radar.add_trace(go.Scatterpolar(r=row.values, theta=list(nama_pilar.values()), fill='toself', name=idx))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=550)
        st.plotly_chart(fig_radar, use_container_width=True)

        # ===== Download Excel =====
        st.subheader("💾 Download Data Filtered")


        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()


        excel_data = to_excel(df_terpilih)
        st.download_button("📥 Download Data Excel", excel_data, file_name=f"IDSD_NTT_{tahun}.xlsx",
                           mime="application/vnd.ms-excel")

# ===== Statistik Deskriptif =====
st.markdown("---")
st.subheader("📊 Statistik Deskriptif Pilar Terpilih")
col1, col2, col3, col4 = st.columns(4)
col1.metric("📈 Max", f"{df_terpilih[indikator].max():.2f}")
col2.metric("📉 Min", f"{df_terpilih[indikator].min():.2f}")
col3.metric("📊 Rata-rata", f"{df_terpilih[indikator].mean():.2f}")
col4.metric("🎯 Median", f"{df_terpilih[indikator].median():.2f}")