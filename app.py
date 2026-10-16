import sys
import py_compile

app_code = """import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import streamlit as st
import folium
import streamlit.components.v1 as components
import shapely.geometry as sg
import geopandas as gpd
import pandas as pd

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO OSCURO "RUN AN EMPIRE"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Oscuro de Alto Contraste para Máxima Legibilidad
st.markdown(\"\"\"
<style>
    /* Fondo principal y textos generales */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Encabezado Épico */
    .header-box {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 2px solid #ffd700;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.2);
    }
    .header-title {
        color: #ffd700;
        font-size: 2.2rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
        text-shadow: 2px 2px 4px #000000;
    }
    .header-subtitle {
        color: #e6edf3;
        font-size: 1.05rem;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Tarjetas de Métricas (Menceyes) */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #ffd700;
        border-left: 5px solid #ffd700;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }
    div[data-testid="stMetricLabel"] {
        color: #ffd700 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Pestañas de Navegación */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 8px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d;
        color: #ffffff !important;
        border-radius: 6px;
        font-weight: bold !important;
        font-size: 1rem !important;
        border: 1px solid #484f58;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
        font-weight: 900 !important;
    }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 2px solid #ffd700 !important;
    }

    /* MÁXIMA VISIBILIDAD Y CONTRASTE EN INPUTS DE FECHA, HORA, TEXTO Y FILE UPLOADER */
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    div[data-testid="stForm"] label,
    label[data-testid="stWidgetLabel"] p {
        color: #ffd700 !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
    }

    /* Cajas de texto, contraseña, valores e indicadores de fecha y hora */
    div[data-baseweb="input"], 
    div[data-baseweb="base-input"],
    input[type="text"],
    input[type="password"],
    input[type="number"],
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 2px solid #ffd700 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }

    /* Textos, fechas y horas visibles dentro de los controles de DateInput y TimeInput */
    div[data-testid="stDateInput"] div,
    div[data-testid="stTimeInput"] div,
    div[data-testid="stDateInput"] span,
    div[data-testid="stTimeInput"] span,
    div[data-testid="stDateInput"] p,
    div[data-testid="stTimeInput"] p,
    div[data-baseweb="input"] div,
    div[data-baseweb="input"] span {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Iconos dentro de inputs (calendario, reloj, candado) */
    div[data-testid="stDateInput"] svg,
    div[data-testid="stTimeInput"] svg,
    div[data-baseweb="input"] svg {
        fill: #ffd700 !important;
        color: #ffd700 !important;
    }

    /* Desplegable Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 2px solid #ffd700 !important;
        border-radius: 6px !important;
        font-weight: bold !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] p {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* File Uploader (Subir archivo .gpx) - Alto Contraste */
    div[data-testid="stFileUploader"] {
        background-color: #0d1117 !important;
        border: 2px dashed #ffd700 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    div[data-testid="stFileUploader"] section {
        background-color: #161b22 !important;
    }
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] label p {
        color: #ffd700 !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
    }
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] small,
    div[data-testid="stFileUploader"] div,
    div[data-testid="stFileUploader"] p,
    [data-testid="stFileUploaderDropzoneInstructions"] div,
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    div[data-testid="stFileUploader"] button {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
        font-weight: bold !important;
        border: none !important;
    }

    /* Menús emergentes de Date/Time picker y Selectbox */
    ul[data-baseweb="menu"], 
    div[data-baseweb="popover"],
    div[data-baseweb="calendar"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 2px solid #ffd700 !important;
    }
    div[data-baseweb="calendar"] button {
        color: #ffffff !important;
    }

    /* Botones primarios */
    .stButton > button {
        background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%) !important;
        color: #0d1117 !important;
        font-weight: 800 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 10px rgba(255, 215, 0, 0.3) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #ffffff 0%, #ffd700 100%) !important;
        color: #0d1117 !important;
        box-shadow: 0 4px 15px rgba(255, 255, 255, 0.5) !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI - La Palma</div>
</div>
\"\"\", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TIMER DINÁMICO EN TIEMPO REAL (JS CLIENTE)
# -----------------------------------------------------------------------------
components.html(\"\"\"
<div id="countdown-box" style="
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border: 2px solid #ffd700;
    border-radius: 10px;
    padding: 12px 20px;
    text-align: center;
    color: #ffffff;
    font-family: 'Segoe UI', Roboto, sans-serif;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
    margin-bottom: 15px;
">
    <div style="color: #ffd700; font-size: 1.1rem; font-weight: bold; letter-spacing: 1px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTAS GPX (Cierre: 30 de Mayo de 2026 - 23:59)
    </div>
    <div id="timer-display" style="
        font-size: 1.8rem;
        font-weight: 900;
        color: #ffffff;
        margin-top: 6px;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    ">
        Cargando cuenta atrás...
    </div>
</div>

<script>
function updateTimer() {
    const targetDate = new Date("2026-05-30T23:59:59").getTime();
    const now = new Date().getTime();
    const difference = targetDate - now;

    const display = document.getElementById("timer-display");

    if (difference <= 0) {
        display.innerHTML = "<span style='color: #ff3333;'>🛑 CAMPAÑA FINALIZADA</span>";
        return;
    }

    const days = Math.floor(difference / (1000 * 60 * 60 * 24));
    const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((difference % (1000 * 60)) / 1000);

    const pad = (n) => n < 10 ? '0' + n : n;

    display.innerHTML = `⏳ <span style="color: #ffd700;">${days}</span> Días | <span style="color: #ffd700;">${pad(hours)}</span>h : <span style="color: #ffd700;">${pad(minutes)}</span>m : <span style="color: #ffd700;">${pad(seconds)}</span>s`;
}

updateTimer();
setInterval(updateTimer, 1000);
</script>
\"\"\", height=110)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# BASE DE DATOS DE LOS 11 ALUMNOS CON ESCUDOS Y COLORES ASIGNADOS
# -----------------------------------------------------------------------------
ALUMNOS_PERFILES = {
    "Estrella": {"escudo": "⭐", "nombre_escudo": "Estrella de Cima", "color": "#FF0055"},
    "Yassine":  {"escudo": "🦅", "nombre_escudo": "Águila de Cumbre", "color": "#00E5FF"},
    "Fabián":   {"escudo": "⚔️", "nombre_escudo": "Lanzas Cruzadas", "color": "#00FF66"},
    "Claudia":  {"escudo": "👑", "nombre_escudo": "Corona de Mencey", "color": "#FFCC00"},
    "Matías":   {"escudo": "🌋", "nombre_escudo": "Volcán Tajogaite", "color": "#FF6600"},
    "Yeray":    {"escudo": "🛡️", "nombre_escudo": "Escudo Táctico", "color": "#AA00FF"},
    "Adrián":   {"escudo": "☀️", "nombre_escudo": "Sol de Roque", "color": "#76FF03"},
    "Yamila":   {"escudo": "🌙", "nombre_escudo": "Luna Aborigen", "color": "#00FFCC"},
    "Gabriel":  {"escudo": "⚡", "nombre_escudo": "Rayo de Cima", "color": "#D500F9"},
    "Juanmi":   {"escudo": "🔥", "nombre_escudo": "Fuego de Cumbre", "color": "#FF3333"},
    "Paula":    {"escudo": "💎", "nombre_escudo": "Diamante Guanche", "color": "#3388FF"}
}

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN Y CARGA DE LOS 12 CANTONES BENAHOARITAS
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
# 3. PROCESAMIENTO DE GPX Y PERSISTENCIA DE DATOS
# -----------------------------------------------------------------------------
def procesar_puntos_gpx(puntos, max_dist_cierre_m=100.0, franja_m=30.0):
    if len(puntos) < 3:
        return None, "Error: GPX con puntos insuficientes"
        
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
        
    return geom_conquista, tipo

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
                geom, tipo = procesar_puntos_gpx(puntos)
                if geom is not None:
                    actividades.append({
                        'alumno': item['alumno'],
                        'fecha': fecha,
                        'geometria_utm': geom,
                        'tipo': tipo,
                        'archivo': item.get('archivo', 'actividad.gpx'),
                        'puntos': puntos
                    })
        actividades.sort(key=lambda x: x['fecha'])
        return actividades
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
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
# 4. BARRA LATERAL DOCENTE
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DEL DOCENTE")

pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password", help="Introduce la clave para gestionar rutas.")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Docente Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Registrar Nueva Ruta GPX")
    
    lista_alumnos = sorted(list(ALUMNOS_PERFILES.keys()))
    alumno_sel = st.sidebar.selectbox("Seleccionar Alumno/a (11 integrantes):", lista_alumnos)
    
    perf = ALUMNOS_PERFILES[alumno_sel]
    st.sidebar.info(f"**Escudo:** {perf['escudo']} {perf['nombre_escudo']}\\n\\n**Color:** `{perf['color']}`")
    
    fecha_ruta = st.sidebar.date_input("Fecha de la Ruta", value=datetime.now())
    hora_ruta = st.sidebar.time_input("Hora de la Ruta", value=datetime.now().time())
    archivo_gpx = st.sidebar.file_uploader("Subir archivo .gpx", type=["gpx"])
    
    if st.sidebar.button("⚡ CONQUISTAR TERRITORIO"):
        if archivo_gpx is not None:
            fecha_completa = datetime.combine(fecha_ruta, hora_ruta)
            puntos = extraer_puntos_gpx(archivo_gpx)
            geom, tipo = procesar_puntos_gpx(puntos)
            
            if geom is not None:
                st.session_state.actividades.append({
                    'alumno': alumno_sel,
                    'fecha': fecha_completa,
                    'geometria_utm': geom,
                    'tipo': tipo,
                    'archivo': archivo_gpx.name,
                    'puntos': puntos
                })
                st.session_state.actividades.sort(key=lambda x: x['fecha'])
                guardar_actividades_persistentes(st.session_state.actividades)
                st.sidebar.success(f"¡Territorio de {perf['escudo']} {alumno_sel} registrado con éxito!")
                st.rerun()
            else:
                st.sidebar.error("El archivo GPX no contiene datos válidos.")
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
    st.sidebar.info("👁️ **Modo Estudiante (Solo Lectura)** - Consulta el mapa de dominio y clasificaciones en tiempo real.")

# -----------------------------------------------------------------------------
# 5. CÁLCULO DE SOLAPAMIENTOS Y COBERTURA POR CANTÓN
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
                escudo = ALUMNOS_PERFILES.get(alumno, {}).get("escudo", "🛡️")
                filas.append({
                    "Cantón": nombre_canton,
                    "Alumno/a": f"{escudo} {alumno}",
                    "Nombre_Limpio": alumno,
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm = calcular_dominios_actuales()
cantones_gdf = cargar_cantones_la_palma()

# -----------------------------------------------------------------------------
# 6. INTERFAZ PRINCIPAL
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

with tab1:
    st.write("### 📍 Mapa Táctico de La Palma")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=10,
        min_zoom=10,
        tiles="OpenStreetMap"
    )
    m.fit_bounds([[28.40, -18.05], [28.90, -17.65]])
    
    # Capa de Cantones Benahoaritas
    for _, row in cantones_gdf.iterrows():
        folium.GeoJson(
            sg.mapping(row['geometry']),
            style_function=lambda x: {
                'fillColor': '#161b22',
                'color': '#ffd700',
                'weight': 2,
                'fillOpacity': 0.15,
                'dashArray': '5, 5'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Municipio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Territorio Conquistado por Alumnos
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            perf = ALUMNOS_PERFILES.get(alumno, {"color": "#00E5FF", "escudo": "🛡️"})
            color = perf["color"]
            escudo = perf["escudo"]
            
            # Polígono con el color personalizado del alumno
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=color: {
                    'fillColor': col,
                    'color': col,
                    'weight': 3,
                    'fillOpacity': 0.6
                },
                tooltip=f"<b>{escudo} Dominio de:</b> {alumno}<br><b>Superficie:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Marcador Flotante con el Escudo en el Centroide del Territorio
            try:
                centroide_wgs = geom_wgs.centroid
                icon_html = f'''
                <div style="
                    background-color: #0d1117;
                    border: 2px solid {color};
                    border-radius: 50%;
                    width: 32px;
                    height: 32px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    box-shadow: 0 0 8px {color};
                ">{escudo}</div>
                '''
                folium.Marker(
                    location=[centroide_wgs.y, centroide_wgs.x],
                    icon=folium.DivIcon(html=icon_html),
                    tooltip=f"<b>Territorio de {escudo} {alumno}</b>"
                ).add_to(m)
            except Exception:
                pass
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        perf = ALUMNOS_PERFILES.get(alumno, {"escudo": "🛡️", "color": "#ffffff"})
        ranking_data.append({
            "Conquistador/a": f"{perf['escudo']} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Conquistador/a", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han registrado rutas. El docente debe subir los primeros archivos GPX.")

with tab3:
    st.write("### 👑 Menceyes y Señoríos por Cantón")
    df_cantones = calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf)
    
    if not df_cantones.empty:
        cantones_conquistados = df_cantones["Cantón"].unique()
        
        st.write("#### 🤴 Menceyes Actuales")
        cols = st.columns(3)
        for i, cant in enumerate(cantones_conquistados):
            df_sub = df_cantones[df_cantones["Cantón"] == cant].sort_values(by="Superficie (m²)", ascending=False)
            lider = df_sub.iloc[0]
            
            with cols[i % 3]:
                st.metric(
                    label=f"🏛️ {cant}",
                    value=f"{lider['Alumno/a']}",
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

with tab4:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    if st.session_state.actividades:
        historial = []
        for act in st.session_state.actividades:
            al = act['alumno']
            perf = ALUMNOS_PERFILES.get(al, {"escudo": "🛡️"})
            historial.append({
                "Fecha/Hora": act['fecha'].strftime("%Y-%m-%d %H:%M"),
                "Conquistador/a": f"{perf['escudo']} {al}",
                "Tipo de Incursión": act['tipo'],
                "Archivo GPX": act['archivo']
            })
        st.table(pd.DataFrame(historial))
    else:
        st.info("El historial está limpio.")
"""

with open('/workspace/scratch/build.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print("build.py created successfully!")
