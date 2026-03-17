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
st.markdown("**Eficiencia y Oportunidad: Medicina | Odontología | Urgencias Triage 2**")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    
    # Verificar que existe columna 'resultado'
    if 'resultado' not in df.columns:
        st.error("❌ Columna 'resultado' no encontrada en el dataset")
        st.stop()
    
    # Limpiar datos nulos en resultado
    df = df.dropna(subset=['resultado'])
    df['resultado'] = pd.to_numeric(df['resultado'], errors='coerce')
    df = df.dropna(subset=['resultado'])
    
    return df

df = load_data()

# Conversión automática: Urgencias en HORAS, otros servicios en DÍAS
def convertir_unidades(row):
    if 'triage 2' in str(row.get('nomservicio', '')).lower() or 'urgencias' in str(row.get('nomservicio', '')).lower():
        return row['resultado'] / 24  # Convertir horas a días para consistencia visual
    return row['resultado']  # Días para medicina y odontología

df['resultado_dias'] = df.apply(convertir_unidades, axis=1)

# Sidebar con filtros específicos
st.sidebar.header("🔍 Filtros Multi-nivel")

# Filtro Departamento
if 'departamento' in df.columns:
    departamentos = sorted(df['departamento'].dropna().unique())
    departamento = st.sidebar.selectbox("Departamento", departamentos)
else:
    departamento = df['departamento'].iloc[0] if 'departamento' in df.columns else None

# Filtro Municipio (cascada)
if 'municipio' in df.columns and departamento:
    municipios = sorted(df[df['departamento'] == departamento]['municipio'].dropna().unique())
    municipios_seleccionados = st.sidebar.multiselect("Municipio", municipios, default=municipios[:3])
else:
    municipios_seleccionados = None

# Filtro Servicio específico
if 'nomservicio' in df.columns:
    servicios_interes = ['Medicina General', 'Odontología General', 'Urgencias Triage 2']
    servicios_disponibles = df['nomservicio'].dropna().unique()
    servicios_filtrados = [s for s in servicios_interes if any(s.lower() in str(x).lower() for x in servicios_disponibles)]
    servicios_seleccionados = st.sidebar.multiselect(
        "Servicio", 
        servicios_filtrados, 
        default=servicios_filtrados
    )
else:
    servicios_seleccionados = None

# Filtro IPS
if 'ips' in df.columns:
    ips_options = df['ips'].dropna().unique()
    ips_seleccionado = st.sidebar.multiselect("IPS", ips_options[:20], default=ips_options[:5])
else:
    ips_seleccionado = None

# Aplicar filtros
df_filtrado = df.copy()

if departamento:
    df_filtrado = df_filtrado[df_filtrado['departamento'] == departamento]

if municipios_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['municipio'].isin(municipios_seleccionados)]

if servicios_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['nomservicio'].isin(servicios_seleccionados)]

if ips_seleccionado:
    df_filtrado = df_filtrado[df_filtrado['ips'].isin(ips_seleccionado)]

# KPIs Principales
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    promedio_general = df_filtrado['resultado_dias'].mean()
    st.metric("⏱️ Promedio General", f"{promedio_general:.1f} días")

with col2:
    cumplimiento = (df_filtrado['resultado_dias'] <= 7).mean() * 100
    st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")

with col3:
    st.metric("🏥 IPS Únicas", df_filtrado['ips'].nunique() if 'ips' in df_filtrado.columns else 0)

with col4:
    st.metric("📊 Registros", f"{len(df_filtrado):,}")

with col5:
    max_tiempo = df_filtrado['resultado_dias'].max()
    st.metric("⚠️ Máximo", f"{max_tiempo:.1f} días")

# VISUALIZACIÓN 1: Box Plot por Servicio (PRINCIPAL)
st.subheader("📦 Distribución Tiempos de Espera por Servicio")
if 'nomservicio' in df_filtrado.columns:
    fig1 = px.box(
        df_filtrado, 
        x='nomservicio', 
        y='resultado_dias',
        title="Tiempos de Espera: Medicina General | Odontología | Urgencias Triage 2",
        color='nomservicio',
        points="outliers",
        labels={'resultado_dias': 'Tiempo (días)'}
    )
    fig1.update_layout(height=500)
    st.plotly_chart(fig1, use_container_width=True)

