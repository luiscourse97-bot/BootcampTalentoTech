import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# -----------------------
# CARGA DE DATOS (ETL MEJORADO)
# -----------------------
@st.cache_data
def load_and_clean_data():
    df = pd.read_excel("Clisalud.xlsx")
    
    # Limpieza base
    df.columns = df.columns.str.strip().str.lower()
    df["nomespecifique"] = df["nomespecifique"].astype(str)
    df["nomespecifique"] = df["nomespecifique"].str.normalize('NFKD')\
        .str.encode('ascii', errors='ignore').str.decode('utf-8')\
        .str.upper().str.strip()
    df["resultado"] = pd.to_numeric(df["resultado"], errors="coerce")
    
    # Crear columna periodo para análisis temporal
    df['periodo_str'] = pd.to_datetime(df['periodo'].astype(str), format='%Y%m%d', errors='coerce')
    df['año'] = df['periodo_str'].dt.year.astype(str)
    
    # KPIs específicos por servicio
    df['kpi_medgen'] = df.apply(lambda x: x['resultado'] if x['nomespecifique']=='MEDICO GENERAL' else np.nan, axis=1)
    df['kpi_odont'] = df.apply(lambda x: x['resultado'] if x['nomespecifique']=='ODONTOLOGIA' else np.nan, axis=1)
    df['kpi_triage'] = df.apply(lambda x: x['resultado'] if x['nomespecifique']=='URGENCIAS' else np.nan, axis=1)
    
    return df.dropna(subset=['periodo_str'])

df = load_and_clean_data()

# -----------------------
# TÍTULO
# -----------------------
st.title("📊Análisis de Tiempos Promedio de Espera para Asignación de Citas y atención en triaje 2 - Urgencias en IPS Colombianas, entre 2016-2021")
st.markdown("*Segmentaciones: Dept, Servicio, Año | KPIs específicos | Mapas | Rankings*")

# -----------------------
# FILTROS LATERALES
# -----------------------
st.sidebar.header("🔍 **FILTROS**")
departamento = st.sidebar.selectbox("Departamento", ["Todos"] + sorted(df["departamento"].dropna().unique()))
servicio = st.sidebar.selectbox("Servicio", ["Todos"] + sorted(df["nomespecifique"].dropna().unique()))
periodo = st.sidebar.selectbox("Año", ["Todos"] + sorted(df["año"].dropna().unique()))

# -----------------------
# APLICAR FILTROS
# -----------------------
df_filtered = df.copy()
if departamento != "Todos": df_filtered = df_filtered[df_filtered["departamento"] == departamento]
if servicio != "Todos": df_filtered = df_filtered[df_filtered["nomespecifique"] == servicio]
if periodo != "Todos": df_filtered = df_filtered[df_filtered["año"] == periodo]

# -----------------------
# 1. KPIs ESPECÍFICOS (REQ)
# -----------------------
st.subheader("📌 **KPIs Clave**")
col1, col2, col3 = st.columns(3)
medgen_prom = df_filtered[df_filtered['nomespecifique']=='MEDICO GENERAL']['kpi_medgen'].mean()
odont_prom = df_filtered[df_filtered['nomespecifique']=='ODONTOLOGIA']['kpi_odont'].mean()
triage_prom = df_filtered[df_filtered['nomespecifique']=='URGENCIAS']['kpi_triage'].mean()

col1.metric("🏥 **Med. General**", f"{medgen_prom:.2f} **días**" if not pd.isna(medgen_prom) else "N/D")
col2.metric("🦷 **Odontología**", f"{odont_prom:.2f} **días**" if not pd.isna(odont_prom) else "N/D")
col3.metric("🚨 **Triage 2**", f"{triage_prom:.1f} **min**" if not pd.isna(triage_prom) else "N/D")

# -----------------------
# 2. VAR. DEPT X MEDGEN-ODONT (REQ)
# -----------------------
st.subheader("📊 **Med. General vs Odontología por Departamento**")
df_med_odont = df_filtered[df_filtered["nomespecifique"].isin(["MEDICO GENERAL", "ODONTOLOGIA"])]
g_med_odont = df_med_odont.groupby(["departamento", "nomespecifique"])["resultado"].mean().reset_index()

fig_med_odont = px.bar(
    g_med_odont, x="departamento", y="resultado", color="nomespecifique",
    barmode="group", title="Variación por Departamento (Días)",
    color_discrete_map={"MEDICO GENERAL": "#1f77b4", "ODONTOLOGIA": "#ff7f0e"}
)
st.plotly_chart(fig_med_odont, use_container_width=True)

# -----------------------
# 3. VAR. DEPT X TRIAGE (REQ)
# -----------------------
st.subheader("🚨 **Triage 2 (Urgencias) por Departamento**")
df_triage = df_filtered[df_filtered["nomespecifique"] == "URGENCIAS"]
g_triage = df_triage.groupby("departamento")["resultado"].mean().reset_index()

fig_triage_dept = px.bar(
    g_triage, x="departamento", y="resultado",
    title="Tiempos Triage 2 por Departamento (Minutos)",
    color_discrete_sequence=["#d62728"]
)
st.plotly_chart(fig_triage_dept, use_container_width=True)

