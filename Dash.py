import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de página
st.set_page_config(
    page_title="Dashboard Tiempos de Espera IPS Colombia",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("🏥 Dashboard Análisis Tiempos de Espera IPS Colombia 2016-2021")
st.markdown("**Eficiencia y Oportunidad en Servicios de Salud: Medicina General, Odontología y Urgencias Triage 2**")

# Sidebar con filtros
st.sidebar.header("🔍 Filtros de Análisis")
departamento = st.sidebar.selectbox("Departamento", df["departamento"].dropna().unique())
ano = st.sidebar.selectbox("Año", sorted(df["ano"].dropna().unique()) if "ano" in df.columns else [2020])
servicio = st.sidebar.multiselect("Servicio", 
    df["nomservicio"].dropna().unique(), 
    default=df["nomservicio"].dropna().unique()
)

# Filtrar datos
df_filtrado = df[
    (df["departamento"] == departamento) & 
    (df["nomservicio"].isin(servicio)) &
    (df["ano"] == ano) if "ano" in df.columns else df[df["departamento"] == departamento]
].copy()

# Columnas 1 y 2: KPIs principales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("⏱️ Promedio Tiempos Espera", 
              f"{df_filtrado['resultado'].mean():.1f} días",
              delta=f"{df_filtrado['resultado'].median():.1f} días (mediana)")

with col2:
    total_atenciones = len(df_filtrado)
    st.metric("📊 Total Atenciones", total_atenciones)

with col3:
    cumplimiento = 100 * (df_filtrado['resultado'] <= 7).sum() / len(df_filtrado)
    st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")

with col4:
    tendencia = df_filtrado['resultado'].std()
    st.metric("📈 Desviación Estándar", f"{tendencia:.1f} días")

# Gráfico 1: Distribución por Municipio (Barra horizontal)
st.subheader("🏛️ Tiempos de Espera por Municipio")
fig1 = px.bar(
    df_filtrado.groupby('municipio')['resultado'].agg(['mean', 'count']).reset_index(),
    x='mean', y='municipio',
    orientation='h',
    title="Tiempo Promedio de Espera por Municipio",
    color='mean',
    color_continuous_scale='RdYlGn_r',
    hover_data=['count']
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Evolución Temporal (Línea)
if "ano" in df.columns:
    st.subheader("📅 Evolución Temporal del Indicador")
    fig2 = px.line(
        df_filtrado.groupby(['ano', 'nomservicio'])['resultado'].mean().reset_index(),
        x='ano', y='resultado',
        color='nomservicio',
        title="Evolución de Tiempos de Espera 2016-2021",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Box Plot por Servicio
st.subheader("📊 Distribución por Tipo de Servicio")
fig3 = px.box(
    df_filtrado, x='nomservicio', y='resultado',
    title="Distribución de Tiempos de Espera por Servicio",
    color='nomservicio',
    points="outliers"
)
st.plotly_chart(fig3, use_container_width=True)

# Gráfico 4: Heatmap Correlación
st.subheader("🔥 Heatmap de Correlaciones")
if len(df_filtrado.columns) > 3:
    corr_cols = df_filtrado.select_dtypes(include=['number']).columns
    fig4 = px.imshow(
        df_filtrado[corr_cols].corr(),
        title="Correlaciones entre Variables Numéricas",
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    st.plotly_chart(fig4, use_container_width=True)

# Tabla Resumen
with st.expander("📋 Tabla Completa de Datos Filtrados"):
    st.dataframe(df_filtrado, use_container_width=True)

# Insights Automáticos
st.subheader("💡 Insights Automáticos")
insights = []
if df_filtrado['resultado'].max() > 30:
    insights.append("⚠️ Se detectan tiempos de espera críticos (>30 días)")
if df_filtrado['resultado'].std() > 10:
    insights.append("📊 Alta variabilidad en los tiempos de atención")
if cumplimiento < 70:
    insights.append("🚨 Bajo cumplimiento del estándar de oportunidad")

for insight in insights:
    st.warning(insight)
