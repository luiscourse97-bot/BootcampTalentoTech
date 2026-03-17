import streamlit as st
import pandas as pd
import plotly.express as px

# Cargar datos
df = pd.read_excel("Libro1.xlsx")

# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

st.title("Dashboard Indicadores de Salud")

# Selector de departamento
departamento = st.selectbox(
    "Seleccione Departamento",
    df["departamento"].dropna().unique()
)

# Filtrar datos
df_filtrado = df[df["departamento"] == departamento]

# Gráfico
fig = px.bar(
    df_filtrado,
    x="municipio",
    y="resultado",
    color="nomservicio",
    title="Resultados por Municipio"
)

st.plotly_chart(fig)

# KPI
st.metric(
    "Promedio Indicador",
    round(df_filtrado["resultado"].mean(),2)
)