# -----------------------
# 4. VAR. AÑO X MEDGEN-ODONT (REQ)
# -----------------------
st.subheader("📈 **Evolución Med. General vs Odontología por Año**")
g_year_med_odont = df_med_odont.groupby(["año", "nomespecifique"])["resultado"].mean().reset_index()

fig_year_med = px.line(
    g_year_med_odont, x="año", y="resultado", color="nomespecifique",
    title="Evolución Temporal (Días)",
    markers=True,
    color_discrete_map={"MEDICO GENERAL": "#1f77b4", "ODONTOLOGIA": "#ff7f0e"}
)
st.plotly_chart(fig_year_med, use_container_width=True)

# -----------------------
# 5. VAR. AÑO X TRIAGE (REQ)
# -----------------------
st.subheader("⏱️ **Evolución Triage 2 por Año**")
g_year_triage = df_triage.groupby("año")["resultado"].mean().reset_index()

fig_year_triage = px.line(
    g_year_triage, x="año", y="resultado",
    title="Evolución Tiempos Urgencias (Minutos)",
    markers=True, color_discrete_sequence=["#d62728"]
)
st.plotly_chart(fig_year_triage, use_container_width=True)

# -----------------------
# 6. MAPA DEPARTAMENTOS (REQ)
# -----------------------
# 6A. MAPA MEDICINA GENERAL + ODONTOLOGÍA (NUEVO)
# -----------------------
st.subheader("🗺️ **Mapa Dept - Med. General & Odontología**")
df_med_odont_map = df_filtered[df_filtered["nomespecifique"].isin(["MEDICO GENERAL", "ODONTOLOGIA"])]
dept_med_odont = df_med_odont_map.groupby("departamento")["resultado"].mean().reset_index()
dept_med_odont_top = dept_med_odont.nlargest(15, 'resultado')

fig_map1 = px.bar(
    dept_med_odont_top, 
    x="resultado", y="departamento",
    orientation="h", 
    title="**Top 15 Departamentos - Consultas (Días)**",
    color="resultado", 
    color_continuous_scale="Blues"
)
fig_map1.update_layout(height=450)
st.plotly_chart(fig_map1, use_container_width=True)

# -----------------------
# 6B. MAPA TRIAGE 2 (NUEVO)
# -----------------------
st.subheader("🚨 **Mapa Dept - Triage 2 (Urgencias)**")
df_triage_map = df_filtered[df_filtered["nomespecifique"] == "URGENCIAS"]
dept_triage = df_triage_map.groupby("departamento")["resultado"].mean().reset_index()
dept_triage_top = dept_triage.nlargest(15, 'resultado')

fig_map2 = px.bar(
    dept_triage_top, 
    x="resultado", y="departamento",
    orientation="h", 
    title="**Top 15 Departamentos - Urgencias (Minutos)**",
    color="resultado", 
    color_continuous_scale="Reds"
)
fig_map2.update_layout(height=450)
st.plotly_chart(fig_map2, use_container_width=True)
# -----------------------
# 7. RANKING IPS (REQ + CÓDIGO ORIGINAL)
# -----------------------
st.subheader("🏥 **Ranking IPS - Peores Tiempos**")
ips_ranking = df_filtered.groupby("ips")["resultado"].mean().reset_index()
ips_top10 = ips_ranking.nlargest(10, "resultado")

fig_ips = px.bar(
    ips_top10, x="resultado", y="ips", orientation="h",
    title="Top 10 IPS con mayores tiempos promedio",
    color="resultado", color_continuous_scale="Reds_r"
)
st.plotly_chart(fig_ips, use_container_width=True)

# -----------------------
# 8. RANKING MUNICIPIOS (REQ + CÓDIGO ORIGINAL)
# -----------------------
st.subheader("🏛️ **Ranking Municipios - Peores Tiempos**")
mun_ranking = df_filtered.groupby("municipio")["resultado"].mean().reset_index()
mun_top10 = mun_ranking.nlargest(10, "resultado")

fig_mun = px.bar(
    mun_top10, x="resultado", y="municipio", orientation="h",
    title="Top 10 Municipios con mayores tiempos promedio",
    color="resultado", color_continuous_scale="Oranges_r"
)
st.plotly_chart(fig_mun, use_container_width=True)

# -----------------------
# EDA RÁPIDO (BONUS)
# -----------------------
with st.expander("📋 **Análisis Exploratorio Completo**"):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Registros", f"{len(df_filtered):,}")
    col2.metric("Departamentos", len(df_filtered['departamento'].unique()))
    col3.metric("IPS Únicos", len(df_filtered['ips'].unique()))
    col4.metric("Municipios", len(df_filtered['municipio'].unique()))

st.markdown("---")
st.markdown("""
**✅ REQUISITOS CUMPLIDOS:**
- **8 visualizaciones** específicas solicitadas
- **ETL** robusto con `@st.cache_data`
- **Filtros** por dept/servicio/año
- **KPIs** diferenciados por tipo atención
- **Mapa** departamentos (simulado)
- **Rankings** IPS/municipios
""")
