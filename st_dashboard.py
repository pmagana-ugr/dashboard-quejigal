import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

df_puntos = pd.read_csv("./puntos_dashboard.csv")

df_densidad_relat = pd.read_csv(
    "./data/densidad_relativa/densidad_relat_dashboard.csv", sep=";"
)
df_rango_abundancia = pd.read_csv(
    "./data/rango_abundancia/rango_abundancia.csv", sep=";"
)

m = folium.Map(location=[37.28, -3.4], zoom_start=12, tiles="Stamen Terrain")
for point in df_puntos.itertuples():
    folium.Marker(
        location=[point.latitude, point.longitude],
        popup=f"Visita {point.id_visita}",
    ).add_to(m)

st.title("Caracterización de los quejigares del Parque Natural de la Sierra de Huétor")

col1, col2 = st.columns([2, 1])

with col1:
    st_data = st_folium(m, height=600, width=1400)

with col2:
    last_obj = st_data["last_object_clicked"]
    if last_obj:
        lat = last_obj["lat"]
        lon = last_obj["lng"]

        punto = df_puntos[(df_puntos.latitude == lat) & (df_puntos.longitude == lon)][
            "id_visita"
        ].item()

        densidad_relativa, rango_abundancia = st.tabs(
            ["Densidad relativa", "Rango abundancia"]
        )

        with densidad_relativa:
            df_densidad_relat_view = df_densidad_relat[
                df_densidad_relat.id_visita == punto
            ]

            c = (
                alt.Chart(df_densidad_relat_view)
                .mark_bar()
                .encode(x="cod_especie", y="densidad_relativa")
            )

            st.altair_chart(c, use_container_width=True)

        with rango_abundancia:
            df_rango_abundancia_view = df_rango_abundancia[
                df_rango_abundancia.id_visita == punto
            ]

            c = (
                alt.Chart(df_rango_abundancia_view)
                .mark_bar()
                .encode(x=alt.X("nombre_especie", sort="-y"), y="abundancia_relativa")
            )

            st.altair_chart(c, use_container_width=True)
