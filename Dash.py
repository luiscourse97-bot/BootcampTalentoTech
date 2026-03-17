import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
    # Limpiar datos nulos en columna numérica principal
    col_num = df.select_dtypes(include=['number']).columns[0]
    df = df.dropna(subset=[col_num])
    return df

df = load_data()

# Identificar columnas principales
col_cat = df.select_dtypes(include=['object']).columns[0]
col_num = df.select_dtypes(include=['number']).columns[0]

# Sidebar con filtros
st.sidebar.header("🔍 Filtros")
departamento = st.sidebar.selectbox("Departamento", sorted(df[col_cat].dropna().unique()))
df_filtrado = df[df[col_cat] == departamento].copy()

# KPIs Principales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("⏱️ Promedio Tiempos", f"{df_filtrado[col_num].mean():.1f} días")
with col2:
    cumplimiento = (df_filtrado[col_num] <= 7).mean() * 100
    st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")
with col3:
    st.metric("📊 Total Atenciones", len(df_filtrado))
with col4:
    st.metric("📈 Máximo", f"{df_filtrado[col_num].max():.1f} días")

# Row 1: Box Plot y Histograma
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("📦 Distribución Tiempos de Espera")
    fig1 = px.box(df_filtrado, y=col_num, title="Distribución por Departamento")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("📈 Histograma de Frecuencias")
    fig2 = px.histogram(df_filtrado, x=col_num, nbins=30, 
                       title="Frecuencia de Tiempos de Espera")
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Bar Plot y Scatter CORREGIDO
col_c, col_d = st.columns(2)
with col_c:
    st.subheader("🏛️ Promedio por Municipio")
    if 'municipio' in df.columns:
        prom_mun = df_filtrado.groupby('municipio')[col_num].mean().reset_index()
        fig3 = px.bar(prom_mun.head(10), x='municipio', y=col_num,
                     title="Top 10 Municipios")
    else:
        fig3 = px.bar(df_filtrado.groupby(col_cat)[col_num].mean().reset_index(), 
                     x=col_cat, y=col_num, title="Promedio por Categoría")
    st.plotly_chart(fig3, use_container_width=True)

with col_d:
    st.subheader("🎯 Cumplimiento por Servicio")
    # CORREGIDO: Crear columna de color explícita
    df_plot = df_filtrado.copy()
    df_plot['Cumple'] = df_plot[col_num] <= 7
    fig4 = px.scatter(df_plot, x=col_cat, y=col_num, color='Cumple',
                     title="Cumplimiento (Azul=NO cumple, Verde=SI cumple)",
                     color_discrete_map={True: 'green', False: 'red'})
    st.plotly_chart(fig4, use_container_width=True)

# Tabla resumen
with st.expander("📋 Tabla Completa"):
    st.dataframe(df_filtrado, use_container_width=True)

# Insights automáticos
st.subheader("💡 Análisis Automático")
if df_filtrado[col_num].mean() > 15:
    st.error("🚨 **CRÍTICO**: Promedio excede 15 días")
elif df_filtrado[col_num].mean() > 10:
    st.warning("⚠️ Promedio elevado")
else:
    st.success("✅ Tiempos aceptables")
