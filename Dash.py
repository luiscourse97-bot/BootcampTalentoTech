import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de página
st.set_page_config(
    page_title="Tiempos de Espera IPS Colombia",
    page_icon="🏥",
    layout="wide"
)

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_excel("Libro1.xlsx")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("🏥 Dashboard Tiempos de Espera por Servicios de Salud")
st.markdown("**Análisis específico: Medicina General, Odontología General y Urgencias Triage 2**")

# Detectar columna de servicios y tiempos
servicios_col = None
tiempo_col = None

for col in df.columns:
    if any(palabra in col.lower() for palabra in ['servicio', 'tipo', 'especialidad']):
        servicios_col = col
    if any(palabra in col.lower() for palabra in ['resultado', 'tiempo', 'espera']):
        tiempo_col = col

# Servicios específicos de interés
servicios_interes = ['Medicina General', 'Odontología General', 'Urgencias Triage 2']

# Filtrar solo los servicios requeridos
if servicios_col and tiempo_col:
    df_servicios = df[df[servicios_col].isin(servicios_interes)].copy()
    
    if df_servicios.empty:
        # Si no encuentra exactamente, buscar coincidencias parciales
        for idx, row in df.iterrows():
            servicio_nombre = str(row[servicios_col]).lower()
            if any(serv in servicio_nombre for serv in ['medicina', 'odontología', 'urgencia']):
                df_servicios = df.copy()
                break
else:
    # Fallback: usar primeras columnas categórica y numérica
    cat_cols = df.select_dtypes(include=['object']).columns
    num_cols = df.select_dtypes(include=['number']).columns
    if len(cat_cols) > 0 and len(num_cols) > 0:
        servicios_col = cat_cols[0]
        tiempo_col = num_cols[0]
        df_servicios = df.copy()

# Verificar datos válidos
if 'df_servicios' not in locals() or df_servicios.empty:
    st.error("❌ No se encontraron datos de Medicina General, Odontología o Urgencias")
    st.stop()

# KPIs Principales
col1, col2, col3 = st.columns(3)
with col1:
    avg_tiempo = df_servicios[tiempo_col].mean()
    st.metric("⏱️ Promedio General", f"{avg_tiempo:.1f} días")

with col2:
    cumplimiento = 100 * (df_servicios[tiempo_col] <= 7).sum() / len(df_servicios)
    st.metric("✅ Cumplimiento ≤7 días", f"{cumplimiento:.1f}%")

with col3:
    st.metric("📊 Total Registros", len(df_servicios))

# Gráfico 1: Box Plot - Distribución por Servicio
st.subheader("📦 Distribución de Tiempos de Espera por Servicio")
fig1 = px.box(
    df_servicios, 
    x=servicios_col, 
    y=tiempo_col,
    title="Tiempos de Espera: Medicina General vs Odontología vs Urgencias Triage 2",
    color=servicios_col,
    points="outliers+ suspectedoutliers",
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig1.update_layout(height=500)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Bar - Promedio por Servicio
st.subheader("📊 Promedio de Tiempos por Servicio")
promedios = df_servicios.groupby(servicios_col)[tiempo_col].agg(['mean', 'count']).reset_index()
promedios.columns = [servicios_col, 'Promedio', 'Total']

fig2 = px.bar(
    promedios,
    x=servicios_col,
    y='Promedio',
    title="Tiempo Promedio de Espera por Tipo de Servicio",
    text='Promedio',
    color='Promedio',
    color_continuous_scale='RdYlGn_r'
)
fig2.update_traces(texttemplate='%{text:.1f} días', textposition='outside')
fig2.update_layout(height=500)
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Histograma comparativo
st.subheader("📈 Histograma de Frecuencias")
fig3 = px.histogram(
    df_servicios,
    x=tiempo_col,
    color=servicios_col,
    title="Distribución de Tiempos de Espera por Servicio",
    nbins=30,
    opacity=0.7
)
fig3.update_layout(height=500, barmode='overlay')
st.plotly_chart(fig3, use_container_width=True)

# Tabla resumen
with st.expander("📋 Tabla Detallada"):
    st.dataframe(df_servicios.groupby(servicios_col)[tiempo_col].describe().round(2))

# Alertas automáticas
st.subheader("🚨 Estado Crítico")
if avg_tiempo > 15:
    st.error(f"⏰ **CRÍTICO**: Promedio {avg_tiempo:.1f} días excede estándares")
elif avg_tiempo > 10:
    st.warning("⚠️ Promedio elevado, revisar capacidad instalada")
else:
    st.success("✅ Tiempos dentro de parámetros aceptables")
