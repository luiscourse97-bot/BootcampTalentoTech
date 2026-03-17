import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Tiempos de Espera IPS Colombia",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Dashboard Tiempos de Espera por Servicios")
st.markdown("**Medicina General | Odontología General | Urgencias Triage 2**")

# Cargar datos con debug
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    
    # DEBUG: Mostrar estructura de datos
    st.info(f"✅ Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
    st.write("**Columnas disponibles:**")
    for i, col in enumerate(df.columns):
        st.write(f"{i}: '{col}'")
    
    return df

df = load_data()

# Encontrar columna numérica para tiempos (primera columna numérica)
columnas_numericas = df.select_dtypes(include=['number']).columns
if len(columnas_numericas) == 0:
    st.error("❌ No se encontraron columnas numéricas para tiempos de espera")
    st.stop()

col_tiempos = columnas_numericas[0]

# Encontrar columna de servicios (primera categórica)
columnas_categoricas = df.select_dtypes(include=['object']).columns
if len(columnas_categoricas) == 0:
    st.error("❌ No se encontraron columnas categóricas para servicios")
    st.stop()

col_servicios = columnas_categoricas[0]

# Mostrar datos únicos de servicios para debug
st.write(f"**Servicios únicos en '{col_servicios}':** {sorted(df[col_servicios].dropna().unique()[:10])}")

# Gráfico 1: Box Plot - Todos los datos
st.subheader("📦 Distribución Tiempos de Espera")
fig1 = px.box(
    df, 
    x=col_servicios, 
    y=col_tiempos,
    title=f"Tiempos de Espera por {col_servicios}",
    color=col_servicios
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Promedio por servicio
st.subheader("📊 Promedio por Servicio")
promedios = df.groupby(col_servicios)[col_tiempos].mean().reset_index()
promedios.columns = [col_servicios, 'Promedio']

fig2 = px.bar(
    promedios.head(10),  # Solo top 10 para evitar gráficos gigantes
    x=col_servicios, 
    y='Promedio',
    title="Top 10 Servicios - Tiempo Promedio",
    text='Promedio'
)
fig2.update_traces(texttemplate='%{text:.1f}', textposition='outside')
st.plotly_chart(fig2, use_container_width=True)

# KPIs simples
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⏱️ Promedio General", f"{df[col_tiempos].mean():.1f}")
with col2:
    st.metric("📈 Máximo", f"{df[col_tiempos].max():.1f}")
with col3:
    st.metric("📊 Registros", f"{len(df):,}")

# Tabla resumen
with st.expander("📋 Ver primeros 100 registros"):
    st.dataframe(df[[col_servicios, col_tiempos]].head(100))
