
import os
import pandas as pd
import streamlit as st
from io import BytesIO

# Cargar el archivo de datos
@st.cache_data
def load_data(file):
    try:
        data = pd.read_csv(file, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
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
uploaded_file = st.file_uploader("Sube tu archivo CSV aquí", type=["csv"])

if uploaded_file is not None:
    data = load_data(uploaded_file)

    if data.empty:
        st.warning("La base de datos no se pudo cargar. Verifica que el archivo existe y su formato es correcto.")
    else:
        # Filtros en la barra lateral
        st.sidebar.header("Filtros")

        # Filtro de período de publicación
        period_options = sorted(data["Period of publication"].unique())
        period_filter = st.sidebar.selectbox("Rango de publicación:", ["All"] + period_options)

        # Filtro de citas
        citations_options = sorted(data["Number of Citations"].unique())
        citations_filter = st.sidebar.selectbox("Rango de citas:", ["All"] + citations_options)

        # Filtro de palabras clave
        keywords_options = sorted(data["Keywords"].dropna().unique())
        keywords_filter = st.sidebar.multiselect("Palabras clave:", keywords_options)
        exact_match = st.sidebar.checkbox("Coincidencia exacta", value=False)

        # Filtro de JCR
        jcr_options = ["All", "No Q", "Q1", "Q2", "Q3", "Q4"]
        jcr_filter = st.sidebar.selectbox("Rango JCR:", jcr_options, index=0)

        # Verificar si la columna "Knowledge area group" existe
        if "Knowledge area group" in data.columns:
            knowledge_group_filter = st.sidebar.selectbox("Grupo de área de conocimiento:", ["All"] + list(data["Knowledge area group"].dropna().unique()))
        else:
            knowledge_group_filter = st.sidebar.selectbox("Grupo de área de conocimiento:", ["All"])
            st.warning("La columna 'Knowledge area group' no se encontró en el archivo CSV.")

        # Aplicar filtros
        filtered_data = data.copy()

        # Filtrar por período de publicación
        if period_filter != "All":
            filtered_data = filtered_data[filtered_data["Period of publication"] == period_filter]

        # Filtrar por citas
        if citations_filter != "All":
            filtered_data = filtered_data[filtered_data["Number of Citations"] == citations_filter]

        # Filtrar por palabras clave
        if keywords_filter:
            if exact_match:
                filtered_data = filtered_data[
                    filtered_data["Keywords"].apply(lambda x: all(kw in x.split(",") for kw in keywords_filter) if pd.notna(x) else False)
                ]
            else:
                filtered_data = filtered_data[
                    filtered_data["Keywords"].str.contains('|'.join(keywords_filter), case=False, na=False)
                ]

        # Filtrar por JCR
        if jcr_filter != "All":
            filtered_data = filtered_data[filtered_data["JCR rank"] == jcr_filter]

        # Filtrar por grupo de área de conocimiento
        if knowledge_group_filter != "All" and "Knowledge area group" in data.columns:
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
    st.info("Por favor, sube un archivo CSV para comenzar.")
