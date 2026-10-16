import xml.etree.ElementTree as ET
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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO OSCURO DE ALTO CONTRASTE "RUN AN EMPIRE"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Oscuro con Máximo Contraste para la Letra y el Menú
st.markdown("""
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
        box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.25);
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
        margin-top: 5px;
        font-weight: 500;
    }

    /* Pestañas de Navegación con Texto Blanco y Alto Contraste */
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
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 10px 18px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
        font-weight: 900 !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #0d1117 !important;
        font-weight: 900 !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* Tarjetas de Métricas (Menceyes) */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #ffd700;
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
        font-weight: 800 !important;
    }

    /* BARRA LATERAL (MENÚ DEL PROFESOR) - MÁXIMO CONTRASTE */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 2px solid #ffd700 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Inputs de texto y contraseña del Menú Lateral */
    div[data-baseweb="input"] input, 
    div[data-baseweb="base-input"] input,
    input[type="text"], 
    input[type="password"] {
        color: #ffffff !important;
        background-color: #0d1117 !important;
        border: 1.5px solid #ffd700 !important;
        border-radius: 6px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        padding: 8px 12px !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 1.5px solid #ffd700 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="select"] span {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Tablas de Streamlit */
    div[data-testid="stTable"] *, div[data-testid="stDataFrame"] * {
        color: #ffffff !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI - La Palma</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CUENTA ATRÁS DINÁMICA EN TIEMPO REAL (HASTA EL 30 DE MAYO DE 2027)
# -----------------------------------------------------------------------------
components.html("""
<div id="countdown-container" style="
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 2px solid #ffd700;
    border-radius: 10px;
    padding: 12px 20px;
    text-align: center;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    box-shadow: 0 4px 12px rgba(255, 215, 0, 0.25);
    margin-bottom: 10px;
">
    <div style="font-size: 0.95rem; color: #ffd700; font-weight: 800; letter-spacing: 1px; text-transform: uppercase;">
        ⏰ CUENTA ATRÁS DE LA CAMPAÑA (Cierre de Entregas GPX: 30 de Mayo - 23:59)
    </div>
    <div id="clock" style="font-size: 1.8rem; font-weight: 900; color: #00e5ff; margin-top: 5px; text-shadow: 0 0 10px rgba(0, 229, 255, 0.6);">
        Cargando tiempo restante...
    </div>
</div>

<script>
    // Fecha límite: 30 de Mayo a las 23:59:59
    const targetDate = new Date('2027-05-30T23:59:59').getTime();
    
    function updateClock() {
        const now = new Date().getTime();
        const diff = targetDate - now;
        
        if (diff <= 0) {
            document.getElementById('clock').innerHTML = '🛑 CAMPAÑA FINALIZADA';
            return;
        }
        
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        
        const hStr = hours < 10 ? '0' + hours : hours;
        const mStr = minutes < 10 ? '0' + minutes : minutes;
        const sStr = seconds < 10 ? '0' + seconds : seconds;
        
        document.getElementById('clock').innerHTML = 
            `⏳ ${days} Días | ${hStr}h : ${mStr}m : ${sStr}s restantes`;
    }
    
    updateClock();
    setInterval(updateClock, 1000);
</script>
""", height=110)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# 3. LISTADO OFICIAL DE LOS 11 ESTUDIANTES CON SUS ESCUDOS Y COLORES NEÓN
# -----------------------------------------------------------------------------
ESTUDIANTES_PREDEFINIDOS = {
    "Estrella": {"escudo": "⭐ Estrella de Cima", "color": "#FF0055"},
    "Yassine": {"escudo": "🦅 Águila de Cumbre", "color": "#00E5FF"},
    "Fabián": {"escudo": "⚔️ Lanzas Cruzadas", "color": "#00FF66"},
    "Claudia": {"escudo": "👑 Corona de Mencey", "color": "#FFCC00"},
    "Matías": {"escudo": "🌋 Volcán Tajogaite", "color": "#FF6600"},
    "Yeray": {"escudo": "🛡️ Escudo Táctico", "color": "#AA00FF"},
    "Adrián": {"escudo": "☀️ Sol de Roque", "color": "#76FF03"},
    "Yamila": {"escudo": "🌙 Luna Aborigen", "color": "#00FFCC"},
    "Gabriel": {"escudo": "⚡ Rayo de Cima", "color": "#D500F9"},
    "Juanmi": {"escudo": "🔥 Fuego de Cumbre", "color": "#FF3333"},
    "Paula": {"escudo": "💎 Diamante Guanche", "color": "#3388FF"}
}

LISTA_ESCUDOS = [
    "⭐ Estrella de Cima", "🦅 Águila de Cumbre", "⚔️ Lanzas Cruzadas",
    "👑 Corona de Mencey", "🌋 Volcán Tajogaite", "🛡️ Escudo Táctico",
    "☀️ Sol de Roque", "🌙 Luna Aborigen", "⚡ Rayo de Cima",
    "🔥 Fuego de Cumbre", "💎 Diamante Guanche"
]

MAPA_COLORES = {
    "Estrella": "#FF0055", "Yassine": "#00E5FF", "Fabián": "#00FF66",
    "Claudia": "#FFCC00", "Matías": "#FF6600", "Yeray": "#AA00FF",
    "Adrián": "#76FF03", "Yamila": "#00FFCC", "Gabriel": "#D500F9",
    "Juanmi": "#FF3333", "Paula": "#3388FF"
}

# -----------------------------------------------------------------------------
# 4. CARGA DE CANTONES Y PERSISTENCIA
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
                        'puntos': puntos,
                        'escudo': item.get('escudo', ESTUDIANTES_PREDEFINIDOS.get(item['alumno'], {}).get('escudo', '🛡️ Escudo Táctico')),
                        'color': item.get('color', MAPA_COLORES.get(item['alumno'], '#00E5FF'))
                    })
        actividades.sort(key=lambda x: x['fecha'])
        return actividades
    except Exception as e:
        st.error(f"Error cargando persistencia: {e}")
        return []

def guardar_actividades_persistentes(actividades):
    data = []
    for act in actividades:
        data.append({
            'alumno': act['alumno'],
            'fecha': act['fecha'].strftime("%Y-%m-%d %H:%M"),
            'archivo': act.get('archivo', 'actividad.gpx'),
            'puntos': act.get('puntos', []),
            'escudo': act.get('escudo', '🛡️ Escudo Táctico'),
            'color': act.get('color', '#00E5FF')
        })
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'actividades' not in st.session_state:
    st.session_state.actividades = cargar_actividades_persistentes()

# -----------------------------------------------------------------------------
# 5. BARRA LATERAL (CONTROL DOCENTE Y RECONOCIMIENTO AUTOMÁTICO DE ALUMNOS)
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DOCENTE")

pwd_input = st.sidebar.text_input("🔑 Contraseña Profesor/a", type="password", help="Escribe la contraseña para acceder al panel de subida.")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Profesor Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Registrar Ruta GPX")
    
    # Seleccionador de uno de los 11 alumnos oficiales
    lista_alumnos = list(ESTUDIANTES_PREDEFINIDOS.keys())
    alumno_sel = st.sidebar.selectbox("Seleccionar Alumno/a (11 Alumnos)", options=lista_alumnos)
    
    # Reconocimiento automático de escudo y color asociado
    escudo_defecto = ESTUDIANTES_PREDEFINIDOS[alumno_sel]["escudo"]
    color_defecto = ESTUDIANTES_PREDEFINIDOS[alumno_sel]["color"]
    
    st.sidebar.markdown(f"""
    <div style="background:#0d1117; border:1px solid #ffd700; border-radius:6px; padding:10px; margin-bottom:12px;">
        <span style="color:#ffd700; font-weight:bold;">Alumno/a Reconocido:</span> {alumno_sel}<br>
        <span style="color:#ffd700; font-weight:bold;">Escudo Asignado:</span> {escudo_defecto}<br>
        <span style="color:#ffd700; font-weight:bold;">Color de Guerra:</span> <span style="color:{color_defecto}; font-weight:bold; font-size:1.1rem;">■</span> {color_defecto}
    </div>
    """, unsafe_allow_html=True)
    
    escudo_elegido = st.sidebar.selectbox("🛡️ Escudo / Blasón", options=LISTA_ESCUDOS, index=LISTA_ESCUDOS.index(escudo_defecto) if escudo_defecto in LISTA_ESCUDOS else 0)
    
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
                    'puntos': puntos,
                    'escudo': escudo_elegido,
                    'color': color_defecto
                })
                st.session_state.actividades.sort(key=lambda x: x['fecha'])
                guardar_actividades_persistentes(st.session_state.actividades)
                st.sidebar.success(f"¡Ruta de {alumno_sel} registrada con éxito!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX sin datos válidos.")
        else:
            st.sidebar.warning("Selecciona el archivo GPX.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Reiniciar Campaña (Borrar Todo)"):
        st.session_state.actividades = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.sidebar.success("¡Campaña reiniciada!")
        st.rerun()
else:
    st.sidebar.info("👁️ **Modo Estudiante (Solo Lectura)** - Navega por el mapa de dominio y consulta el ranking en tiempo real.")

# -----------------------------------------------------------------------------
# 6. CÁLCULO DE TERRITORIOS Y SOLAPAMIENTOS
# -----------------------------------------------------------------------------
def calcular_dominios_actuales():
    dominios = {}
    escudos = {}
    colores = {}
    
    for act in st.session_state.actividades:
        alumno = act['alumno']
        nueva_geom = act['geometria_utm']
        escudos[alumno] = act.get('escudo', ESTUDIANTES_PREDEFINIDOS.get(alumno, {}).get('escudo', '🛡️'))
        colores[alumno] = act.get('color', MAPA_COLORES.get(alumno, '#00E5FF'))
        
        for al in list(dominios.keys()):
            if dominios[al] is not None and not getattr(dominios[al], 'is_empty', True):
                dominios[al] = dominios[al].difference(nueva_geom)
                
        if alumno not in dominios or dominios[alumno] is None or getattr(dominios[alumno], 'is_empty', True):
            dominios[alumno] = nueva_geom
        else:
            dominios[alumno] = dominios[alumno].union(nueva_geom)
            
    return dominios, escudos, colores

def calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf, escudos):
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
                    "Escudo": escudos.get(alumno, "🛡️"),
                    "Alumno/a": alumno,
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm, escudos_alumnos, colores_alumnos = calcular_dominios_actuales()
cantones_gdf = cargar_cantones_la_palma()

# -----------------------------------------------------------------------------
# 7. INTERFAZ PRINCIPAL
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

with tab1:
    st.write("### 📍 Mapa Táctico de La Palma")
    
    # Mapa OpenStreetMap limpio sin API Key con zoom acotado a La Palma
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
                'fillColor': '#161b22',
                'color': '#ffd700',
                'weight': 1.8,
                'fillOpacity': 0.15,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Municipio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Territorios Conquistados con Colores Neón e Insignia de Escudo
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            color = colores_alumnos.get(alumno, MAPA_COLORES.get(alumno, "#00E5FF"))
            escudo = escudos_alumnos.get(alumno, ESTUDIANTES_PREDEFINIDOS.get(alumno, {}).get('escudo', '🛡️'))
            
            # Polígono teñido con el color del alumno
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=color: {
                    'fillColor': col,
                    'color': col,
                    'weight': 2.5,
                    'fillOpacity': 0.65
                },
                tooltip=f"<b>{escudo} Dominio de {alumno}</b><br><b>Superficie:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Icono Flotante del Escudo en el centro de la zona conquistada
            centroide = geom_wgs.centroid
            icono_html = f"""
            <div style="
                background-color: #0d1117;
                border: 2px solid {color};
                border-radius: 50%;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                box-shadow: 0 0 8px {color};
            ">{escudo.split()[0]}</div>
            """
            folium.Marker(
                location=[centroide.y, centroide.x],
                icon=folium.DivIcon(html=icono_html),
                tooltip=f"<b>{escudo} - {alumno}</b>"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        escudo = escudos_alumnos.get(alumno, ESTUDIANTES_PREDEFINIDOS.get(alumno, {}).get('escudo', '🛡️'))
        ranking_data.append({
            "Escudo": escudo.split()[0],
            "Alumno/a": alumno,
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Escudo", "Alumno/a", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han registrado rutas. El docente debe subir los primeros archivos GPX.")

with tab3:
    st.write("### 👑 Menceyes y Señoríos por Cantón")
    df_cantones = calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf, escudos_alumnos)
    
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
                    value=f"{lider['Escudo'].split()[0]} {lider['Alumno/a']}",
                    delta=f"{lider['Hectáreas (ha)']} ha ({lider['% Conquistado del Cantón']}% del cantón)"
                )
                
        st.markdown("---")
        
        canton_sel = st.selectbox("🔎 Inspeccionar Cantón:", cantones_conquistados)
        df_canton_especifico = df_cantones[df_cantones["Cantón"] == canton_sel].sort_values(by="Superficie (m²)", ascending=False)
        df_canton_especifico.index = range(1, len(df_canton_especifico) + 1)
        
        st.write(f"### Disputa Territorial en **{canton_sel}**")
        st.dataframe(
            df_canton_especifico[["Escudo", "Alumno/a", "Hectáreas (ha)", "% Conquistado del Cantón", "Superficie (m²)"]],
            use_container_width=True
        )
    else:
        st.info("Ningún cantón ha sido conquistado todavía.")

with tab4:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    if st.session_state.actividades:
        historial = [{
            "Fecha/Hora": act['fecha'].strftime("%Y-%m-%d %H:%M"),
            "Escudo": act.get('escudo', '🛡️').split()[0],
            "Conquistador/a": act['alumno'],
            "Tipo de Incursión": act['tipo'],
            "Archivo GPX": act['archivo']
        } for act in st.session_state.actividades]
        st.table(pd.DataFrame(historial))
    else:
        st.info("El historial está limpio.")
