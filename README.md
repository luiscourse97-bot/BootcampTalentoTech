<div align="center">

# 🚑 **Dashboard Análisis Eficiencia Atención Salud IPS Colombia 2016-2021** 

<br>

![Banner Salud](https://img.shields.io/badge/Salud-Colombia-0066cc?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTIiIGZpbGw9IiMwMDY2Y2MiLz4KPHBhdGggZD0iTTEyIDE4QzE0LjIwOTEgMTggMTYgMTYuMjA5MSAxNiAxNFMyLjIwOTEgMTQgMTIgMTRFMTkgMTQgNy44MDkxIDE0IDYgMTRTMCAxNS44MDkxIDAgMThDMSA4LjY1MjE4IDEgNy4zNDc4MiAxIDEyIDFDMTEuNjUyMiAxIDEzLjM0NzgyIDEgMTQgMVoiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo=)

[![Streamlit](https://img.shields.io/badge/Streamlit-%23FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Datos Abiertos](https://img.shields.io/badge/Datos_Gov-CO-0066CC?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTIgMGM1LjMyIDAgMTIgNC4zNyAxMi0xMkMxMiAxOS41MyA2LjQ3IDI0IDAgMjRjNS41MyAwIDEyLTMgMTItM3M2LjQ3IDMgMTIgMHMtNi40NyAxMi0xMiAxMkM2LjQ3IDI0IDAgMTkuNDcgMCAxMnM1LjQ3LTEyIDEyLTEyWiIgZmlsbD0iI0ZGRkZGRiIvPjwvc3ZnPg==)](https://www.datos.gov.co/)
[![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)

<br><br>

<div style="background: linear-gradient(90deg, #0066cc 0%, #00cc99 100%); padding: 1rem; border-radius: 15px; color: white; text-align: center;">
  <h2>📊 <b>Análisis Interactivo Tiempos de Espera</b> en IPS Colombianas</h2>
  <p><b>Medicina General • Odontología • Triage 2 Urgencias • 2016-2021</b></p>
</div>

[![Launch App](https://img.shields.io/badge/Launch-Streamlit-FF6B35?style=for-the-badge&logo=streamlit&logoColor=white)](https://share.streamlit.io/tu-usuario/app.py)
[![Datos Fuente](https://img.shields.io/badge/Datos-Fuente-0066CC?style=for-the-badge&logo=opencollective&logoColor=white)](https://www.datos.gov.co/api/v3/views/thui-g47e/query.json)

</div>

---

## 🎯 **Introducción**

<div style="display: flex; gap: 1rem; margin: 1rem 0;">
  <span>🚀</span>
  <div>
    <p><b>Dashboard interactivo en Streamlit</b> que analiza la <b>eficiencia y oportunidades</b> en tiempos de espera de servicios de salud en <b>IPS colombianas (2016-2021)</b>.</p>
  </div>
</div>

**Funcionalidades clave:**
- 🔍 Filtros por **departamento, año e IPS**
- 📈 **Gráficos interactivos** con Plotly (líneas, boxplots, heatmaps)
- ⚡ **Métricas en tiempo real** (promedios, máximos)
- 📱 **Responsive design** para análisis móvil

---

## 🎭 **Problemática Identificada**

<div style="background: #fff3cd; padding: 1.5rem; border-left: 5px solid #ffc107; border-radius: 8px; margin: 1rem 0;">

### 🚨 **Impacto de Tiempos de Espera Prolongados**

| **Servicio** | **Problema Detectado** | **Impacto** |
|--------------|----------------------|-------------|
| 🩺 **Medicina General** | Promedios >5 días en 30% IPS | Retrasos diagnósticos |
| 🦷 **Odontología** | Variabilidad regional 200% | Dolor prolongado pacientes |
| 🚑 **Triage 2 Urgencias** | Máximos >12h en picos | Riesgo vital pacientes |

**Dato crítico:** 25% de IPS superan **benchmarks internacionales** de espera.[web:1]

</div>

---

## 🛠️ **Desarrollo del Proyecto**

```mermaid
graph TD
    A[📥 API Datos.gov.co] --> B[🔄 Pandas Limpieza]
    B --> C[🎨 Plotly Visualizaciones]
    C --> D[🌐 Streamlit Dashboard]
    D --> E[🚀 Deploy Streamlit Cloud]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
