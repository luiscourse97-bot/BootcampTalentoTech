import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Dashboard Tiempos de Espera IPS Colombia",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 Dashboard Tiempos de Espera IPS Colombia 2016-2021")
st.markdown("""
**Tres indicadores específicos de oportunidad:**
• **Medicina General** - Tiempo promedio de espera (días)
• **Odontología General** - Tiempo promedio de espera (días)  
• **Urgencias Triage 2** - Tiempo promedio de atención (minutos → días)
""")

# Cargar y preparar datos
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    
    # Verificar columnas requeridas
    for col in ['resultado', 'departamento', 'municipio', 'ips', 'nomservicio']:
        if col not in df.columns:
            st.error(f"❌ Columna '{col}' requerida no encontrada")
            st.stop()
    
    # Limpiar datos
    df = df.dropna(subset=['resultado'])
    df['resultado'] = pd.to_numeric(df['resultado'], errors='coerce')
    df = df.dropna(subset=['resultado'])
    
    # Clasificar servicios y convertir unidades
    def clasificar_servicio(fila):
        servicio = str(fila['nomservicio']).lower()
        if 'triage 2' in servicio or 'urgencias' in servicio:
            return 'Urgencias Triage 2', fila['resultado'] / 1440  # minutos a días
        elif 'medicina' in servicio or 'médico' in servicio:
            return 'Medicina General', fila['resultado']  # días
        elif 'odontología' in servicio:
            return 'Odontología General', fila['resultado']  # días
        else:
            return 'Otros', fila['resultado']
    
    df[['servicio_tipo', 'tiempo_dias']] = df.apply(clasificar_servicio, axis=1, result_type='expand')
    return df

df = load_data()

# Sidebar - Filtros jerárquicos
st.sidebar.header("🔍 Filtros Multi-nivel")

# Filtro Departamento
departamentos = sorted(df['departamento'].dropna().unique())
departamento = st.sidebar.selectbox("Departamento", ['TODOS'] + list(departamentos))

# Filtro Municipio
municipios = sorted(df['municipio'].dropna().unique())
if departamento != 'TODOS':
    municipios = sorted(df[df['departamento'] == departamento]['municipio'].dropna().unique())
municipio = st.sidebar.multiselect("Municipio", municipios[:20])

# Filtro IPS
ips_options = sorted(df['ips'].dropna().unique())[:30]
ips = st.sidebar.multiselect("IPS", ips_options)

# Aplicar filtros
df_filtrado = df.copy()
if departamento != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['departamento'] == departamento]
if municipio:
    df_filtrado = df_filtrado[df_filtrado['municipio'].isin(municipio)]
if ips:
    df_filtrado = df_filtrado[df_filtrado['ips'].isin(ips)]

# KPIs por servicio
col1, col2, col3 = st.columns(3)
servicios = ['Medicina General', 'Odontología General', 'Urgencias Triage 2']

for i, servicio in enumerate(servicios):
    data_serv = df_filtrado[df_filtrado['servicio_tipo'] == servicio]
    if len(data_serv) > 0:
        prom = data_serv['tiempo_dias'].mean()
        with col1 if i==0 else col2 if i==1 else col3:
            unidad = "min" if servicio == 'Urgencias Triage 2' else "días"
            valor = prom*1440 if servicio == 'Urgencias Triage 2' else prom
            st.metric(servicio, f"{valor:.1f} {unidad}", delta=f"N={len(data_serv):,}")

# ============================================================================
# GRÁFICO 1: Box Plot - Distribución por Servicio
st.subheader("📦 1. Distribución Tiempos de Espera por Servicio")
fig1 = px.box(
    df_filtrado[df_filtrado['servicio_tipo'].isin(servicios)],
    x='servicio_tipo',
    y='tiempo_dias',
    title="Distribución completa por tipo de servicio",
    color='servicio_tipo',
    points="outliers",
    labels={'tiempo_dias': 'Tiempo (días)'}
)
fig1.update_layout(height=450, showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# ============================================================================
# GRÁFICO 2: Barras - Promedio por Municipio-Servicio (Heatmap style)
st.subheader("📊 2. Promedio por Municipio y Servicio")
pivot_mun = df_filtrado[df_filtrado['servicio_tipo'].isin(servicios)].pivot_table(
    values='tiempo_dias', 
    index='municipio', 
    columns='servicio_tipo', 
    aggfunc='mean'
).round(2).head(15)  # Top 15 municipios

fig2 = px.imshow(
    pivot_mun,
    title="Heatmap: Tiempo promedio por Municipio-Servicio",
    color_continuous_scale='RdYlGn_r',
    aspect="auto",
    labels=dict(color='Días promedio')
)
fig2.update_layout(height=450)
st.plotly_chart(fig2, use_container_width=True)

# ============================================================================
# GRÁFICO 3: Subplots - Box Plot por Departamento (uno por servicio)
st.subheader("🏛️ 3. Análisis por Departamento")
df_plot = df_filtrado[df_filtrado['servicio_tipo'].isin(servicios)]

fig3 = make_subplots(
    rows=1, cols=3,
    subplot_titles=[
        "Medicina General", 
        "Odontología General", 
        "Urgencias Triage 2"
    ],
    specs=[[{"type": "box"}, {"type": "box"}, {"type": "box"}]]
)

colores = ['#1f77b4', '#ff7f0e', '#2ca02c']

for i, servicio in enumerate(servicios):
    data_serv = df_plot[df_plot['servicio_tipo'] == servicio]
    if len(data_serv) > 0:
        fig3.add_trace(
            go.Box(
                y=data_serv['tiempo_dias'],
                x=data_serv['departamento'],
                name=servicio,
                marker_color=colores[i],
                boxmean=True
            ),
            row=1, col=i+1
        )

fig3.update_layout(height=500, showlegend=False, title_text="Box Plot por Departamento - Tres Servicios")
st.plotly_chart(fig3, use_container_width=True)

# ============================================================================
# Tabla resumen ejecutiva
st.subheader("📋 Resumen Ejecutivo: IPS por Servicio")
resumen = df_filtrado[df_filtrado['servicio_tipo'].isin(servicios)].groupby([
    'departamento', 'municipio', 'ips', 'servicio_tipo'
])['tiempo_dias'].agg(['mean', 'count']).round(2)
resumen.columns = ['Promedio_días', 'N_citas']
resumen = resumen.sort_values('Promedio_días', ascending=False).head(25)

st.dataframe(resumen, use_container_width=True, height=400)

# ============================================================================
# Evaluación automática
st.subheader("🚨 Evaluación de Cumplimiento")

c1, c2, c3 = st.columns(3)
for i, servicio in enumerate(servicios):
    data_serv = df_filtrado[df_filtrado['servicio_tipo'] == servicio]
    if len(data_serv) > 0:
        prom_dias = data_serv['tiempo_dias'].mean()
        if servicio == 'Urgencias Triage 2':
            cumple = prom_dias * 1440 <= 30  # 30 minutos
            estandar = "≤30 min"
        else:
            cumple = prom_dias <= 7
            estandar = "≤7 días"
        
        color = "inverse" if cumple else None
        with c1 if i==0 else c2 if i==1 else c3:
            st.metric(
                f"📊 {servicio}", 
                f"{prom_dias:.2f} días" if servicio != 'Urgencias Triage 2' else f"{prom_dias*1440:.0f} min",
                delta=f"✅ {estandar}" if cumple else f"❌ {estandar}"
            )
