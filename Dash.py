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

# Cargar datos con manejo de errores
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Libro1.xlsx")
        df.columns = df.columns.str.strip()
        st.success("✅ Datos cargados correctamente")
        return df
    except:
        st.error("❌ Error cargando Libro1.xlsx. Verifica que el archivo esté en la raíz del repositorio.")
        st.stop()

df = load_data()

st.title("🏥 Dashboard Análisis Tiempos de Espera IPS Colombia 2016-2021")
st.markdown("**Eficiencia y Oportunidad: Medicina General, Odontología y Urgencias Triage 2**")

# Verificar columnas disponibles
st.sidebar.subheader("📊 Columnas disponibles:")
for col in df.columns:
    st.sidebar.text(f"• {col}")

# Sidebar con filtros DINÁMICOS basados en columnas reales
st.sidebar.header("🔍 Filtros")

# Filtros seguros - solo columnas que existen
columnas_categoricas = df.select_dtypes(include=['object', 'category']).columns.tolist()
columnas_numericas = df.select_dtypes(include=['number']).columns.tolist()

if columnas_categoricas:
    primer_categorica = columnas_categoricas[0]
    departamento = st.sidebar.selectbox("Departamento/Región", sorted(df[primer_categorica].dropna().unique()))
    
    if len(columnas_categoricas) > 1:
        segunda_categorica = columnas_categoricas[1]
        servicio = st.sidebar.multiselect("Servicio/Tipo", 
                                        df[segunda_categorica].dropna().unique(),
                                        default=df[segunda_categorica].dropna().unique()[:3])
    else:
        servicio = None
else:
    departamento = df.iloc[0][columnas_categoricas[0]] if columnas_categoricas else None
    servicio = None

# Filtrar datos de forma SEGURA
if departamento is not None:
    mask = df[primer_categorica] == departamento
    if servicio and len(servicio) > 0:
        mask &= df[segunda_categorica].isin(servicio)
    df_filtrado = df[mask].copy()
else:
    df_filtrado = df.copy()

# Verificar que hay datos filtrados
if df_filtrado.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados")
    st.stop()

# Columnas para KPIs - usar la primera columna numérica
col_num_principal = columnas_numericas[0] if columnas_numericas else None

if col_num_principal:
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        promedio = df_filtrado[col_num_principal].mean()
        st.metric("⏱️ Promedio Tiempos Espera", 
                  f"{promedio:.1f}", 
                  delta=f"{df_filtrado[col_num_principal].median():.1f} (mediana)")
    
    with col2:
        st.metric("📊 Total Registros", len(df_filtrado))
    
    with col3:
        cumplimiento = 100 * (df_filtrado[col_num_principal] <= 7).sum() / len(df_filtrado)
        st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")
    
    with col4:
        st.metric("📈 Desviación", f"{df_filtrado[col_num_principal].std():.1f}")

# Gráfico 1: Distribución por primera columna categórica
st.subheader("🏛️ Distribución por Municipio/Región")
if len(columnas_categoricas) >= 2:
    grupo1 = columnas_categoricas[1]
    datos_grafico = df_filtrado.groupby(grupo1)[col_num_principal].agg(['mean', 'count']).reset_index()
    datos_grafico.columns = [grupo1, 'Promedio', 'Total']
    
    fig1 = px.bar(
        datos_grafico, 
        x='Promedio', y=grupo1,
        orientation='h',
        title=f"Tiempos Promedio por {grupo1}",
        color='Promedio',
        color_continuous_scale='RdYlGn_r',
        hover_data=['Total']
    )
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Box plot por servicio
st.subheader("📦 Distribución por Tipo de Servicio")
if len(columnas_categoricas) >= 2:
    fig2 = px.box(
        df_filtrado, 
        x=columnas_categoricas[1], 
        y=col_num_principal,
        title=f"Distribución {col_num_principal} por {columnas_categoricas[1]}",
        color=columnas_categoricas[1],
        points="outliers"
    )
    st.plotly_chart(fig2, use_container_width=True)

# Tabla resumen
st.subheader("📋 Datos Filtrados")
st.dataframe(df_filtrado.head(100), use_container_width=True)

# Insights automáticos
if col_num_principal:
    st.subheader("💡 Análisis Automático")
    col1, col2 = st.columns(2)
    
    with col1:
        if df_filtrado[col_num_principal].max() > 30:
            st.error("🚨 Tiempos críticos >30 días detectados")
        if df_filtrado[col_num_principal].std() > 10:
            st.warning("⚠️ Alta variabilidad en tiempos de espera")
    
    with col2:
        if (df_filtrado[col_num_principal] <= 7).mean() * 100 < 70:
            st.error("🚨 Cumplimiento bajo (<70%)")
        else:
            st.success("✅ Buen nivel de cumplimiento")
