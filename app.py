import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import base64
import os

# Configuración de página en Streamlit
st.set_page_config(
    layout="wide", page_title="Mapa de Recursos Hídricos", page_icon="🗺️")

# --- FUNCIÓN PARA CARGAR IMÁGENES SVG ---


def get_base64_image(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""


# Cargar los SVGs en memoria
logo_b64 = get_base64_image("logo.svg")
slogan_b64 = get_base64_image("slogan.svg")
inferior_b64 = get_base64_image("inferior.svg")

# Crear etiquetas HTML para las imágenes
img_logo = f'<img src="data:image/svg+xml;base64,{logo_b64}" style="height: 60px;">' if logo_b64 else ''
img_slogan = f'<img src="data:image/svg+xml;base64,{slogan_b64}" style="height: 60px;">' if slogan_b64 else ''
img_inferior = f'<img src="data:image/svg+xml;base64,{inferior_b64}" style="height: 50px;">' if inferior_b64 else ''

# ═══════════════════════════════════════════════════════════════════════════════
# ESTILOS CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
.app-header {
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 60%, #40916C 100%);
    color: #fff; padding: 1.2rem 2rem;
    border-radius: 0 0 16px 16px; margin: -3rem -2rem 1.8rem;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 4px 20px rgba(27,67,50,.35);
}
.header-text { text-align: center; flex-grow: 1; }
.header-text h1 { margin:0; font-size:1.75rem; font-weight:700; letter-spacing:-.3px; color: #fff;}
.header-text p { margin:.3rem 0 0; font-size:.88rem; opacity:.82; color: #fff;}
.app-footer {
    text-align:center; padding:1.5rem 0 .4rem;
    font-size:.76rem; color:#adb5bd;
    border-top:1px solid #eee; margin-top:1.8rem;
    display: flex; flex-direction: column; align-items: center; gap: 12px;
}
</style>
""", unsafe_allow_html=True)

# --- RENDERIZAR HEADER ---
st.markdown(f"""
<div class="app-header">
    <div>{img_logo}</div>
    <div class="header-text">
        <h1>🗺️ Mapa de Recursos Hídricos y Accesibilidad</h1>
        <p>Análisis de cuerpos de agua para recolección en incendios forestales · CONAF</p>
    </div>
    <div>{img_slogan}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DEL MAPA
# ═══════════════════════════════════════════════════════════════════════════════


@st.cache_data
def load_geojson(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# Cargamos los datos
cuerpos_perm = load_geojson("permanentes.geojson")
cuerpos_estiv = load_geojson("estivales.geojson")
calles = load_geojson("calles.geojson")
aerodromos = load_geojson("aerodromos.geojson")

# --- CREAR EL MAPA BASE ---
m = folium.Map(location=[-40.60, -72.85], zoom_start=9)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Imagen Satelital',
    overlay=False,
    control=True
).add_to(m)

# 1. Cuerpos Permanentes (Azul) - OPTIMIZADO
folium.GeoJson(
    cuerpos_perm,
    name="Cuerpos Permanentes (Invierno/Todo el año)",
    smooth_factor=2.0,  # <-- Simplifica la geometría al alejar el mapa
    style_function=lambda x: {'fillColor': 'blue',
                              'color': 'blue', 'weight': 1, 'fillOpacity': 0.7}
).add_to(m)

# 2. Cuerpos Estivales (Rojo) - OPTIMIZADO
folium.GeoJson(
    cuerpos_estiv,
    name="Cuerpos Estivales (Solo Verano)",
    smooth_factor=2.0,  # <-- Simplifica la geometría al alejar el mapa
    style_function=lambda x: {'fillColor': 'red',
                              'color': 'red', 'weight': 1, 'fillOpacity': 0.7}
).add_to(m)

# 3. Calles - OPTIMIZADO
folium.GeoJson(
    calles,
    name="Calles y Caminos",
    smooth_factor=1.5,
    style_function=lambda x: {
        'color': '#bab972', 'weight': 1.2, 'opacity': 0.5}
).add_to(m)

# 4. Aeródromos y Aeropuertos
folium.GeoJson(
    aerodromos,
    name="Aeródromos y Aeropuertos",
    marker=folium.Marker(
        icon=folium.Icon(icon='plane', prefix='fa',
                         color='orange', icon_color='white')
    )
).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# --- MOSTRAR EN STREAMLIT OPTIMIZADO ---
# returned_objects=[] evita que Streamlit colapse tratando de leer los datos de clics
st_data = st_folium(m, use_container_width=True,
                    height=700, returned_objects=[])

# --- RENDERIZAR FOOTER ---
st.markdown(f"""
<div class="app-footer">
    <div>{img_inferior}</div>
    <div>Mapa de Recursos Hídricos y Accesibilidad · Chile 2026 · CONAF · Autor: Alumno en Práctica Francisco Vidal</div>
</div>
""", unsafe_allow_html=True)
