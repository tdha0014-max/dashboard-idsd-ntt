# ======================
# Import libraries
# ======================
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from branca.colormap import linear
import plotly.express as px

# ======================
# Streamlit page config
# ======================
st.set_page_config(page_title="Peta Interaktif IDSD NTT", layout="wide")
st.title("🗺️ Peta Interaktif IDSD Nusa Tenggara Timur")

# ======================
# Load data
# ======================
# CSV skor pilar
try:
    df_scores = pd.read_csv("data/scores.csv")
except FileNotFoundError:
    st.error("File data/scores.csv tidak ditemukan. Pastikan file ada di folder 'data/'.")
    st.stop()

# GeoJSON kabupaten
try:
    gdf_kab = gpd.read_file("data/geojson_kabupaten.geojson")
except FileNotFoundError:
    st.error("File data/geojson_kabupaten.geojson tidak ditemukan.")
    st.stop()

# ======================
# Gabungkan data
# ======================
gdf = gdf_kab.merge(df_scores, on="kabupaten", how="left")

# ======================
# Peta Folium
# ======================
m = folium.Map(location=[-10.2, 123.6], zoom_start=8)

for _, row in gdf.iterrows():
    folium.GeoJson(
        row["geometry"],
        name=row["kabupaten"],
        tooltip=f"{row['kabupaten']}: Pilar 1={row['pilar_1']}, Pilar 2={row['pilar_2']}, Pilar 3={row['pilar_3']}"
    ).add_to(m)

st.subheader("Peta Kabupaten NTT dengan Skor Pilar IDSD")
st_folium(m, width="stretch")

# ======================
# Statistik ringkas
# ======================
df_scores["total"] = df_scores[["pilar_1", "pilar_2", "pilar_3"]].sum(axis=1)

st.subheader("5 Kabupaten dengan Skor Total Tertinggi")
st.dataframe(df_scores.nlargest(5, "total"), width="stretch")

st.subheader("5 Kabupaten dengan Skor Total Terendah")
st.dataframe(df_scores.nsmallest(5, "total"), width="stretch")

# ======================
# Grafik Plotly
# ======================
st.subheader("Distribusi Skor Pilar")
fig = px.bar(
    df_scores,
    x="kabupaten",
    y=["pilar_1", "pilar_2", "pilar_3"],
    title="Perbandingan Pilar IDSD per Kabupaten",
    barmode="group"
)
st.plotly_chart(fig, use_container_width=True)