# VISUALIZACIÓN 2: Heatmap por Departamento-Servicio
st.subheader("🔥 Heatmap: Departamento vs Servicio")
if all(col in df_filtrado.columns for col in ['departamento', 'nomservicio']):
    heatmap_data = df_filtrado.groupby(['departamento', 'nomservicio'])['resultado_dias'].mean().unstack().round(2)
    fig2 = px.imshow(
        heatmap_data,
        title="Tiempo Promedio por Departamento y Servicio",
        color_continuous_scale='RdYlGn_r',
        labels=dict(color='Días promedio')
    )
    st.plotly_chart(fig2, use_container_width=True)

# VISUALIZACIÓN 3: Top 15 Municipios
st.subheader("🏛️ Top 15 Municipios - Tiempo Promedio")
if 'municipio' in df_filtrado.columns:
    mun_stats = df_filtrado.groupby('municipio')['resultado_dias'].agg(['mean', 'count']).round(2)
    mun_stats = mun_stats.sort_values('mean', ascending=False).head(15)
    
    fig3 = px.bar(
        mun_stats.reset_index(),
        x='municipio',
        y='mean',
        title="Municipios con Mayores Demoras",
        text='mean',
        color='mean',
        color_continuous_scale='Reds',
        labels={'mean': 'Días promedio'}
    )
    fig3.update_traces(texttemplate='%{text:.1f} días', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

# VISUALIZACIÓN 4: Rendimiento IPS (Bubble Chart)
st.subheader("🏥 Top IPS por Rendimiento")
if all(col in df_filtrado.columns for col in ['ips', 'nomservicio']):
    ips_stats = df_filtrado.groupby(['ips', 'nomservicio']).agg({
        'resultado_dias': ['mean', 'count']
    }).round(2)
    ips_stats.columns = ['Promedio_dias', 'Volumen']
    ips_stats = ips_stats.reset_index()
    
    fig4 = px.scatter(
        ips_stats.head(100),
        x='nomservicio',
        y='Promedio_dias',
        size='Volumen',
        color='Promedio_dias',
        hover_name='ips',
        title="IPS: Tamaño=Volumen, Color=Tiempo Promedio",
        color_continuous_scale='Viridis',
        labels={'Promedio_dias': 'Días promedio'}
    )
    st.plotly_chart(fig4, use_container_width=True)

# Tabla resumen ejecutiva
st.subheader("📊 Resumen Ejecutivo Multi-segmentación")
if all(col in df_filtrado.columns for col in ['departamento', 'municipio', 'ips', 'nomservicio']):
    resumen = df_filtrado.groupby(['departamento', 'municipio', 'nomservicio', 'ips']).agg({
        'resultado_dias': ['mean', 'count']
    }).round(2)
    resumen.columns = ['Promedio_días', 'Total_citas']
    resumen = resumen.sort_values('Promedio_días', ascending=False).head(20)
    
    st.dataframe(resumen, use_container_width=True)

# ALERTAS AUTOMÁTICAS ESPECÍFICAS
st.subheader("🚨 Alertas Críticas por Servicio")
alertas = []

medicina_data = df_filtrado[df_filtrado['nomservicio'].str.contains('Medicina', na=False)] if 'nomservicio' in df_filtrado else df_filtrado
odontologia_data = df_filtrado[df_filtrado['nomservicio'].str.contains('Odontología', na=False)] if 'nomservicio' in df_filtrado else pd.DataFrame()
urgencias_data = df_filtrado[df_filtrado['nomservicio'].str.contains('Triage|Urgencias', na=False)] if 'nomservicio' in df_filtrado else pd.DataFrame()

if len(medicina_data) > 0 and medicina_data['resultado_dias'].mean() > 10:
    alertas.append("🔴 MEDICINA GENERAL: Promedio >10 días")
if len(odontologia_data) > 0 and odontologia_data['resultado_dias'].mean() > 10:
    alertas.append("🟠 ODONTOLOGÍA: Promedio >10 días")
if len(urgencias_data) > 0 and urgencias_data['resultado_dias'].mean() > 1:
    alertas.append("🚨 URGENCIAS Triage 2: Promedio >24 horas")

for alerta in alertas:
    st.error(alerta)

if not alertas:
    st.success("✅ Todos los servicios dentro de parámetros aceptables")
