
import os
import pandas as pd
import streamlit as st
from io import BytesIO

# Cargar el archivo de datos
@st.cache_data
def load_data(file):
    try:
        data = pd.read_excel(file, engine='openpyxl')
        st.write("Datos cargados correctamente:")
        st.write(data.head())
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# Configuración de la aplicación
st.set_page_config(page_title="Interactive Article Filter", layout="wide")

# Título
st.title("Interactive Article Filter")
st.markdown("Usa los filtros a continuación para explorar y segmentar la base de datos de manera interactiva.")
st.markdown("---")

# Carga dinámica del archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel aquí", type=["xlsx"])

if uploaded_file is not None:
    data = load_data(uploaded_file)

    if data.empty:
        st.warning("La base de datos no se pudo cargar. Verifica que el archivo existe y su formato es correcto.")
    else:
        # Filtros en la barra lateral
        st.sidebar.header("Filtros")

        # Filtro de período de publicación
        period_filter = st.sidebar.slider("Rango de publicación:", 2000, 2025, (2000, 2025))

        # Filtro de citas
        citations_filter = st.sidebar.slider("Rango de citas:", 0, 500, (0, 500))

        # Filtro de palabras clave
        keywords_filter = st.sidebar.text_input("Palabras clave (separadas por comas):", "")
        exact_match = st.sidebar.checkbox("Coincidencia exacta", value=False)

        # Filtro de JCR
        jcr_options = ["All", "No Q", "Q1", "Q2", "Q3", "Q4"]
        jcr_filter = st.sidebar.selectbox("Rango JCR:", jcr_options, index=0)

        # Filtro de área de conocimiento
        knowledge_group_filter = st.sidebar.selectbox("Grupo de área de conocimiento:", ["All"] + list(data["Knowledge area group"].dropna().unique()))

        # Aplicar filtros
        filtered_data = data.copy()

        # Filtrar por período de publicación
        filtered_data = filtered_data[
            (filtered_data["Publication Year"] >= period_filter[0]) &
            (filtered_data["Publication Year"] <= period_filter[1])
        ]

        # Filtrar por citas
        filtered_data = filtered_data[
            (filtered_data["Cited by"] >= citations_filter[0]) &
            (filtered_data["Cited by"] <= citations_filter[1])
        ]

        # Filtrar por palabras clave
        if keywords_filter:
            keywords = [kw.strip() for kw in keywords_filter.split(",")]
            if exact_match:
                filtered_data = filtered_data[
                    filtered_data["Keywords"].apply(lambda x: all(kw in x.split(",") for kw in keywords) if pd.notna(x) else False)
                ]
            else:
                filtered_data = filtered_data[
                    filtered_data["Keywords"].str.contains('|'.join(keywords), case=False, na=False)
                ]

        # Filtrar por JCR
        if jcr_filter != "All":
            filtered_data = filtered_data[filtered_data["JCR rank"] == jcr_filter]

        # Filtrar por grupo de área de conocimiento
        if knowledge_group_filter != "All":
            filtered_data = filtered_data[filtered_data["Knowledge area group"] == knowledge_group_filter]

        # Resultados
        st.subheader("Resumen de resultados")
        if filtered_data.empty:
            st.warning("No se encontraron resultados para los filtros seleccionados.")
        else:
            st.write(f"Total de resultados: {len(filtered_data)}")

            # Mostrar tabla filtrada
            st.subheader("Tabla filtrada")
            st.dataframe(filtered_data)

            # Descargar resultados como Excel
            def convert_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False)
                return output.getvalue()

            st.download_button(
                label="Descargar resultados en Excel",
                data=convert_to_excel(filtered_data),
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Por favor, sube un archivo Excel para comenzar.")
