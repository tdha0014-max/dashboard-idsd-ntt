# idsd_dashboard_ntt_jhu_heatmap.py
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np

st.set_page_config(page_title="IDSD NTT Dashboard", layout="wide")
st.title("IDSD NTT Dashboard (Heatmap ala JHU)")

# -----------------------------
# 1. Generate Dummy Data: Semua Kabupaten & 2 Tahun
# -----------------------------
kabupaten_list = [
    "Kupang", "Kupang Kota", "Timor Tengah Selatan", "Timor Tengah Utara", "Belu",
    "Alor", "Lembata", "Flores Timur", "Sikka", "Ende", "Ngada", "Manggarai",
    "Manggarai Timur", "Manggarai Barat", "Rote Ndao", "Sumba Barat", "Sumba Timur",
    "Nagekeo", "Sabu Raijua", "Malaka", "Lautem", "Tetun Timur"
]

rows = []
for tahun in [2023, 2024]:
    for kab in kabupaten_list:
        row = {
            "kabupaten": kab,
            "tahun": tahun,
            "pilar_1": np.random.randint(60,85),
            "pilar_2": np.random.randint(60,85),
            "pilar_3": np.random.randint(60,85),
            "pilar_4": np.random.randint(60,85),
            "pilar_5": np.random.randint(60,85),
            "lon": np.random.uniform(121.5, 125.0),
            "lat": np.random.uniform(-10.5, -8.0)
        }
        rows.append(row)

df = pd.DataFrame(rows)

# -----------------------------
# 2. Sidebar Filter
# -----------------------------
tahun_selected = st.sidebar.selectbox("Pilih Tahun", sorted(df['tahun'].unique()))
kabupaten_selected = st.sidebar.multiselect(
    "Pilih Kabupaten/Kota",
    df['kabupaten'].unique(),
    default=df['kabupaten'].unique()
)
df_filter = df[(df['tahun']==tahun_selected) & (df['kabupaten'].isin(kabupaten_selected))]

# -----------------------------
# 3. KPI per Pilar (Baris Atas)
# -----------------------------
st.markdown("### Skor Rata-rata per Pilar")
pilar_names = ['pilar_1','pilar_2','pilar_3','pilar_4','pilar_5']
cols = st.columns(5)
for i, pilar in enumerate(pilar_names):
    avg_score = df_filter[pilar].mean()
    cols[i].metric(label=f"Pilar {i+1}", value=f"{avg_score:.1f}")

# -----------------------------
# 4. Layout Grid Bawah (Heatmap Kiri, Grafik Kanan)
# -----------------------------
left_col, right_col = st.columns([2,3])

# -----------------------------
# 4a. Heatmap Interaktif (Kiri)
# -----------------------------
with left_col:
    st.markdown("### Heatmap Total Skor Kabupaten")
    df_filter['total_score'] = df_filter[pilar_names].sum(axis=1)
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df_filter,
        get_position='[lon, lat]',
        get_weight='total_score',
        radiusPixels=50,
        intensity=1
    )
    view_state = pdk.ViewState(latitude=-10.2, longitude=123.6, zoom=7)
    r = pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view_state,
        tooltip={"text":"{kabupaten}\nTotal Skor: {total_score}"}
    )
    st.pydeck_chart(r)

# -----------------------------
# 4b. Grafik Tren Pilar (Kanan)
# -----------------------------
with right_col:
    st.markdown("### Tren Skor per Pilar")
    df_plot = df[df['kabupaten'].isin(kabupaten_selected)]
    fig = px.line(df_plot, x='tahun', y=pilar_names,
                  color='kabupaten',
                  labels={'value':'Skor', 'variable':'Pilar', 'tahun':'Tahun'},
                  title="Evolusi Skor Pilar per Tahun per Kabupaten")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 5. Tabel Data Detail
# -----------------------------
st.markdown("### Data Detail Kabupaten")
st.dataframe(df_filter.reset_index(drop=True))
