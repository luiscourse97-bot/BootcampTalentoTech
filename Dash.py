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

st.title("🏥 Dashboard Tiempos de Espera IPS Colombia 2016-2021")
st.markdown("**Eficiencia y Oportunidad: Medicina General | Odontología | Urgencias Triage 2**")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    col_num = df.select_dtypes(include=['number']).columns[0]
    df = df.dropna(subset=[col_num])
    return df

df = load_data()

# Verificar columnas específicas
columnas_esperadas = ['departamento', 'municipio', 'ips', 'nomservicio']
columnas_existentes = [col for col in columnas_esperadas if col in df.columns]

# Sidebar con filtros múltiples
st.sidebar.header("🔍 Filtros Multi-nivel")
filtros = {}

if 'departamento' in df.columns:
    dept_opts = df['departamento'].dropna().unique()
    filtros['departamento'] = st.sidebar.selectbox("Departamento", dept_opts)

if 'municipio' in df.columns and 'departamento' in filtros:
    mun_opts = df[df['departamento'] == filtros['departamento']]['municipio'].dropna().unique()
    filtros['municipio'] = st.sidebar.multiselect("Municipio", mun_opts)

if 'nomservicio' in df.columns:
    serv_opts = ['Medicina General', 'Odontología General', 'Urgencias Triage 2']
    serv_exist = df['nomservicio'].dropna().unique()
    serv_opts_final = [s for s in serv_opts if any(s in str(x) for x in serv_exist)]
    filtros['servicio'] = st.sidebar.multiselect("Servicio", serv_opts_final, default=serv_opts_final)

# Aplicar filtros
df_filtrado = df.copy()
for col, valor in filtros.items():
    if col == 'departamento':
        df_filtrado = df_filtrado[df_filtrado['departamento'] == valor]
    elif col == 'municipio' and valor:
        df_filtrado = df_filtrado[df_filtrado['municipio'].isin(valor)]
    elif col == 'servicio' and valor:
        df_filtrado = df_filtrado[df_filtrado['nomservicio'].isin(valor)]

# Columna de tiempo
col_tiempo = df.select_dtypes(include=['number']).columns[0]

# KPIs Principales por segmentación
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("⏱️ Promedio General", f"{df_filtrado[col_tiempo].mean():.1f} días")
with col2:
    cumplimiento = (df_filtrado[col_tiempo] <= 7).mean() * 100
    st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")
with col3:
    st.metric("🏥 Total IPS Analizadas", df_filtrado['ips'].nunique() if 'ips' in df.columns else 0)
with col4:
    st.metric("📊 Registros", len(df_filtrado))

# VISUALIZACIÓN 1: Box Plot por Servicio (PRINCIPAL)
st.subheader("📦 Distribución Tiempos de Espera por Servicio")
if 'nomservicio' in df.columns:
    fig1 = px.box(
        df_filtrado, 
        x='nomservicio', 
        y=col_tiempo,
        title="Medicina General vs Odontología vs Urgencias Triage 2",
        color='nomservicio',
        points="outliers"
    )
    fig1.update_layout(height=500)
    st.plotly_chart(fig1, use_container_width=True)

# VISUALIZACIÓN 2: Heatmap Departamento vs Servicio
st.subheader("🔥 Heatmap: Departamento vs Servicio")
if all(col in df_filtrado.columns for col in ['departamento', 'nomservicio']):
    heatmap_data = df_filtrado.groupby(['departamento', 'nomservicio'])[col_tiempo].mean().unstack()
    fig2 = px.imshow(
        heatmap_data,
        title="Tiempo Promedio: Filas=Departamentos, Columnas=Servicios",
        color_continuous_scale='RdYlGn_r',
        aspect="auto"
    )
    st.plotly_chart(fig2, use_container_width=True)

# VISUALIZACIÓN 3: Barra por Municipio (Top 15)
st.subheader("🏛️ Top 15 Municipios por Tiempo Promedio")
if 'municipio' in df_filtrado.columns:
    mun_prom = df_filtrado.groupby('municipio')[col_tiempo].mean().sort_values(ascending=False).head(15)
    fig3 = px.bar(
        mun_prom.reset_index(),
        x='municipio',
        y=col_tiempo,
        title="Municipios con Mayores Tiempos de Espera",
        text=col_tiempo,
        color=col_tiempo,
        color_continuous_scale='Reds'
    )
    fig3.update_traces(texttemplate='%{text:.1f} días', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

# VISUALIZACIÓN 4: Scatter IPS (Tamaño por volumen)
st.subheader("🏥 Rendimiento IPS - Tamaño por Volumen de Atenciones")
if all(col in df_filtrado.columns for col in ['ips', 'municipio']):
    ips_data = df_filtrado.groupby(['ips', 'municipio']).agg({
        col_tiempo: ['mean', 'count']
    }).round(2)
    ips_data.columns = ['Promedio', 'Volumen']
    ips_data = ips_data.reset_index()
    
    fig4 = px.scatter(
        ips_data,
        x='municipio',
        y='Promedio',
        size='Volumen',
        color='Promedio',
        hover_name='ips',
        title="IPS: Tamaño=Volumen Atenciones, Color=Tiempo Promedio",
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig4, use_container_width=True)

# VISUALIZACIÓN 5: Tabla Interactiva Resumen
st.subheader("📊 Tabla Resumen Multi-segmentación")
resumen = df_filtrado.groupby(['departamento', 'municipio', 'nomservicio', 'ips'])[col_tiempo].agg(['mean', 'count']).round(2)
resumen.columns = ['Promedio_días', 'Total_atenciones']
st.dataframe(resumen.sort_values('Promedio_días', ascending=False).head(50), use_container_width=True)

# ALERTAS AUTOMÁTICAS
st.subheader("🚨 Alertas Críticas")
alertas = []
if df_filtrado[col_tiempo].mean() > 15:
    alertas.append("🔴 CRÍTICO: Promedio >15 días")
if (df_filtrado[col_tiempo] > 30).any():
    alertas.append("🔴 Outliers >30 días detectados")
if df_filtrado['ips'].nunique() > 50:
    alertas.append("🟡 Demasiadas IPS - considerar segmentación adicional")

for alerta in alertas:
    st.error(alerta)

if not alertas:
    st.success("✅ Todos los indicadores dentro de parámetros aceptables")
