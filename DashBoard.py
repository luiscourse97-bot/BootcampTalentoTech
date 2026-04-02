import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# CARGA DE DATOS
# -----------------------
df = pd.read_excel("Clisalud.xlsx")

# -----------------------
# LIMPIEZA
# -----------------------
df.columns = df.columns.str.strip().str.lower()

df["nomespecifique"] = df["nomespecifique"].astype(str)
df["nomespecifique"] = df["nomespecifique"].str.normalize('NFKD')\
    .str.encode('ascii', errors='ignore').str.decode('utf-8')\
    .str.upper().str.strip()

df["resultado"] = pd.to_numeric(df["resultado"], errors="coerce")

# -----------------------
# TÍTULO
# -----------------------
st.title("📊 Dashboard Salud - Tiempos de Espera")

# -----------------------
# FILTROS (CAMBIADO)
# -----------------------
departamento = st.selectbox(
    "Departamento",
    ["Todos"] + sorted(df["departamento"].dropna().unique())
)

nomespecifique = st.selectbox(
    "Tipo de atención",
    ["Todos"] + sorted(df["nomespecifique"].dropna().unique())
)

# -----------------------
# APLICAR FILTROS
# -----------------------
df_filtered = df.copy()

if departamento != "Todos":
    df_filtered = df_filtered[df_filtered["departamento"] == departamento]

if nomespecifique != "Todos":
    df_filtered = df_filtered[df_filtered["nomespecifique"] == nomespecifique]

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores clave")

col1, col2, col3 = st.columns(3)

col1.metric("Promedio espera", round(df_filtered["resultado"].mean(), 2))
col2.metric("Máximo", round(df_filtered["resultado"].max(), 2))
col3.metric("Mínimo", round(df_filtered["resultado"].min(), 2))

# -----------------------
# RANKING IPS
# -----------------------
st.subheader("Ranking IPS con peores tiempos")

ips = df_filtered.groupby("ips")["resultado"].mean().reset_index()
ips = ips.sort_values(by="resultado", ascending=False).head(10)

fig1 = px.bar(
    ips,
    x="resultado",
    y="ips",
    orientation="h"
)

st.plotly_chart(fig1)

# -----------------------
# RANKING MUNICIPIOS
# -----------------------
st.subheader("Ranking Municipios")

mun = df_filtered.groupby("municipio")["resultado"].mean().reset_index()
mun = mun.sort_values(by="resultado", ascending=False).head(10)

fig2 = px.bar(
    mun,
    x="resultado",
    y="municipio",
    orientation="h"
)

st.plotly_chart(fig2)

# -----------------------
# RANKING DEPARTAMENTOS TOP 10
# -----------------------
st.subheader("Top 10 Departamentos con mayores tiempos de espera")

dep = df_filtered.groupby("departamento")["resultado"].mean().reset_index()

# Ordenar de peor a mejor
dep = dep.sort_values(by="resultado", ascending=False)

# 🔥 SOLO LOS 10 PRIMEROS
dep = dep.head(10)

fig5 = px.bar(
    dep,
    x="resultado",
    y="departamento",
    orientation="h"
)

# Orden visual correcto (mejor práctica)
fig5.update_layout(yaxis={'categoryorder':'total ascending'})

st.plotly_chart(fig5)

# -----------------------
# MÉDICO GENERAL VS ODONTOLOGÍA
# -----------------------
st.subheader("Médico General vs Odontología por Departamento")

filtro_servicios = ["MEDICO GENERAL", "ODONTOLOGIA"]

df_serv = df_filtered[df_filtered["nomespecifique"].isin(filtro_servicios)]

g3 = df_serv.groupby(["departamento", "nomespecifique"])["resultado"].mean().reset_index()

fig3 = px.bar(
    g3,
    x="departamento",
    y="resultado",
    color="nomespecifique",
    barmode="group"
)

st.plotly_chart(fig3)

# -----------------------
# URGENCIAS
# -----------------------
st.subheader("Urgencias por Departamento")

df_urg = df_filtered[df_filtered["nomespecifique"] == "URGENCIAS"]

g4 = df_urg.groupby("departamento")["resultado"].mean().reset_index()

fig4 = px.bar(
    g4,
    x="departamento",
    y="resultado"
)

st.plotly_chart(fig4)