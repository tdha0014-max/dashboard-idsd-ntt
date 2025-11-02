import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import io
import numpy as np

# ===== Streamlit page config =====
st.set_page_config(page_title="Dashboard IDSD NTT", layout="wide")

# ===== Caching =====
@st.cache_data(show_spinner=True)
def load_csv(path):
    return pd.read_csv(path)

@st.cache_data(show_spinner=True)
def load_geojson(path):
    return gpd.read_file(path, driver="GeoJSON")

# ===== Load data =====
csv_path = "data/idsd_data_2023_lengkap.csv"
geojson_path = "data/geojson_kabupaten.geojson"

try:
    df = load_csv(csv_path)
except FileNotFoundError:
    st.warning("CSV data tidak ditemukan, hanya peta yang akan tampil")
    df = pd.DataFrame()

try:
    gdf = load_geojson(geojson_path)
except Exception as e:
    st.error(f"Gagal membaca GeoJSON: {e}")
    st.stop()

# ===== Auto deteksi nama kolom kabupaten =====
geojson_kab_col = [col for col in gdf.columns if col != 'geometry'][0]
st.write(f"GeoJSON kolom kabupaten terdeteksi: {geojson_kab_col}")

# ===== Sidebar filter =====
if not df.empty:
    kabupaten_list = df['kabupaten'].dropna().unique()
    selected_kabupaten = st.sidebar.multiselect("Pilih Kabupaten/Kota", kabupaten_list, default=kabupaten_list)
    filtered_df = df[df['kabupaten'].isin(selected_kabupaten)]
else:
    selected_kabupaten = gdf[geojson_kab_col].unique()
    filtered_df = pd.DataFrame()

filtered_gdf = gdf[gdf[geojson_kab_col].isin(selected_kabupaten)]

# ===== Pilih Pilar =====
pilar_columns = [f'pilar_{i}' for i in range(1, 13) if not df.empty]
selected_pilars = st.sidebar.multiselect(
    "Pilih Pilar untuk Composite",
    pilar_columns,
    default=pilar_columns
) if not df.empty else []

# ===== Hitung skor composite =====
if not filtered_df.empty and selected_pilars:
    filtered_df['skor_composite'] = filtered_df[selected_pilars].mean(axis=1)
else:
    filtered_df['skor_composite'] = np.nan

# ===== Peta =====
m = folium.Map(
    location=[-10, 123],
    zoom_start=8,
    tiles="CartoDB positron",
    control_scale=True
)

if not filtered_df.empty and selected_pilars:
    folium.Choropleth(
        geo_data=filtered_gdf,
        data=filtered_df,
        columns=['kabupaten', 'skor_composite'],
        key_on=f'feature.properties.{geojson_kab_col}',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='Skor Composite'
    ).add_to(m)

# Tooltip interaktif
for _, row in filtered_gdf.iterrows():
    kab = row[geojson_kab_col]
    popup_text = f"<b>{kab}</b><br>"
    if not filtered_df.empty and selected_pilars:
        for pilar in selected_pilars:
            skor = filtered_df.loc[filtered_df['kabupaten']==kab, pilar].values
            if len(skor) > 0:
                popup_text += f"{pilar}: {skor[0]}<br>"
        popup_text += f"<b>Composite: {filtered_df.loc[filtered_df['kabupaten']==kab, 'skor_composite'].values[0]:.2f}</b>"
    folium.CircleMarker(
        location=[row.geometry.centroid.y, row.geometry.centroid.x],
        radius=6,
        color='black',
        fill=True,
        fill_opacity=0.7,
        popup=popup_text
    ).add_to(m)

st_folium(m, width=1000, height=600)

# ===== Tabel & ringkasan =====
if not filtered_df.empty and selected_pilars:
    st.subheader("Data Filtered")
    st.dataframe(filtered_df)

    st.subheader("Ringkasan Statistik Composite")
    st.write(filtered_df[['skor_composite'] + selected_pilars].describe())

    # ===== Export Excel =====
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='CompositeData')
        return output.getvalue()

    excel_data = to_excel(filtered_df)
    st.download_button(
        label="📥 Download Data Filtered (Composite)",
        data=excel_data,
        file_name='idsd_filtered_composite.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
