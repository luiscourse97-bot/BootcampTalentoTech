import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración de página
st.set_page_config(
    page_title="Dashboard Tiempos de Espera IPS Colombia",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏥 Dashboard Indicadores de Oportunidad IPS Colombia 2016-2021")
st.markdown("""
**Análisis de eficiencia en servicios prioritarios:**
- Tiempo promedio de espera **Medicina General** (días)
- Tiempo promedio de espera **Odontología General** (días)  
- Tiempo promedio de espera **Urgencias Triage 2** (minutos → días)
""")

# Cargar y preparar datos
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    
    # Verificar columnas requeridas
    columnas_requeridas = ['resultado', 'departamento', 'municipio', 'ips', 'nomservicio']
    for col in columnas_requeridas:
        if col not in df.columns:
            st.error(f"❌ Columna '{col}' no encontrada")
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
        elif 'odontología' in servicio or 'odontología' in servicio:
            return 'Odontología General', fila['resultado']  # días
        else:
            return 'Otros', fila['resultado']
    
    df[['servicio_clasificado', 'resultado_dias']] = df.apply(clasificar_servicio, axis=1, result_type='expand')
    
    return df

df = load_data()

# Sidebar - Filtros jerárquicos
st.sidebar.header("🔍 Filtros")

# Filtro Departamento
departamentos = sorted(df['departamento'].dropna().unique())
departamento = st.sidebar.selectbox("Departamento", ['TODOS'] + list(departamentos))

# Filtro Municipio
municipios = df['municipio'].dropna().unique()
if departamento != 'TODOS':
    municipios = df[df['departamento'] == departamento]['municipio'].dropna().unique()
municipios = sorted(municipios)
municipio = st.sidebar.multiselect("Municipio", municipios, default=municipios[:5] if len(municipios)>0 else [])

# Filtro Servicio
servicios = ['Medicina General', 'Odontología General', 'Urgencias Triage 2']
servicio = st.sidebar.multiselect("Servicio", servicios, default=servicios)

# Filtro IPS
ips_options = sorted(df['ips'].dropna().unique())[:50]  # Limitar opciones
ips = st.sidebar.multiselect("IPS", ips_options)

# Aplicar filtros
df_filtrado = df.copy()

if departamento != 'TODOS':
    df_filtrado = df_filtrado[df_filtrado['departamento'] == departamento]
if municipio:
    df_filtrado = df_filtrado[df_filtrado['municipio'].isin(municipio)]
if servicio:
    df_filtrado = df_filtrado[df_filtrado['servicio_clasificado'].isin(servicio)]
if ips:
    df_filtrado = df_filtrado[df_filtrado['ips'].isin(ips)]

# KPIs Principales
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    prom_gen = df_filtrado[df_filtrado['servicio_clasificado']=='Medicina General']['resultado_dias'].mean()
    st.metric("👨‍⚕️ Medicina General", f"{prom_gen:.1f} días" if not pd.isna(prom_gen) else "N/D")

with col2:
    prom_odon = df_filtrado[df_filtrado['servicio_clasificado']=='Odontología General']['resultado_dias'].mean()
    st.metric("🦷 Odontología", f"{prom_odon:.1f} días" if not pd.isna(prom_odon) else "N/D")

with col3:
    prom_urg = df_filtrado[df_filtrado['servicio_clasificado']=='Urgencias Triage 2']['resultado_dias'].mean()
    st.metric("🚨 Urgencias Triage 2", f"{prom_urg:.1f} días ({prom_urg*1440:.0f} min)" if not pd.isna(prom_urg) else "N/D")

with col4:
    cumplimiento = (df_filtrado['resultado_dias'] <= 7).mean() * 100
    st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")

with col5:
    st.metric("🏥 IPS Analizadas", df_filtrado['ips'].nunique())

# Row 1: Comparación Servicios + Heatmap
col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 Distribución por Servicio")
    fig1 = px.box(
        df_filtrado[df_filtrado['servicio_clasificado'].isin(servicios)],
        x='servicio_clasificado', 
        y='resultado_dias',
        title="Distribución Tiempos de Espera",
        color='servicio_clasificado',
        points="outliers"
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🔥 Heatmap Depto-Servicio")
    if len(df_filtrado['departamento'].unique()) <= 20:  # Limitar heatmap
        heatmap_data = df_filtrado.pivot_table(
            values='resultado_dias', 
            index='departamento', 
            columns='servicio_clasificado', 
            aggfunc='mean'
        ).round(2)
        
        fig2 = px.imshow(
            heatmap_data,
            title="Promedio por Departamento-Servicio",
            color_continuous_scale='RdYlGn_r',
            aspect="auto"
        )
        st.plotly_chart(fig2, use_container_width=True)

# Row 2: Municipios + IPS
col3, col4 = st.columns(2)

with col3:
    st.subheader("🏛️ Top 15 Municipios")
    mun_stats = df_filtrado.groupby('municipio')['resultado_dias'].mean().sort_values(ascending=False).head(15)
    fig3 = px.bar(
        mun_stats.reset_index(),
        x='municipio', y='resultado_dias',
        title="Municipios con Mayores Demoras",
        text='resultado_dias',
        color='resultado_dias',
        color_continuous_scale='Reds'
    )
    fig3.update_traces(texttemplate='%{text:.1f}d', textposition='outside')
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("🏥 Top 20 IPS")
    ips_stats = df_filtrado.groupby('ips')['resultado_dias'].agg(['mean', 'count']).sort_values('mean', ascending=False).head(20)
    fig4 = px.scatter(
        ips_stats.reset_index(),
        x='count', y='mean',
        size='count',
        hover_name='ips',
        title="IPS: Tamaño=Volumen, Y=Promedio días",
        labels={'count':'Atenciones', 'mean':'Días promedio'}
    )
    st.plotly_chart(fig4, use_container_width=True)

# Tabla Resumen Ejecutiva
st.subheader("📊 Resumen por IPS-Municipio-Servicio")
resumen = df_filtrado.groupby(['departamento', 'municipio', 'ips', 'servicio_clasificado']).agg({
    'resultado_dias': ['mean', 'count', 'std']
}).round(3)
resumen.columns = ['Promedio_días', 'Volumen', 'Desviación']
resumen = resumen.sort_values('Promedio_días', ascending=False).head(30)

st.dataframe(resumen, use_container_width=True, height=400)

# Análisis Automático
st.subheader("🚨 Evaluación Automática de Oportunidad")

medicina = df_filtrado[df_filtrado['servicio_clasificado']=='Medicina General']
odontologia = df_filtrado[df_filtrado['servicio_clasificado']=='Odontología General']
urgencias = df_filtrado[df_filtrado['servicio_clasificado']=='Urgencias Triage 2']

c1, c2, c3 = st.columns(3)

with c1:
    if len(medicina) > 0:
        color = "🔴" if medicina['resultado_dias'].mean() > 10 else "🟡" if medicina['resultado_dias'].mean() > 7 else "🟢"
        st.metric("Medicina General", f"{medicina['resultado_dias'].mean():.1f} días", delta=f"Estándar: ≤7 días")
    else:
        st.metric("Medicina General", "Sin datos")

with c2:
    if len(odontologia) > 0:
        color = "🔴" if odontologia['resultado_dias'].mean() > 10 else "🟡" if odontologia['resultado_dias'].mean() > 7 else "🟢"
        st.metric("Odontología General", f"{odontologia['resultado_dias'].mean():.1f} días", delta=f"Estándar: ≤7 días")
    else:
        st.metric("Odontología General", "Sin datos")

with c3:
    if len(urgencias) > 0:
        min_promedio = urgencias['resultado_dias'].mean() * 1440
        color = "🔴" if min_promedio > 60 else "🟡" if min_promedio > 30 else "🟢"
        st.metric("Urgencias Triage 2", f"{min_promedio:.0f} min", delta="Estándar: ≤30 min")
    else:
        st.metric("Urgencias Triage 2", "Sin datos")
