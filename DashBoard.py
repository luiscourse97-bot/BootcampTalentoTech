import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# -----------------------
# CARGA DE DATOS (ETL)
# -----------------------
@st.cache_data
def load_and_clean_data():
    df = pd.read_excel("Clisalud.xlsx")
    
    # Limpieza mejorada
    df.columns = df.columns.str.strip().str.lower()
    
    # Normalizar nomespecifique
    df["nomespecifique"] = df["nomespecifique"].astype(str)
    df["nomespecifique"] = df["nomespecifique"].str.normalize('NFKD')\
        .str.encode('ascii', errors='ignore').str.decode('utf-8')\
        .str.upper().str.strip()
    
    # Convertir resultado a numérico
    df["resultado"] = pd.to_numeric(df["resultado"], errors="coerce")
    
    # Filtrar outliers extremos (>99th percentile) - OPCIONAL
    # Q1 = df["resultado"].quantile(0.25)
    # Q3 = df["resultado"].quantile(0.75)
    # IQR = Q3 - Q1
    # lower_bound = Q1 - 1.5 * IQR
    # upper_bound = Q3 + 1.5 * IQR
    # df = df[(df["resultado"] >= lower_bound) & (df["resultado"] <= upper_bound)]
    
    # Crear columna periodo legible para tendencias
    df['periodo_str'] = pd.to_datetime(df['periodo'].astype(str), format='%Y%m%d', errors='coerce')
    df['año'] = df['periodo_str'].dt.year
    df['mes'] = df['periodo_str'].dt.month
    
    # Eliminar filas sin fecha válida
    df = df.dropna(subset=['periodo_str'])
    
    return df

df = load_and_clean_data()

# -----------------------
# TÍTULO Y EDA
# -----------------------
st.title("📊 Dashboard Salud - Tiempos de Espera **CORREGIDO**")
st.markdown("**Análisis completo de tiempos de espera (2016-2020) - 69,688 registros** [code:1]")

# EDA Sidebar
st.sidebar.title("📊 Resumen Datos")
col1, col2 = st.columns(2)
col1.metric("Registros", f"{len(df):,}")
col2.metric("Años", df['año'].nunique())
st.sidebar.metric("Departamentos", df['departamento'].nunique())
st.sidebar.metric("IPS únicos", df['ips'].nunique())

# -----------------------
# FILTROS
# -----------------------
st.sidebar.header("🔍 Filtros")
departamento = st.sidebar.selectbox(
    "Departamento", 
    ["Todos"] + sorted(df["departamento"].dropna().unique().tolist())
)

servicio = st.sidebar.selectbox(
    "Servicio", 
    ["Todos"] + sorted(df["nomespecifique"].dropna().unique().tolist())
)

año = st.sidebar.multiselect(
    "Años", 
    sorted(df["año"].dropna().unique().tolist()),
    default=sorted(df["año"].dropna().unique().tolist())
)

# -----------------------
# APLICAR FILTROS
# -----------------------
df_filtered = df.copy()

if departamento != "Todos":
    df_filtered = df_filtered[df_filtered["departamento"] == departamento]

if servicio != "Todos":
    df_filtered = df_filtered[df_filtered["nomespecifique"] == servicio]

if año:
    df_filtered = df_filtered[df_filtered["año"].isin(año)]

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 KPIs Principales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Promedio", f"{df_filtered['resultado'].mean():.2f} días")
col2.metric("Mediana", f"{df_filtered['resultado'].median():.2f} días")
col3.metric("Desv. Est.", f"{df_filtered['resultado'].std():.2f} días")
col4.metric("Muestras", f"{len(df_filtered):,}")

# -----------------------
# 1. DISTRIBUCIÓN
# -----------------------
st.subheader("📈 Distribución Tiempos")
fig_hist = px.histogram(
    df_filtered, 
    x="resultado", 
    nbins=50,
    title="Histograma de tiempos de espera",
    labels={'resultado': 'Días de espera'}
)
st.plotly_chart(fig_hist, use_container_width=True)

# -----------------------
# 2. TENDENCIA TEMPORAL - CORREGIDA
# -----------------------
st.subheader("⏱️ Evolución Temporal")
trend_data = df_filtered.groupby(['periodo_str', 'año', 'mes'])['resultado'].agg(['mean', 'count']).reset_index()
trend_data['año_mes'] = trend_data['periodo_str'].dt.to_period('M').astype(str)

if len(trend_data) > 0:
    fig_trend = px.line(
        trend_data, 
        x='periodo_str', 
        y='mean',
        title="Evolución promedio mensual",
        labels={'mean': 'Días promedio', 'periodo_str': 'Fecha'}
    )
    fig_trend.update_xaxes(title="Período")
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.warning("No hay datos para mostrar tendencia")

# -----------------------
# 3. RANKING IPS
# -----------------------
st.subheader("🏥 Top 10 IPS (Peores)")
ips_ranking = df_filtered.groupby("ips")["resultado"].mean().reset_index()
ips_top = ips_ranking.nlargest(10, 'resultado')

fig_ips = px.bar(
    ips_top, 
    x="resultado", 
    y="ips", 
    orientation="h",
    title="IPS con mayores tiempos promedio"
)
st.plotly_chart(fig_ips, use_container_width=True)

# -----------------------
# 4. RANKING DEPARTAMENTOS
# -----------------------
st.subheader("📊 Top 10 Departamentos")
dept_ranking = df_filtered.groupby("departamento")["resultado"].mean().reset_index()
dept_top = dept_ranking.nlargest(10, 'resultado')

fig_dept = px.bar(
    dept_top, 
    x="resultado", 
    y="departamento", 
    orientation="h",
    title="Departamentos con mayores tiempos promedio"
)
st.plotly_chart(fig_dept, use_container_width=True)

# -----------------------
# 5. COMPARATIVA SERVICIOS
# -----------------------
st.subheader("⚖️ Comparativa por Servicio")
service_stats = df_filtered.groupby('nomespecifique')['resultado'].agg(['mean','median','count']).round(2)
st.dataframe(service_stats.T.style.format("{:.2f}"))

fig_box = px.box(
    df_filtered, 
    x='nomespecifique', 
    y='resultado',
    title="Boxplot por tipo de servicio"
)
st.plotly_chart(fig_box, use_container_width=True)

# -----------------------
# 6. HEATMAP DEPARTAMENTO-SERVICIO
# -----------------------
st.subheader("🌡️ Heatmap Dept-Servicio")
pivot_heatmap = df_filtered.pivot_table(
    values='resultado', 
    index='departamento', 
    columns='nomespecifique', 
    aggfunc='mean', 
    fill_value=0
).round(2)

fig_heatmap = px.imshow(
    pivot_heatmap.values,
    labels=dict(color="Días promedio"),
    x=pivot_heatmap.columns,
    y=pivot_heatmap.index,
    aspect="auto",
    color_continuous_scale='YlOrRd'
)
fig_heatmap.update_layout(height=600)
st.plotly_chart(fig_heatmap, use_container_width=True)

# -----------------------
# 7. DISTRIBUCIÓN SERVICIOS (PIE)
# -----------------------
col1, col2 = st.columns(2)
with col1:
    st.subheader("📱 % Registros por Servicio")
    service_dist = df_filtered['nomespecifique'].value_counts()
    fig_pie = px.pie(
        values=service_dist.values,
        names=service_dist.index,
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("📋 Tabla Resumen Servicios")
    st.dataframe(service_dist)

st.markdown("---")
st.markdown("*✅ Dashboard corregido y optimizado. ETL robusto + 7 visualizaciones interactivas* [code:1]")
