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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO ÉPICO TÁCTICO "BEN AHOARE"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Oscuro con Rediseño de Alto Contraste para los Controles del Profesor
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&family=Outfit:wght@400;600;700;800&display=swap');

    /* Fondo principal y fuentes */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1c2333 0%, #0d1117 60%, #05070a 100%);
        color: #ffffff;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Encabezado Épico */
    .header-box {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(33, 38, 45, 0.95) 100%);
        border: 2px solid #ffd700;
        border-radius: 14px;
        padding: 22px;
        text-align: center;
        margin-bottom: 22px;
        box-shadow: 0px 6px 20px rgba(255, 215, 0, 0.3), inset 0 0 15px rgba(255, 215, 0, 0.1);
    }
    .header-title {
        color: #ffd700;
        font-family: 'Cinzel', serif;
        font-size: 2.3rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0;
        text-shadow: 3px 3px 6px #000000;
    }
    .header-subtitle {
        color: #e6edf3;
        font-size: 1.05rem;
        margin-top: 6px;
        font-weight: 600;
    }

    /* REDISEÑO EXCLUSIVO DEL MENÚ Y CONTROLES DEL PROFESOR (ALTO CONTRASTE) */
    
    /* Etiqueta y Título del Panel Docente */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: #ffd700 !important;
        font-family: 'Cinzel', serif !important;
        text-shadow: 1px 1px 3px #000000 !important;
    }

    /* Todos los inputs, passwords, selects y pickers del profesor */
    section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 2px solid #ffd700 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
    }

    /* Texto dentro de los cuadros de texto, contraseña y desplegables */
    section[data-testid="stSidebar"] input,
    div[data-testid="stSelectbox"] input,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }

    /* REDISEÑO ESPECÍFICO DE FECHA Y HORA (FECHA DE LA RUTA Y HORA DE LA RUTA) */
    div[data-testid="stDateInput"] > div,
    div[data-testid="stTimeInput"] > div {
        background-color: #ffffff !important;
        border: 2.5px solid #ffd700 !important;
        border-radius: 8px !important;
        padding: 2px !important;
        box-shadow: 0 3px 8px rgba(255, 215, 0, 0.4) !important;
    }
    
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 1.15rem !important;
        letter-spacing: 0.5px !important;
        text-align: center !important;
    }

    /* Iconos del Calendario y Reloj */
    div[data-testid="stDateInput"] svg,
    div[data-testid="stTimeInput"] svg {
        fill: #000000 !important;
        color: #000000 !important;
        stroke: #000000 !important;
    }

    /* Etiquetas de los formularios (Labels) */
    section[data-testid="stSidebar"] label,
    div[data-testid="stSelectbox"] label {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        text-shadow: 1px 1px 2px #000000 !important;
        margin-bottom: 4px !important;
    }

    /* Botones tácticos en la barra lateral y cuerpo */
    .stButton > button, div.stButton > button, button[kind="primary"], button[kind="secondary"] {
        background: linear-gradient(135deg, #21262d 0%, #161b22 100%) !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 8px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        padding: 10px 18px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
    }
    .stButton > button:hover, div.stButton > button:hover {
        background: #ffd700 !important;
        color: #0d1117 !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 215, 0, 0.8) !important;
        transform: translateY(-1px) !important;
    }

    /* File Uploader (Subida de GPX) */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2.5px dashed #ffd700 !important;
        border-radius: 10px !important;
        padding: 18px !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.4) !important;
    }
    section[data-testid="stFileUploadDropzone"] span,
    section[data-testid="stFileUploadDropzone"] div,
    section[data-testid="stFileUploadDropzone"] p,
    section[data-testid="stFileUploadDropzone"] small {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    section[data-testid="stFileUploadDropzone"] button {
        background-color: #0d1117 !important;
        color: #ffd700 !important;
        border: 1.5px solid #ffd700 !important;
        font-weight: bold !important;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #161b22;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
    }
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
        color: #ffffff !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ffd700 0%, #ffae00 100%) !important;
        border: 1px solid #ffffff !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.6) !important;
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #0d1117 !important;
        font-weight: 900 !important;
    }

    /* Tarjetas de Métricas (Menceyes) */
    div[data-testid="stMetric"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-left: 5px solid #ffd700 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.6) !important;
    }
    div[data-testid="stMetricLabel"] label, div[data-testid="stMetricLabel"] p {
        color: #ffd700 !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricValue"] div {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
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
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    margin-bottom: 22px;
    box-shadow: 0 0 14px rgba(255, 215, 0, 0.35);
">
    <div style="color: #ffd700; font-family: 'Cinzel', serif; font-size: 1rem; font-weight: 800; letter-spacing: 1.5px; margin-bottom: 4px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTA GPX (Cierre: 30 de Mayo - 23:59)
    </div>
    <div id="timer" style="color: #ffffff; font-size: 1.6rem; font-weight: 900; font-family: monospace;">
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
components.html(countdown_html, height=90)

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
    "Adrián": {"escudo": "🐂", "titulo": "La Cuadra Pichichi", "color": "#76FF03"},
    "Yamila": {"escudo": "🌙", "titulo": "Luna Aborigen", "color": "#00FFCC"},
    "Gabriel": {"escudo": "🌌", "titulo": "Subiendo a la Cima", "color": "#D500F9"},
    "Juanmi": {"escudo": "🏃🏽⚡️", "titulo": "El Polvacera", "color": "#FF3333"},
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
    gdf_linea = gpd.GeoDataFrame(geometry=[linea], crs="EPSG:4326").to_crs("EPSG:32628")
    geom_utm = gdf_linea.geometry.iloc[0]
    
    p_inicio = sg.Point(geom_utm.coords[0])
    p_fin = sg.Point(geom_utm.coords[-1])
    
    if p_inicio.distance(p_fin) <= max_dist_cierre_m:
        poligono = sg.Polygon(geom_utm.coords)
        if not poligono.is_valid:
            poligono = poligono.buffer(0)
        geom_conquista = poligono.buffer(5.0)
        tipo = "⭕ Bucle Cerrado (Dominio Interior)"
    else:
        geom_conquista = geom_utm.buffer(franja_m)
        tipo = f"🚩 Línea de Incursión ({int(franja_m)}m)"
        
    return geom_conquista, tipo, geom_utm

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
                geom, tipo, geom_linea = procesar_puntos_gpx(puntos)
                if geom is not None:
                    actividades.append({
                        'alumno': item['alumno'],
                        'fecha': fecha,
                        'geometria_utm': geom,
                        'geometria_linea_utm': geom_linea,
                        'tipo': tipo,
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
            geom, tipo, geom_linea = procesar_puntos_gpx(puntos)
            
            if geom is not None:
                st.session_state.actividades.append({
                    'alumno': alumno_sel,
                    'fecha': fecha_completa,
                    'geometria_utm': geom,
                    'geometria_linea_utm': geom_linea,
                    'tipo': tipo,
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

# -----------------------------------------------------------------------------------------
# 7. CÁLCULO DE SOLAPAMIENTOS, RE-CONQUISTAS Y ESTADÍSTICAS GLOBALES DE ROBOS DE TERRITORIO
# -----------------------------------------------------------------------------------------
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

def calcular_estadisticas_robos_globales():
    """Calcula cronológicamente el total de m² robados y perdidos por cada alumno."""
    robados_m2 = {al: 0.0 for al in ESTUDIANTES.keys()}
    perdidose_m2 = {al: 0.0 for al in ESTUDIANTES.keys()}
    
    dominios_pasados = {}
    historial_robos = []
    cantones_utm = cargar_cantones_la_palma().to_crs("EPSG:32628")
    
    for act in st.session_state.actividades:
        atractor = act['alumno']
        nueva_geom = act['geometria_utm']
        
        # Intersección con cantones
        c_nombres = []
        for _, c_row in cantones_utm.iterrows():
            if c_row['geometry'].intersects(nueva_geom):
                c_nombres.append(c_row['canton'])
        cantones_str = "📍 " + ", ".join(c_nombres) if c_nombres else "📍 Sin cantón"
        
        # Evaluar robos
        robos_actividad = {}
        total_robado_act = 0.0
        
        for victima, geom_victima in dominios_pasados.items():
            if victima != atractor and geom_victima is not None and not getattr(geom_victima, 'is_empty', True):
                intersec = geom_victima.intersection(nueva_geom)
                area_stolen = intersec.area
                if area_stolen > 0.1:
                    robos_actividad[victima] = area_stolen
                    total_robado_act += area_stolen
                    robados_m2[atractor] += area_stolen
                    perdidose_m2[victima] += area_stolen
                    dominios_pasados[victima] = geom_victima.difference(nueva_geom)
                    
        if atractor not in dominios_pasados or dominios_pasados[atractor] is None or getattr(dominios_pasados[atractor], 'is_empty', True):
            dominios_pasados[atractor] = nueva_geom
        else:
            dominios_pasados[atractor] = dominios_pasados[atractor].union(nueva_geom)
            
        desglose_txt = []
        for vic, m2_s in robos_actividad.items():
            p_vic = ESTUDIANTES.get(vic, {"escudo": "🛡️"})
            desglose_txt.append(f"{round(m2_s/10000, 2)} ha a {p_vic['escudo']} {vic}")
            
        if total_robado_act > 0.1:
            res_robo = f"⚔️ <b>{round(total_robado_act/10000, 2)} ha</b> (" + ", ".join(desglose_txt) + ")"
        else:
            res_robo = "🕊️ 0.00 ha (Sin robos)"
            
        historial_robos.append({
            'fecha': act['fecha'].strftime("%Y-%m-%d %H:%M"),
            'alumno': act['alumno'],
            'cantones': cantones_str,
            'robos': res_robo,
            'tipo': act['tipo'],
            'archivo': act['archivo']
        })
        
    return robados_m2, perdidose_m2, historial_robos

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
robados_m2_dict, perdidos_m2_dict, historial_robos_list = calcular_estadisticas_robos_globales()

# -----------------------------------------------------------------------------
# 8. INTERFAZ PRINCIPAL CON 5 PESTAÑAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "⚡ CLASIFICACIÓN SEMANAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

# -----------------------------------------------------------------------------
# PESTAÑA 1: MAPA DE DOMINIO
# -----------------------------------------------------------------------------
with tab1:
    st.write("### 📍 Mapa Táctico de La Palma")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=11,
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
                'fillOpacity': 0.15,
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
                    'fillOpacity': 0.60
                },
                tooltip=f"<b>{escudo} Conquistador:</b> {alumno}<br><b>Dominio:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)

    # MARCADORES DE ESCUDO PARA CADA RUTA REALIZADA
    for act in st.session_state.actividades:
        al = act['alumno']
        perf = ESTUDIANTES.get(al, {"escudo": "🛡️", "color": "#00E5FF"})
        color = perf["color"]
        escudo = perf["escudo"]
        
        geom_util = act.get('geometria_linea_utm', act['geometria_utm'])
        if "Bucle Cerrado" in act['tipo']:
            punto_utm = act['geometria_utm'].centroid
        else:
            punto_utm = geom_util.interpolate(0.5, normalized=True)
            
        gdf_p = gpd.GeoDataFrame(geometry=[punto_utm], crs="EPSG:32628").to_crs("EPSG:4326")
        p_wgs = gdf_p.geometry.iloc[0]
        
        icon_html = f'<div style="background-color: #0d1117; border: 2.5px solid {color}; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-size: 17px; box-shadow: 0 0 10px {color};">{escudo}</div>'
        folium.Marker(
            location=[p_wgs.y, p_wgs.x],
            icon=folium.DivIcon(html=icon_html),
            tooltip=f"<b>{escudo} {al}</b><br>📁 {act['archivo']}<br>📅 {act['fecha'].strftime('%d/%m %H:%M')}<br>{act['tipo']}"
        ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

# -----------------------------------------------------------------------------
# PESTAÑA 2: CLASIFICACIÓN GENERAL
# -----------------------------------------------------------------------------
with tab2:
    st.write("### 🏆 Ranking General de la Isla")
    ranking_data = []
    
    for alumno in ESTUDIANTES.keys():
        geom = dominios_utm.get(alumno, None)
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        perf = ESTUDIANTES[alumno]
        
        rob_km2 = round(robados_m2_dict.get(alumno, 0.0) / 1_000_000.0, 4)
        perd_km2 = round(perdidos_m2_dict.get(alumno, 0.0) / 1_000_000.0, 4)
        
        ranking_data.append({
            "Guerrero/a": f"{perf['escudo']} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "km² que he robado (total)": rob_km2,
            "km² que me han robado (total)": perd_km2,
            "_area_sort": area_m2
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="_area_sort", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(
            df_ranking[["Guerrero/a", "Superficie (km²)", "km² que he robado (total)", "km² que me han robado (total)"]],
            use_container_width=True
        )
    else:
        st.info("Aún no se han registrado rutas en la campaña.")

# -----------------------------------------------------------------------------
# PESTAÑA 3: CLASIFICACIÓN SEMANAL
# -----------------------------------------------------------------------------
with tab3:
    st.write("### ⚡ Clasificación Semanal de Conquista")
    
    now_dt = datetime.now()
    cur_year, cur_week, _ = now_dt.isocalendar()
    
    # Construcción del selector semanal (Semana Actual vs Semana Anterior)
    opciones_semanas = {}
    
    # Semana actual
    l_cur_start = now_dt - timedelta(days=now_dt.weekday())
    l_cur_end = l_cur_start + timedelta(days=6)
    str_cur = f"Semana Actual ({cur_week}) [{l_cur_start.strftime('%d %b')} - {l_cur_end.strftime('%d %b %Y')}]"
    opciones_semanas[str_cur] = (cur_year, cur_week)
    
    # Semanas anteriores
    for w_back in range(1, 12):
        dt_ref = now_dt - timedelta(weeks=w_back)
        y_ref, w_ref, _ = dt_ref.isocalendar()
        dt_start = dt_ref - timedelta(days=dt_ref.weekday())
        dt_end = dt_start + timedelta(days=6)
        
        tag_ant = " [SEMANA ANTERIOR]" if w_back == 1 else ""
        label_w = f"Semana {w_ref}{tag_ant} [{dt_start.strftime('%d %b')} - {dt_end.strftime('%d %b %Y')}]"
        opciones_semanas[label_w] = (y_ref, w_ref)
        
    lista_labels = list(opciones_semanas.keys())
    idx_default = 1 if len(lista_labels) > 1 else 0
    
    sem_seleccionada_str = st.selectbox(
        "📅 Seleccionar Semana de Campaña:",
        lista_labels,
        index=idx_default
    )
    
    sel_year, sel_week = opciones_semanas[sem_seleccionada_str]
    
    # Filtrar actividades de esa semana
    actividades_semana = []
    for act in st.session_state.actividades:
        ay, aw, _ = act['fecha'].isocalendar()
        if ay == sel_year and aw == sel_week:
            actividades_semana.append(act)
            
    if actividades_semana:
        sum_semanal = {al: 0.0 for al in ESTUDIANTES.keys()}
        count_rutas = {al: 0 for al in ESTUDIANTES.keys()}
        cantones_rutas = {al: set() for al in ESTUDIANTES.keys()}
        cantones_utm = cargar_cantones_la_palma().to_crs("EPSG:32628")
        
        for act in actividades_semana:
            al = act['alumno']
            geom = act['geometria_utm']
            sum_semanal[al] += geom.area
            count_rutas[al] += 1
            
            for _, c_row in cantones_utm.iterrows():
                if c_row['geometry'].intersects(geom):
                    cantones_rutas[al].add(c_row['canton'])
                    
        filas_semana = []
        for al, area_m2 in sum_semanal.items():
            if area_m2 > 0:
                p = ESTUDIANTES[al]
                c_str = ", ".join(sorted(list(cantones_rutas[al]))) if cantones_rutas[al] else "Sin cantón"
                filas_semana.append({
                    "Guerrero/a": f"{p['escudo']} {al}",
                    "Hectáreas Sumadas (ha)": round(area_m2 / 10000.0, 2),
                    "Superficie (m²)": round(area_m2, 2),
                    "Rutas Realizadas": count_rutas[al],
                    "Cantones Explorados": c_str,
                    "_sort": area_m2
                })
                
        if filas_semana:
            df_sem = pd.DataFrame(filas_semana).sort_values(by="_sort", ascending=False)
            
            # Podio semanal
            lider_sem = df_sem.iloc[0]
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(22, 27, 34, 0.9) 100%);
                border: 2px solid #ffd700;
                border-radius: 12px;
                padding: 16px;
                text-align: center;
                margin-bottom: 20px;
                box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);
            ">
                <div style="color: #ffd700; font-family: 'Cinzel', serif; font-size: 1.2rem; font-weight: 800;">
                    🏆 CAMPEÓN/A DE LA {sem_seleccionada_str.split('[')[0]}
                </div>
                <div style="color: #ffffff; font-size: 1.8rem; font-weight: 900; margin: 8px 0;">
                    🥇 {lider_sem['Guerrero/a']}
                </div>
                <div style="color: #00FF66; font-size: 1.1rem; font-weight: 800;">
                    + {lider_sem['Hectáreas Sumadas (ha)']} ha conquistadas ({lider_sem['Rutas Realizadas']} rutas)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            medallas = ["🥇 1.º", "🥈 2.º", "🥉 3.º"] + [f"🏅 {i}º" for i in range(4, len(df_sem) + 1)]
            df_sem["Posición"] = medallas[:len(df_sem)]
            df_sem.index = range(1, len(df_sem) + 1)
            
            st.dataframe(
                df_sem[["Posición", "Guerrero/a", "Hectáreas Sumadas (ha)", "Superficie (m²)", "Rutas Realizadas", "Cantones Explorados"]],
                use_container_width=True
            )
        else:
            st.info("Sin registros de territorio conquistado en la semana elegida.")
    else:
        st.info("No hay rutas registradas en la semana elegida.")

# -----------------------------------------------------------------------------
# PESTAÑA 4: MENCEYES POR CANTÓN
# -----------------------------------------------------------------------------
with tab4:
    st.write("### 👑 Menceyes y Señoríos por Cantón")
    df_cantones = calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf)
    
    if not df_cantones.empty:
        cantones_conquistados = df_cantones["Cantón"].unique()
        
        st.write("#### 🤴 Menceyes Actuales")
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

# -----------------------------------------------------------------------------
# PESTAÑA 5: LIBRO DE GUERRA
# -----------------------------------------------------------------------------
with tab5:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    
    if historial_robos_list:
        rows_html = ""
        for h in historial_robos_list:
            al = h['alumno']
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️"})
            rows_html += f"""
            <tr style="border-bottom: 1px solid #cbd5e1; background-color: #ffffff;">
                <td style="padding: 12px; color: #111111; font-weight: 700;">{h['fecha']}</td>
                <td style="padding: 12px; color: #111111; font-weight: 800; font-size: 1.05rem;">{perf['escudo']} {al}</td>
                <td style="padding: 12px; color: #0f172a; font-weight: 600;">{h['cantones']}</td>
                <td style="padding: 12px; color: #111111; font-weight: 600;">{h['robos']}</td>
                <td style="padding: 12px; color: #334155; font-weight: 600;">{h['tipo']}</td>
                <td style="padding: 12px; color: #0284c7; font-family: monospace; font-size: 0.9rem;">{h['archivo']}</td>
            </tr>
            """
            
        tabla_completa_html = f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            max-height: 520px;
            overflow-y: auto;
        ">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: 'Outfit', sans-serif;">
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
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        components.html(tabla_completa_html, height=540)
    else:
        st.info("El historial de incursiones de guerra está limpio.")
