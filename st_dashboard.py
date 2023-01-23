import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

df_puntos = pd.read_csv("./puntos_dashboard.csv")

df_densidad_relat = pd.read_csv(
    "./data/densidad_relativa/densidad_relat_dashboard.csv", sep=";", index_col=0
)
df_rango_abundancia = pd.read_csv(
    "./data/rango_abundancia/rango_abundancia.csv", sep=";", index_col=0
)
df_regeneracion = pd.read_csv(
    "./data/regeneracion/regeneracion.csv", sep=";", index_col=0
)
df_clases = pd.read_csv("./data/clases_tamaño/histograma_altura_DBH.csv", sep=";")
df_ndvi = pd.read_csv("./data/NDVI/NDVI.csv", sep=";", index_col=0)
df_data = pd.read_csv(
    "./data/tablas/ecl_shannon_erodibilidad.csv", sep=";", index_col=0
)

m = folium.Map(location=[37.28, -3.4], zoom_start=12, tiles="Stamen Terrain")

for point in df_puntos.itertuples():
    estado = df_data[df_data.id_visita == point.id_visita][
        "estado_conservacion_local"
    ].item()

    estado_texto = ""
    color_estado = ""
    if estado < 13:
        estado_texto = "Desforable-malo"
        color_estado = "red"
    elif 13 <= estado <= 26:
        estado_texto = "Desfarable-inadecuado"
        color_estado = "orange"
    elif 26 < estado < 38:
        estado_texto = "Favorable"
        color_estado = "green"
    else:
        estado_texto = "-"

    folium.Marker(
        location=[point.latitude, point.longitude],
        popup=f"Visita {point.id_visita}<br/><br/>"
        + f"<b>Estado de conservación:</b> <font color='{color_estado}'>"
        + f"{estado_texto}</font>",
    ).add_to(m)

st.title("Quejigares del Parque Natural Sierra de Huétor")

col1, col2 = st.columns([2, 1])

with col1:
    folium.LayerControl().add_to(m)
    st_data = st_folium(m, height=550, width=1400)

with col2:
    last_obj = st_data["last_object_clicked"]
    if last_obj:
        lat = last_obj["lat"]
        lon = last_obj["lng"]

        punto = df_puntos[(df_puntos.latitude == lat) & (df_puntos.longitude == lon)][
            "id_visita"
        ].item()

        (
            densidad_relativa,
            rango_abundancia,
            clases_altura,
            clases_diametro_pecho,
            ndvi,
            regeneracion,
            tabla_datos,
        ) = st.tabs(
            [
                "Densidad relativa",
                "Rango abundancia",
                "Clases de altura",
                "Clases DBH",
                "NDVI",
                "Regeneración",
                "Tabla de datos",
            ]
        )

        with densidad_relativa:
            df_densidad_relat_view = df_densidad_relat[
                df_densidad_relat.id_visita == punto
            ]

            c = (
                alt.Chart(df_densidad_relat_view)
                .mark_bar()
                .encode(
                    x=alt.X("cod_especie", sort="-y", title=""),
                    y=alt.Y("densidad_relativa", title="%"),
                )
            )

            st.altair_chart(c, use_container_width=True)

        with rango_abundancia:
            df_rango_abundancia_view = df_rango_abundancia[
                df_rango_abundancia.id_visita == punto
            ]

            c = (
                alt.Chart(df_rango_abundancia_view)
                .mark_bar()
                .encode(
                    x=alt.X("nombre_especie", sort="-y", title=""),
                    y=alt.Y("abundancia_relativa", title="%"),
                )
            )

            st.altair_chart(c, use_container_width=True)

        with clases_altura:
            df_clases_altura_view = df_clases[df_clases.id_visita == punto]

            c = (
                alt.Chart(df_clases_altura_view)
                .mark_bar()
                .encode(
                    x=alt.X("altura_cm", bin=True, title="cm"),
                    y=alt.Y("count()", title="Nº individuos"),
                )
            )

            st.altair_chart(c, use_container_width=True)

        with clases_diametro_pecho:
            df_clases_diametro_pecho_view = df_clases[df_clases.id_visita == punto]

            c = (
                alt.Chart(df_clases_diametro_pecho_view)
                .mark_bar()
                .encode(
                    x=alt.X("DBH_cm", bin=True, title="cm"),
                    y=alt.Y("count()", title="Nº individuos"),
                )
            )

            st.altair_chart(c, use_container_width=True)

        with ndvi:
            df_ndvi_view = (
                df_ndvi[df_ndvi.id_visita == punto]
                .drop("id_visita", axis=1)
                .T.reset_index()
            )
            df_ndvi_view.columns = ["Año", "NDVI"]

            c = (
                alt.Chart(df_ndvi_view)
                .mark_line()
                .encode(
                    x=alt.X("Año", title=""),
                    y=alt.Y(
                        "NDVI",
                        title="",
                        scale=alt.Scale(
                            domain=[
                                df_ndvi_view["NDVI"].min(),
                                df_ndvi_view["NDVI"].max(),
                            ]
                        ),
                    ),
                )
            )

            st.altair_chart(c, use_container_width=True)

        with regeneracion:
            df_regeneracion_view = df_regeneracion[df_regeneracion.id_visita == punto]

            c = (
                alt.Chart(df_regeneracion_view)
                .mark_bar()
                .encode(
                    x=alt.X("cod_especie", sort="-y", title=""),
                    y=alt.Y("N_plantulas", title="Nº plántulas"),
                )
            )

            st.altair_chart(c, use_container_width=True)

        with tabla_datos:
            df_data_view = df_data[df_data.id_visita == punto].T
            df_data_view = df_data_view[1:]

            df_data_view.columns = ["Valor"]
            df_data_view.index = [
                "Estado de conservación local",
                "Índice de Shannon",
                "Movimiento de la capa superficial del suelo (GRT)",
                "Pedregosidad superficial (GRT)",
                "Presencia de regueros (GRT)",
                "Presencia de pedestales de erosión (GRT)",
                "Presencia de una incipiente red de drenaje para el transporte de "
                + "agua y sedimentos (GRT)",
                "Presencia de cárcavas y barrancos (GRT)",
            ]

            st.table(df_data_view)
    else:
        st.markdown("Pulse en un punto para ver su información")

st.markdown(
    "**TFM desarrollado por Estrella Conde Raposo. "
    + "Código disponible en [GitHub](https://github.com/pmagana-ugr/dashboard-quejigal)**"
)
