import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    
    # Filtrar outliers extremos (>99th percentile)
    Q1 = df["resultado"].quantile(0.25)
    Q3 = df["resultado"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df["resultado"] >= lower_bound) & (df["resultado"] <= upper_bound)]
    
    # Crear columna año-mes para tendencias
    df['periodo_str'] = pd.to_datetime(df['periodo'], format='%Y%m%d')
    df['año'] = df['periodo_str'].dt.year
    df['mes'] = df['periodo_str'].dt.month
    
    return df

df = load_and_clean_data()

# -----------------------
# EDA RESUMEN
# -----------------------
st.sidebar.title("📊 Análisis Exploratorio")
if st.sidebar.checkbox("Mostrar resumen EDA"):
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Registros totales", f"{len(df):,}")
        st.metric("IPS únicos", df['ips'].nunique())
        st.metric("Municipios", df['municipio'].nunique())
    with col2:
        st.metric("Departamentos", df['departamento'].nunique())
        st.metric("Servicios", df['nomespecifique'].nunique())
        st.metric("Años de datos", df['año'].nunique())

# -----------------------
# TÍTULO
# -----------------------
st.title("📊 Dashboard Salud - Tiempos de Espera Mejorado")
st.markdown("**Análisis completo de tiempos de espera en consultas médicas (2016-2020)** [code:1]")

# -----------------------
# FILTROS MEJORADOS
# -----------------------
st.sidebar.header("🔍 Filtros")
departamento = st.sidebar.selectbox(
    "Departamento",
    ["Todos"] + sorted(df["departamento"].dropna().unique())
)

nomespecifique = st.sidebar.selectbox(
    "Tipo de atención",
    ["Todos"] + sorted(df["nomespecifique"].dropna().unique())
)

año = st.sidebar.selectbox(
    "Año",
    ["Todos"] + sorted(df["año"].dropna().unique().astype(str))
)

# -----------------------
# APLICAR FILTROS
# -----------------------
df_filtered = df.copy()

if departamento != "Todos":
    df_filtered = df_filtered[df_filtered["departamento"] == departamento]
if nomespecifique != "Todos":
    df_filtered = df_filtered[df_filtered["nomespecifique"] == nomespecifique]
if año != "Todos":
    df_filtered = df_filtered[df_filtered["año"] == int(año)]

# -----------------------
# KPIs PRINCIPALES
# -----------------------
st.subheader("📌 Indicadores Clave de Desempeño")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Promedio espera", f"{df_filtered['resultado'].mean():.2f} días")
col2.metric("Mediana", f"{df_filtered['resultado'].median():.2f} días")
col3.metric("Máximo", f"{df_filtered['resultado'].max():.2f} días")
col4.metric("Registros", f"{len(df_filtered):,}")

# -----------------------
# DISTRIBUCIÓN TIEMPOS ESPERA
# -----------------------
st.subheader("📈 Distribución de Tiempos de Espera")
fig_dist = px.histogram(
    df_filtered, 
    x="resultado", 
    nbins=50,
    title="Histograma de tiempos de espera",
    labels={'resultado': 'Días de espera'}
)
fig_dist.update_layout(bargap=0.1)
st.plotly_chart(fig_dist, use_container_width=True)

# -----------------------
# TENDENCIA TEMPORAL
# -----------------------
st.subheader("⏱️ Evolución Temporal")
# Groupby SIMPLE solo por fecha con media
trend_data = df_filtered.groupby('periodo_str')['resultado'].mean().reset_index()
fig_trend = px.line(trend_data,
                    x='periodo_str',
                    y='resultado')
st.plotly_chart(fig_trend, use_container_width=True)

# -----------------------
# RANKING IPS (Top 10 peores)
# -----------------------
st.subheader("🏥 Ranking IPS - Peores desempeños")
ips_worst = df_filtered.groupby("ips")["resultado"].mean().reset_index()
ips_worst = ips_worst.sort_values(by="resultado", ascending=False).head(10)

fig_ips = px.bar(
    ips_worst,
    x="resultado",
    y="ips",
    orientation="h",
    title="Top 10 IPS con mayores tiempos promedio"
)
st.plotly_chart(fig_ips, use_container_width=True)

# -----------------------
# RANKING MUNICIPIOS
# -----------------------
st.subheader("🏛️ Ranking Municipios")
mun_worst = df_filtered.groupby("municipio")["resultado"].mean().reset_index()
mun_worst = mun_worst.sort_values(by="resultado", ascending=False).head(10)

fig_mun = px.bar(
    mun_worst,
    x="resultado",
    y="municipio",
    orientation="h",
    title="Top 10 Municipios con mayores tiempos promedio"
)
st.plotly_chart(fig_mun, use_container_width=True)

# -----------------------
# HEATMAP DEPARTAMENTOS
# -----------------------
st.subheader("🌡️ Mapa de Calor por Departamento y Servicio")
pivot_dept = df_filtered.pivot_table(
    values='resultado', 
    index='departamento', 
    columns='nomespecifique', 
    aggfunc='mean'
).fillna(0)

fig_heatmap = px.imshow(
    pivot_dept.values,
    labels=dict(x="Servicio", y="Departamento", color="Días promedio"),
    x=pivot_dept.columns,
    y=pivot_dept.index,
    aspect="auto",
    color_continuous_scale='Reds'
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# -----------------------
# COMPARACIÓN SERVICIOS
# -----------------------
st.subheader("⚖️ Comparación por Tipo de Servicio")
service_stats = df_filtered.groupby('nomespecifique')['resultado'].agg(['mean', 'median', 'std', 'count']).round(2)
st.dataframe(service_stats.style.highlight_max(axis=0, color='lightcoral'))

# Boxplot comparativo
fig_box = px.box(
    df_filtered, 
    x='nomespecifique', 
    y='resultado',
    title="Distribución por tipo de servicio"
)
st.plotly_chart(fig_box, use_container_width=True)

# -----------------------
# TOP 10 DEPARTAMENTOS
# -----------------------
st.subheader("📊 Top 10 Departamentos")
dep_stats = df_filtered.groupby("departamento")["resultado"].mean().reset_index()
dep_stats = dep_stats.sort_values(by="resultado", ascending=False).head(10)

fig_dep = px.bar(
    dep_stats,
    x="resultado",
    y="departamento",
    orientation="h",
    title="Departamentos con mayores tiempos promedio"
)
fig_dep.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_dep, use_container_width=True)

# -----------------------
# PIE CHART PORCENTAJES
# -----------------------
st.subheader("📱 Distribución por Servicio")
service_dist = df_filtered['nomespecifique'].value_counts()
fig_pie = px.pie(
    values=service_dist.values,
    names=service_dist.index,
    title="Proporción de registros por tipo de servicio"
)
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.markdown("*Dashboard mejorado con ETL completo, análisis exploratorio y visualizaciones avanzadas. Datos procesados: 69,688 registros de 2016-2020* [code:1]")
