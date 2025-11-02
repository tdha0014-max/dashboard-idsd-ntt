# =======================================
# 📊 Dashboard IDSD Nusa Tenggara Timur - Super Interactive
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

st.set_page_config(page_title="IDSD NTT Dashboard", layout="wide")

# ===== Load Data =====
@st.cache_data
def load_data():
    df_2023 = pd.read_csv("data_2023_lengkap.csv")
    df_2024 = pd.read_csv("data_2024_lengkap.csv")
    return df_2023, df_2024

df_2023, df_2024 = load_data()

# ===== Load GeoJSON =====
@st.cache_resource
def load_geojson():
    gdf = gpd.read_file("NTT_Kabupaten_All.geojson")
    gdf["kabupaten"] = gdf["kabupaten"].str.upper().str.strip()
    return gdf

gdf = load_geojson()

# ===== Nama Pilar =====
nama_pilar = {f'pilar_{i}': f'Pilar {i}' for i in range(1,13)}

# ===== Sidebar =====
with st.sidebar:
    st.header("Filter Dashboard")
    tahun = st.selectbox("📅 Pilih Tahun:", ["2023","2024"])
    df_terpilih = df_2023 if tahun=="2023" else df_2024
    df_terpilih["kabupaten"] = df_terpilih["kabupaten"].str.upper().str.strip()
    kolom_pilar = [col for col in df_terpilih.columns if col.startswith('pilar_')]
    indikator = st.selectbox("🎯 Pilih Pilar:", kolom_pilar, format_func=lambda x: nama_pilar.get(x,x))
    kab_sel = st.selectbox("🏛 Pilih Kabupaten:", sorted(df_terpilih['kabupaten'].unique()) + ["Semua"])

# ===== Merge GeoJSON =====
df_map = df_terpilih[['kabupaten', indikator]].copy()
gdf_merged = gdf.merge(df_map, on="kabupaten", how="left")
gdf_merged[indikator] = pd.to_numeric(gdf_merged[indikator], errors="coerce")

# ===== Colormap =====
vmin, vmax = gdf_merged[indikator].min(), gdf_merged[indikator].max()
if vmin==vmax: vmax=vmin+0.01
colormap = linear.YlGnBu_09.scale(vmin,vmax).to_step(n=10)
colormap.caption = f"{nama_pilar.get(indikator,indikator)} ({tahun})"

# ===== Highlight kabupaten terpilih =====
def style_function(feature):
    val = feature["properties"].get(indikator)
    base_color = colormap(val) if val is not None else "#d3d3d3"
    if kab_sel != "Semua" and feature["properties"]["kabupaten"]==kab_sel:
        base_color = "#ff6600"
    return {"fillColor": base_color, "color":"black","weight":1,"fillOpacity":0.7}

m = folium.Map(location=[-8.6,121.1], zoom_start=7, tiles="CartoDB positron")
folium.GeoJson(
    gdf_merged,
    style_function=style_function,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["kabupaten", indikator],
        aliases=["Kabupaten/Kota:", f"{nama_pilar.get(indikator,indikator)}:"],
        localize=True,
    )
).add_to(m)
colormap.add_to(m)

# ===== Layout =====
col1, col2 = st.columns([2,1])
with col1:
    st.subheader(f"🗺️ Peta {nama_pilar.get(indikator,indikator)} ({tahun})")
    st_folium(m, width=900, height=550)

with col2:
    st.subheader("📋 Tabel Skor Pilar")
    if kab_sel=="Semua":
        df_display = df_terpilih[['kabupaten'] + kolom_pilar].sort_values('kabupaten')
    else:
        df_display = df_terpilih[df_terpilih['kabupaten']==kab_sel][['kabupaten'] + kolom_pilar]
    st.dataframe(df_display, height=550)

# ===== Grafik Ranking =====
st.markdown("---")
st.subheader(f"📊 Ranking {nama_pilar.get(indikator,indikator)}")
df_sorted = df_terpilih[['kabupaten', indikator]].sort_values(by=indikator, ascending=False)
fig = px.bar(df_sorted, x='kabupaten', y=indikator, color=indikator,
             color_continuous_scale='YlGnBu')
fig.update_layout(xaxis_tickangle=-45, height=500, showlegend=False)
st.plotly_chart(fig, use_container_width=True)

# ===== Detail Indikator =====
st.markdown("---")
st.subheader("🔍 Detail Indikator")
kolom_indikator = [c for c in df_terpilih.columns if c.startswith(f"{indikator}_")]
if kolom_indikator:
    tab_mode = st.radio("Mode Tampilan:", ["Per Kabupaten","Per Indikator"], horizontal=True)
    if tab_mode=="Per Kabupaten":
        kab = st.selectbox("Pilih Kabupaten:", sorted(df_terpilih['kabupaten'].unique()))
        data_kab = df_terpilih[df_terpilih['kabupaten']==kab].iloc[0]
        df_ind = pd.DataFrame({
            "Indikator":[c.split("_",2)[2] for c in kolom_indikator],
            "Nilai":[data_kab[c] for c in kolom_indikator]
        })
        st.dataframe(df_ind)
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=df_ind['Nilai'], y=df_ind['Indikator'], orientation='h',
                                 marker=dict(color=df_ind['Nilai'], colorscale='YlGnBu')))
        fig_bar.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        ind_sel = st.selectbox("Pilih Indikator:", kolom_indikator)
        df_ind_all = df_terpilih[['kabupaten', ind_sel]].sort_values(ind_sel, ascending=False)
        st.dataframe(df_ind_all)
        fig_ind = px.bar(df_ind_all, x='kabupaten', y=ind_sel, color=ind_sel,
                         color_continuous_scale='YlGnBu')
        fig_ind.update_layout(xaxis_tickangle=-45, height=500, showlegend=False)
        st.plotly_chart(fig_ind, use_container_width=True)

# ===== Download Excel =====
st.markdown("---")
st.subheader("💾 Download Data")
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

excel_data = to_excel(df_terpilih)
st.download_button("📥 Download Data Excel", excel_data, file_name=f"IDSD_NTT_{tahun}.xlsx", mime="application/vnd.ms-excel")
