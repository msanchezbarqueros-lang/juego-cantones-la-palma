import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json
import os
import streamlit as st
import folium
import streamlit.components.v1 as components
import shapely.geometry as sg
import geopandas as gpd
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ÉPICO "GUANCHE BENAHOARITA"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Épico de Batalla Benahoarita inspirado en la Presentación de la Actividad
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Outfit:wght@400;600;700;800&display=swap');

    /* Fondo principal con gradiente volcánico místico */
    .stApp {
        background: radial-gradient(circle at 50% 20%, #1c2333 0%, #0d1117 60%, #05070a 100%);
        background-attachment: fixed;
        color: #f1f5f9;
        font-family: 'Outfit', -apple-system, sans-serif;
    }

    /* Encabezado Épico de Mencey */
    .header-box {
        background: linear-gradient(135deg, #1f242d 0%, #161b22 50%, #0d1117 100%);
        border: 2px solid #ffd700;
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0px 8px 30px rgba(255, 215, 0, 0.25), inset 0px 0px 20px rgba(0,0,0,0.8);
        position: relative;
        overflow: hidden;
    }
    .header-title {
        color: #ffd700;
        font-family: 'Cinzel', serif;
        font-size: 2.5rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0;
        text-shadow: 3px 3px 6px #000000, 0 0 15px rgba(255, 215, 0, 0.5);
    }
    .header-subtitle {
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 600;
        margin-top: 8px;
        letter-spacing: 1px;
        text-shadow: 1px 1px 3px #000000;
    }

    /* Botones Tácticos de Guerra */
    .stButton > button, div.stButton > button, button[kind="primary"], button[kind="secondary"] {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%) !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 8px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        padding: 10px 20px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
        text-shadow: 1px 1px 2px #000000 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
    }
    .stButton > button:hover, div.stButton > button:hover {
        background: linear-gradient(135deg, #ffd700 0%, #d4af37 100%) !important;
        color: #0a0c10 !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 18px rgba(255, 215, 0, 0.8) !important;
        transform: translateY(-2px);
        text-shadow: none !important;
    }

    /* Formularios, Inputs y Selects */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #161b22 !important;
        border: 1.5px solid #ffd700 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
    }
    input {
        color: #ffffff !important;
        background-color: transparent !important;
        font-weight: bold !important;
    }
    
    /* Selectores de Fecha y Hora con Texto Negro de Alto Contraste */
    div[data-testid="stDateInput"] input, div[data-testid="stTimeInput"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
    }
    label, p, span {
        color: #f1f5f9 !important;
    }

    /* File Uploader (Subida de GPX) */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #161b22 !important;
        border: 2px dashed #ffd700 !important;
        border-radius: 10px !important;
        padding: 18px !important;
    }
    section[data-testid="stFileUploadDropzone"] span {
        color: #ffffff !important;
    }

    /* Pestañas Épicas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(22, 27, 34, 0.9);
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #ffd700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1e27 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        border: 1px solid #30363d !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
        color: #cbd5e1 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffd700 0%, #b8860b 100%) !important;
        border: 1px solid #ffffff !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.5) !important;
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #0a0c10 !important;
        font-weight: 900 !important;
    }

    /* Tarjetas de Métricas (Menceyes) */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #161b22 0%, #0d1117 100%) !important;
        border: 1px solid #ffd700 !important;
        border-left: 6px solid #ffd700 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6) !important;
    }
    div[data-testid="stMetricLabel"] label, div[data-testid="stMetricLabel"] p {
        color: #ffd700 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #12161f !important;
        border-right: 2px solid #ffd700 !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI - La Palma</div>
</div>
""", unsafe_allow_html=True)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# 2. CUENTA ATRÁS DINÁMICA EN TIEMPO REAL (FECHA LÍMITE: 30 MAYO 2027)
# -----------------------------------------------------------------------------
countdown_html = """
<div style="
    background: linear-gradient(135deg, #1f242d 0%, #0d1117 100%);
    border: 2px solid #ffd700;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
">
    <div style="color: #ffd700; font-family: 'Cinzel', serif; font-size: 1rem; font-weight: bold; letter-spacing: 1px; margin-bottom: 4px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTA GPX (Cierre: 30 de Mayo - 23:59)
    </div>
    <div id="timer" style="color: #ffffff; font-size: 1.55rem; font-weight: 800; font-family: monospace;">
        Calculando tiempo...
    </div>
</div>

<script>
    function updateCountdown() {
        const targetDate = new Date("2027-05-30T23:59:59").getTime();
        const now = new Date().getTime();
        const difference = targetDate - now;

        if (difference <= 0) {
            document.getElementById("timer").innerHTML = "🛑 CAMPAÑA FINALIZADA";
            return;
        }

        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        const pad = (n) => n < 10 ? '0' + n : n;

        document.getElementById("timer").innerHTML = 
            "⏳ " + days + " Días | " + pad(hours) + "h : " + pad(minutes) + "m : " + pad(seconds) + "s restantes";
    }

    updateCountdown();
    setInterval(updateCountdown, 1000);
</script>
"""
components.html(countdown_html, height=85)

# -----------------------------------------------------------------------------
# 3. BASE DE DATOS OFICIAL DE LOS 11 ESTUDIANTES
# -----------------------------------------------------------------------------
ESTUDIANTES = {
    "Estrella": {"escudo": "⭐", "titulo": "Estrella de Cima", "color": "#FF0055"},
    "Yassine": {"escudo": "🦅", "titulo": "Águila de Cumbre", "color": "#00E5FF"},
    "Fabián": {"escudo": "⚔️", "titulo": "Lanzas Cruzadas", "color": "#00FF66"},
    "Claudia": {"escudo": "👑", "titulo": "Corona de Mencey", "color": "#FFCC00"},
    "Matías": {"escudo": "🌋", "titulo": "Volcán Tajogaite", "color": "#FF6600"},
    "Yeray": {"escudo": "🛡️", "titulo": "Escudo Táctico", "color": "#AA00FF"},
    "Adrián": {"escudo": "☀️", "titulo": "Sol de Roque", "color": "#76FF03"},
    "Yamila": {"escudo": "🌙", "titulo": "Luna Aborigen", "color": "#00FFCC"},
    "Gabriel": {"escudo": "⚡", "titulo": "Rayo de Cima", "color": "#D500F9"},
    "Juanmi": {"escudo": "🔥", "titulo": "Fuego de Cumbre", "color": "#FF3333"},
    "Paula": {"escudo": "💎", "titulo": "Diamante Guanche", "color": "#3388FF"}
}

# -----------------------------------------------------------------------------
# 4. DEFINICIÓN Y CARGA DE LOS 12 CANTONES BENAHOARITAS
# -----------------------------------------------------------------------------
@st.cache_data
def cargar_cantones_la_palma():
    try:
        gdf = gpd.read_file("cantones_la_palma.geojson")
        return gdf
    except Exception:
        cantones_data = [
            {"canton": "Tagalgen", "municipio": "Garafía", "geometry": sg.box(-17.95, 28.78, -17.85, 28.85)},
            {"canton": "Tagaragre", "municipio": "Barlovento", "geometry": sg.box(-17.85, 28.78, -17.78, 28.84)},
            {"canton": "Adeyahamen", "municipio": "San Andrés y Sauces", "geometry": sg.box(-17.82, 28.70, -17.74, 28.78)},
            {"canton": "Tenagua", "municipio": "Puntallana", "geometry": sg.box(-17.79, 28.65, -17.72, 28.72)},
            {"canton": "Tedote", "municipio": "Santa Cruz / Breñas", "geometry": sg.box(-17.82, 28.58, -17.74, 28.68)},
            {"canton": "Tigalate", "municipio": "Mazo", "geometry": sg.box(-17.84, 28.50, -17.75, 28.60)},
            {"canton": "Ahenguareme", "municipio": "Fuencaliente Sur", "geometry": sg.box(-17.86, 28.44, -17.80, 28.53)},
            {"canton": "Guehevey", "municipio": "Las Manchas / Tamanca", "geometry": sg.box(-17.90, 28.53, -17.82, 28.60)},
            {"canton": "Tahuya", "municipio": "El Paso / Los Llanos Sur", "geometry": sg.box(-17.92, 28.58, -17.84, 28.65)},
            {"canton": "Aridane", "municipio": "Los Llanos / Tazacorte", "geometry": sg.box(-17.96, 28.62, -17.88, 28.68)},
            {"canton": "Tijarafe", "municipio": "Tijarafe / Puntagorda", "geometry": sg.box(-17.98, 28.68, -17.88, 28.78)},
            {"canton": "Aceró", "municipio": "Caldera de Taburiente", "geometry": sg.box(-17.88, 28.66, -17.81, 28.75)},
        ]
        return gpd.GeoDataFrame(cantones_data, crs="EPSG:4326")

# -----------------------------------------------------------------------------
# 5. PROCESAMIENTO DE GPX Y PERSISTENCIA
# -----------------------------------------------------------------------------
def procesar_puntos_gpx(puntos, max_dist_cierre_m=100.0, franja_m=30.0):
    if len(puntos) < 3:
        return None, "Error: GPX con puntos insuficientes", None
        
    linea = sg.LineString(puntos)
    gdf_linea = gpd.GeoDataFrame(geometry=[linea], crs="EPSG:32628" if puntos[0][0] > 1000 else "EPSG:4326")
    if gdf_linea.crs.to_string() != "EPSG:32628":
        gdf_linea = gdf_linea.to_crs("EPSG:32628")
        
    geom_utm = gdf_linea.geometry.iloc[0]
    
    p_inicio = sg.Point(geom_utm.coords[0])
    p_fin = sg.Point(geom_utm.coords[-1])
    
    if p_inicio.distance(p_fin) <= max_dist_cierre_m:
        poligono = sg.Polygon(geom_utm.coords)
        if not poligono.is_valid:
            poligono = poligono.buffer(0)
        geom_conquista = poligono.buffer(5.0)
        tipo = "⭕ Bucle Cerrado (Dominio Interior)"
        es_circular = True
    else:
        geom_conquista = geom_utm.buffer(franja_m)
        tipo = f"🚩 Línea de Incursión ({int(franja_m)}m)"
        es_circular = False
        
    return geom_conquista, tipo, es_circular

def extraer_puntos_gpx(archivo_gpx):
    tree = ET.parse(archivo_gpx)
    root = tree.getroot()
    puntos = []
    for elem in root.iter():
        if elem.tag.endswith('trkpt'):
            lat = float(elem.attrib['lat'])
            lon = float(elem.attrib['lon'])
            puntos.append((lon, lat))
    return puntos

def cargar_actividades_persistentes():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        actividades = []
        for item in data:
            puntos = item.get("puntos", [])
            fecha = datetime.strptime(item["fecha"], "%Y-%m-%d %H:%M")
            if puntos:
                geom, tipo, es_circ = procesar_puntos_gpx(puntos)
                if geom is not None:
                    actividades.append({
                        'alumno': item['alumno'],
                        'fecha': fecha,
                        'geometria_utm': geom,
                        'tipo': tipo,
                        'es_circular': es_circ,
                        'archivo': item.get('archivo', 'actividad.gpx'),
                        'puntos': puntos
                    })
        actividades.sort(key=lambda x: x['fecha'])
        return actividades
    except Exception:
        return []

def guardar_actividades_persistentes(actividades):
    data = []
    for act in actividades:
        data.append({
            'alumno': act['alumno'],
            'fecha': act['fecha'].strftime("%Y-%m-%d %H:%M"),
            'archivo': act.get('archivo', 'actividad.gpx'),
            'puntos': act.get('puntos', [])
        })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'actividades' not in st.session_state:
    st.session_state.actividades = cargar_actividades_persistentes()

# -----------------------------------------------------------------------------
# 6. BARRA LATERAL (CONTROL DOCENTE PROTEGIDO CON PASSWORD)
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DOCENTE")

pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password", help="Introduce la contraseña para gestionar la campaña.")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Profesor Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Registrar Incursión GPX")
    
    alumno_sel = st.sidebar.selectbox("Seleccionar Alumno/a", list(ESTUDIANTES.keys()))
    info_est = ESTUDIANTES[alumno_sel]
    
    st.sidebar.info(f"**Escudo:** {info_est['escudo']} {info_est['titulo']}  \n**Color:** {info_est['color']}")
    
    fecha_ruta = st.sidebar.date_input("Fecha de la Ruta", value=datetime.now())
    hora_ruta = st.sidebar.time_input("Hora de la Ruta", value=datetime.now().time())
    archivo_gpx = st.sidebar.file_uploader("Subir archivo .gpx", type=["gpx"])
    
    if st.sidebar.button("⚡ CONQUISTAR TERRITORIO"):
        if archivo_gpx is not None:
            fecha_completa = datetime.combine(fecha_ruta, hora_ruta)
            puntos = extraer_puntos_gpx(archivo_gpx)
            geom, tipo, es_circ = procesar_puntos_gpx(puntos)
            
            if geom is not None:
                st.session_state.actividades.append({
                    'alumno': alumno_sel,
                    'fecha': fecha_completa,
                    'geometria_utm': geom,
                    'tipo': tipo,
                    'es_circular': es_circ,
                    'archivo': archivo_gpx.name,
                    'puntos': puntos
                })
                st.session_state.actividades.sort(key=lambda x: x['fecha'])
                guardar_actividades_persistentes(st.session_state.actividades)
                st.sidebar.success(f"¡Ruta de {alumno_sel} registrada!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX sin datos válidos.")
        else:
            st.sidebar.warning("Selecciona un archivo GPX.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Reiniciar Campaña"):
        st.session_state.actividades = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.sidebar.success("¡Campaña reiniciada!")
        st.rerun()

else:
    st.sidebar.info("👁️ **Modo Estudiante (Solo Lectura)** - Consulta el mapa de dominio y las clasificaciones en tiempo real.")

# -----------------------------------------------------------------------------
# 7. CÁLCULOS GIS: DOMINIOS ACTUALES, ROBOS Y CANTONES
# -----------------------------------------------------------------------------
def calcular_dominios_actuales():
    dominios = {}
    for act in st.session_state.actividades:
        alumno = act['alumno']
        nueva_geom = act['geometria_utm']
        
        for al in list(dominios.keys()):
            if dominios[al] is not None and not getattr(dominios[al], 'is_empty', True):
                dominios[al] = dominios[al].difference(nueva_geom)
                
        if alumno not in dominios or dominios[alumno] is None or getattr(dominios[alumno], 'is_empty', True):
            dominios[alumno] = nueva_geom
        else:
            dominios[alumno] = dominios[alumno].union(nueva_geom)
            
    return dominios

def calcular_historial_robos_y_cantones(cantones_gdf):
    cantones_utm = cantones_gdf.to_crs("EPSG:32628")
    dominios_previos = {}
    registro = []
    
    total_robado = {al: 0.0 for al in ESTUDIANTES.keys()}
    total_perdido = {al: 0.0 for al in ESTUDIANTES.keys()}
    
    for act in st.session_state.actividades:
        alumno = act['alumno']
        geom = act['geometria_utm']
        
        # Identificar cantones cruzados
        cantones_cruzados = []
        for _, c_row in cantones_utm.iterrows():
            if geom.intersects(c_row['geometry']):
                cantones_cruzados.append(c_row['canton'])
        str_cantones = ", ".join(cantones_cruzados) if cantones_cruzados else "Fuera de Cantón"
        
        # Calcular robos a otros compañeros
        robos_detalle = []
        area_robada_act = 0.0
        
        for rival in list(dominios_previos.keys()):
            if rival != alumno and dominios_previos[rival] is not None and not getattr(dominios_previos[rival], 'is_empty', True):
                interseccion = dominios_previos[rival].intersection(geom)
                a_m2 = interseccion.area
                if a_m2 > 10.0:
                    a_ha = a_m2 / 10000.0
                    a_km2 = a_m2 / 1_000_000.0
                    robos_detalle.append((rival, a_ha, a_km2))
                    area_robada_act += a_km2
                    total_robado[alumno] += a_km2
                    total_perdido[rival] += a_km2
                    
                    dominios_previos[rival] = dominios_previos[rival].difference(geom)
                    
        if alumno not in dominios_previos or dominios_previos[alumno] is None or getattr(dominios_previos[alumno], 'is_empty', True):
            dominios_previos[alumno] = geom
        else:
            dominios_previos[alumno] = dominios_previos[alumno].union(geom)
            
        registro.append({
            'actividad': act,
            'cantones_str': str_cantones,
            'robos_detalle': robos_detalle,
            'area_robada_km2': area_robada_act
        })
        
    return registro, total_robado, total_perdido

def calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf):
    cantones_utm = cantones_gdf.to_crs("EPSG:32628")
    filas = []
    
    for _, canton_row in cantones_utm.iterrows():
        nombre_canton = canton_row['canton']
        geom_canton = canton_row['geometry']
        area_total_canton = geom_canton.area
        
        for alumno, geom_alumno in dominios_utm.items():
            if geom_alumno is not None and not getattr(geom_alumno, 'is_empty', True):
                interseccion = geom_alumno.intersection(geom_canton)
                area_m2 = interseccion.area
            else:
                area_m2 = 0.0
                
            if area_m2 > 0:
                pct = (area_m2 / area_total_canton) * 100
                filas.append({
                    "Cantón": nombre_canton,
                    "Alumno/a": alumno,
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm = calcular_dominios_actuales()
cantones_gdf = cargar_cantones_la_palma()
registro_actividades, total_robado, total_perdido = calcular_historial_robos_y_cantones(cantones_gdf)

# -----------------------------------------------------------------------------
# 8. INTERFAZ PRINCIPAL CON 5 PESTAÑAS DEDICADAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "⚡ CLASIFICACIÓN SEMANAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

# TAB 1: MAPA DE DOMINIO CON ICONOS SEGÚN FORMA DE RUTA
with tab1:
    st.write("### 📍 Mapa Táctico de Dominio Benahoarita")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=10,
        min_zoom=10,
        max_bounds=True,
        tiles="OpenStreetMap"
    )
    
    # Capa de Cantones Benahoaritas
    for _, row in cantones_gdf.iterrows():
        folium.GeoJson(
            sg.mapping(row['geometry']),
            style_function=lambda x: {
                'fillColor': '#f4a261',
                'color': '#e76f51',
                'weight': 1.8,
                'fillOpacity': 0.12,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Municipio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Territorios Conquistados por Alumnos
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            perf = ESTUDIANTES.get(alumno, {"escudo": "🛡️", "color": "#00E5FF"})
            color = perf["color"]
            escudo = perf["escudo"]
            
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=color: {
                    'fillColor': col,
                    'color': col,
                    'weight': 2.5,
                    'fillOpacity': 0.55
                },
                tooltip=f"<b>{escudo} Dominio de:</b> {alumno}<br><b>Superficie Activa:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 4)} km²)"
            ).add_to(m)

    # Ubicación del icono según tipo de ruta (en la línea si es lineal, en el centro si es circular)
    for item in registro_actividades:
        act = item['actividad']
        al = act['alumno']
        puntos = act.get('puntos', [])
        if len(puntos) >= 3:
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️", "color": "#00E5FF"})
            color = perf["color"]
            escudo = perf["escudo"]
            
            linea_gpx = sg.LineString(puntos)
            
            if act.get('es_circular', False):
                poly = sg.Polygon(puntos)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                punto_icon = poly.centroid
            else:
                punto_icon = linea_gpx.interpolate(0.5, normalized=True)
                
            icon_style = "background-color: #0d1117; border: 2.5px solid " + color + "; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-size: 17px; box-shadow: 0 0 10px " + color + ";"
            icon_html = '<div style="' + icon_style + '">' + escudo + '</div>'
            
            folium.Marker(
                location=[punto_icon.y, punto_icon.x],
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"<b>{escudo} {al}</b><br><b>Fecha:</b> {act['fecha'].strftime('%d/%m/%Y %H:%M')}<br><b>Ruta:</b> {act['archivo']}<br><b>Tipo:</b> {act['tipo']}"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

# TAB 2: CLASIFICACIÓN GENERAL (CON LAS 4 COLUMNAS EXACTAS REQUERIDAS)
with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    
    for alumno in ESTUDIANTES.keys():
        geom = dominios_utm.get(alumno, None)
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        area_km2 = area_m2 / 1_000_000.0
        
        perf = ESTUDIANTES[alumno]
        
        ranking_data.append({
            "Guerrero/a": f"{perf['escudo']} {alumno}",
            "Superficie (km²)": round(area_km2, 4),
            "km² que he robado (total)": round(total_robado[alumno], 4),
            "km² que me han robado (total)": round(total_perdido[alumno], 4)
        })
        
    df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (km²)", ascending=False)
    df_ranking.index = range(1, len(df_ranking) + 1)
    st.dataframe(df_ranking, use_container_width=True)

# TAB 3: CLASIFICACIÓN SEMANAL (CON SELECTOR DE SEMANA ACTUAL / ANTERIOR)
with tab3:
    st.write("### ⚡ Clasificación Semanal de Conquista")
    
    hoy = datetime.now()
    semana_actual_num = hoy.isocalendar()[1]
    semana_anterior_num = semana_actual_num - 1 if semana_actual_num > 1 else 52
    
    def obtener_rango_semana(year, week_num):
        primer_dia = datetime.fromisocalendar(year, week_num, 1)
        ultimo_dia = primer_dia + timedelta(days=6)
        return primer_dia, ultimo_dia

    f_ini_act, f_fin_act = obtener_rango_semana(2026, semana_actual_num)
    f_ini_ant, f_fin_ant = obtener_rango_semana(2026, semana_anterior_num)
    
    str_sem_actual = f"Semana {semana_actual_num} ({f_ini_act.strftime('%d %b')} - {f_fin_act.strftime('%d %b 2026')}) [SEMANA ACTUAL]"
    str_sem_anterior = f"Semana {semana_anterior_num} ({f_ini_ant.strftime('%d %b')} - {f_fin_ant.strftime('%d %b 2026')}) [SEMANA ANTERIOR]"
    
    opcion_semana = st.selectbox(
        "📅 Seleccionar Semana de Campaña:",
        [str_sem_anterior, str_sem_actual],
        index=0
    )
    
    sem_elegida_num = semana_anterior_num if opcion_semana == str_sem_anterior else semana_actual_num
    
    act_semana = [act for act in st.session_state.actividades if act['fecha'].isocalendar()[1] == sem_elegida_num]
    
    if act_semana:
        area_sumada_sem = {al: 0.0 for al in ESTUDIANTES.keys()}
        rutas_sem = {al: 0 for al in ESTUDIANTES.keys()}
        
        for act in act_semana:
            al = act['alumno']
            area_sumada_sem[al] += act['geometria_utm'].area
            rutas_sem[al] += 1
            
        filas_sem = []
        for al in ESTUDIANTES.keys():
            m2 = area_sumada_sem[al]
            if m2 > 0:
                perf = ESTUDIANTES[al]
                filas_sem.append({
                    "Guerrero/a": f"{perf['escudo']} {al}",
                    "Hectáreas Sumadas (ha)": round(m2 / 10000.0, 2),
                    "Superficie (m²)": round(m2, 2),
                    "Rutas Realizadas": rutas_sem[al]
                })
                
        if filas_sem:
            df_sem = pd.DataFrame(filas_sem).sort_values(by="Superficie (m²)", ascending=False)
            df_sem.index = range(1, len(df_sem) + 1)
            
            campeon = df_sem.iloc[0]
            st.success(f"🏆 **CAMPEÓN/A DE LA SEMANA:** {campeon['Guerrero/a']} con **{campeon['Hectáreas Sumadas (ha)']} ha** sumadas ({campeon['Rutas Realizadas']} rutas).")
            st.dataframe(df_sem, use_container_width=True)
        else:
            st.info("No hay rutas registradas en la semana seleccionada.")
    else:
        st.info(f"Aún no hay incursiones registradas para la {opcion_semana}.")

# TAB 4: MENCEYES POR CANTÓN
with tab4:
    st.write("### 👑 Menceyes y Señoríos por Cantón")
    df_cantones = calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf)
    
    if not df_cantones.empty:
        cantones_conquistados = df_cantones["Cantón"].unique()
        
        st.write("#### 🤴 Menceyes Actuales de Benahoare")
        cols = st.columns(3)
        for i, cant in enumerate(cantones_conquistados):
            df_sub = df_cantones[df_cantones["Cantón"] == cant].sort_values(by="Superficie (m²)", ascending=False)
            lider = df_sub.iloc[0]
            al_nombre = lider['Alumno/a']
            perf = ESTUDIANTES.get(al_nombre, {"escudo": "👑"})
            
            with cols[i % 3]:
                st.metric(
                    label=f"🏛️ {cant}",
                    value=f"{perf['escudo']} {al_nombre}",
                    delta=f"{lider['Hectáreas (ha)']} ha ({lider['% Conquistado del Cantón']}% del cantón)"
                )
                
        st.markdown("---")
        
        canton_sel = st.selectbox("🔎 Inspeccionar Cantón:", cantones_conquistados)
        df_canton_especifico = df_cantones[df_cantones["Cantón"] == canton_sel].sort_values(by="Superficie (m²)", ascending=False)
        df_canton_especifico.index = range(1, len(df_canton_especifico) + 1)
        
        st.write(f"### Disputa Territorial en **{canton_sel}**")
        st.dataframe(
            df_canton_especifico[["Alumno/a", "Hectáreas (ha)", "% Conquistado del Cantón", "Superficie (m²)"]],
            use_container_width=True
        )
    else:
        st.info("Ningún cantón ha sido conquistado todavía.")

# TAB 5: LIBRO DE GUERRA
with tab5:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    
    if registro_actividades:
        filas_html = ""
        for item in registro_actividades:
            act = item['actividad']
            al = act['alumno']
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️"})
            
            if item['robos_detalle']:
                robos_str_list = [f"<b>{ha:.2f} ha</b> a {ESTUDIANTES.get(r, {}).get('escudo', '')} {r}" for r, ha, _ in item['robos_detalle']]
                str_robos = f"⚔️ <b>{item['actividad']['geometria_utm'].area/10000.0:.2f} ha</b> (" + ", ".join(robos_str_list) + ")"
            else:
                str_robos = "🕊️ 0.00 ha (Sin robos)"
                
            filas_html += f"""
            <tr style="border-bottom: 1px solid #cbd5e1; background-color: #ffffff;">
                <td style="padding: 12px; color: #111111; font-weight: 700;">{act['fecha'].strftime("%Y-%m-%d %H:%M")}</td>
                <td style="padding: 12px; color: #111111; font-weight: 800; font-size: 1.05rem;">{perf['escudo']} {al}</td>
                <td style="padding: 12px; color: #0f172a; font-weight: 600;">📍 {item['cantones_str']}</td>
                <td style="padding: 12px; color: #111111; font-weight: 600;">{str_robos}</td>
                <td style="padding: 12px; color: #334155; font-weight: 600;">{act['tipo']}</td>
                <td style="padding: 12px; color: #0284c7; font-family: monospace; font-size: 0.9rem;"><code>{act['archivo']}</code></td>
            </tr>
            """
            
        tabla_html = f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #ffd700;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            max-height: 520px;
            overflow-y: auto;
        ">
            <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; text-align: left;">
                <thead>
                    <tr style="background-color: #161b22; color: #ffd700; border-bottom: 2px solid #ffd700; position: sticky; top: 0; z-index: 10;">
                        <th style="padding: 12px;">📅 Fecha/Hora</th>
                        <th style="padding: 12px;">👑 Conquistador/a</th>
                        <th style="padding: 12px;">📍 Cantón / Cantones</th>
                        <th style="padding: 12px;">⚔️ Territorio Robado</th>
                        <th style="padding: 12px;">🚩 Tipo de Ruta</th>
                        <th style="padding: 12px;">📁 Archivo GPX</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
        """
        components.html(tabla_html, height=550, scrolling=True)
    else:
        st.info("El historial de guerra está limpio. Registra la primera incursión desde el panel docente.")
