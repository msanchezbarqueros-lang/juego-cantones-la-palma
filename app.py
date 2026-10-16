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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO "RUN AN EMPIRE"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Personalizado
css_code = """
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
        color: #d0d7de;
        font-size: 1.05rem;
        margin-top: 6px;
    }

    /* Pestañas Principales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #161b22;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d;
        color: #ffffff !important;
        border-radius: 8px;
        font-weight: 700 !important;
        font-size: 1.05rem;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
        border: 2px solid #ffffff;
    }

    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #ffd700;
        border-radius: 8px;
        padding: 12px;
    }
    div[data-testid="stMetricLabel"] {
        color: #ffd700 !important;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* Barra lateral y Controles de Entrada en Blanco sobre Fondo Oscuro */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 2px solid #ffd700;
    }

    /* Cuadros de Entrada de Texto, Fechas y Tiempos: Letras Negras sobre Fondo Blanco */
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 6px;
    }

    /* Botones de Acción */
    .stButton button {
        background-color: #21262d !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
        border-radius: 8px !important;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
    }

    /* Estilo para la Tabla Blanca del Libro de Guerra */
    .tabla-libro-guerra {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff !important;
        color: #111111 !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        margin-top: 15px;
    }
    .tabla-libro-guerra th {
        background-color: #161b22 !important;
        color: #ffd700 !important;
        font-weight: bold;
        text-align: left;
        padding: 12px 15px;
        border-bottom: 3px solid #ffd700;
        font-size: 1rem;
    }
    .tabla-libro-guerra td {
        padding: 10px 15px;
        border-bottom: 1px solid #e1e4e8;
        color: #111111 !important;
        font-size: 0.95rem;
    }
    .tabla-libro-guerra tr:nth-child(even) {
        background-color: #f6f8fa !important;
    }
    .tabla-libro-guerra tr:hover {
        background-color: #eef2f5 !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI (La Palma)</div>
</div>
"""
st.markdown(css_code, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BANNER DE CUENTA ATRÁS EN TIEMPO REAL
# -----------------------------------------------------------------------------
component_timer_html = """
<div id="timer-box" style="
    background: linear-gradient(90deg, #161b22 0%, #21262d 100%);
    border: 2px solid #ffd700;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    color: #ffffff;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    margin-bottom: 15px;
">
    <div style="font-size: 0.95rem; color: #ffd700; font-weight: bold; letter-spacing: 1px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTA GPX (Cierre: 30 de Mayo de 2027 - 23:59)
    </div>
    <div id="countdown-display" style="font-size: 1.6rem; font-weight: 800; color: #00FF66; margin-top: 4px;">
        Cargando cuenta atrás...
    </div>
</div>

<script>
    const targetDate = new Date("2027-05-30T23:59:59").getTime();
    
    function updateCountdown() {
        const now = new Date().getTime();
        const difference = targetDate - now;
        
        if (difference <= 0) {
            document.getElementById("countdown-display").innerHTML = "🛑 CAMPAÑA FINALIZADA";
            document.getElementById("countdown-display").style.color = "#FF3333";
            return;
        }
        
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);
        
        document.getElementById("countdown-display").innerHTML = 
            "⏳ " + days + " Días | " + 
            (hours < 10 ? "0" : "") + hours + "h : " + 
            (minutes < 10 ? "0" : "") + minutes + "m : " + 
            (seconds < 10 ? "0" : "") + seconds + "s restantes";
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
</script>
"""
components.html(component_timer_html, height=90)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# DICCIONARIO OFICIAL DE LOS 11 ALUMNOS, ESCUDOS Y COLORES NEÓN
# -----------------------------------------------------------------------------
ALUMNOS_OFICIALES = {
    "Estrella": {"escudo": "⭐", "color": "#FF0055", "titulo": "Estrella de Cima"},
    "Yassine": {"escudo": "🦅", "color": "#00E5FF", "titulo": "Águila de Cumbre"},
    "Fabián": {"escudo": "⚔️", "color": "#00FF66", "titulo": "Lanzas Cruzadas"},
    "Claudia": {"escudo": "👑", "color": "#FFCC00", "titulo": "Corona de Mencey"},
    "Matías": {"escudo": "🌋", "color": "#FF6600", "titulo": "Volcán Tajogaite"},
    "Yeray": {"escudo": "🛡️", "color": "#AA00FF", "titulo": "Escudo Táctico"},
    "Adrián": {"escudo": "☀️", "color": "#76FF03", "titulo": "Sol de Roque"},
    "Yamila": {"escudo": "🌙", "color": "#00FFCC", "titulo": "Luna Aborigen"},
    "Gabriel": {"escudo": "⚡", "color": "#D500F9", "titulo": "Rayo de Cima"},
    "Juanmi": {"escudo": "🔥", "color": "#FF3333", "titulo": "Fuego de Cumbre"},
    "Paula": {"escudo": "💎", "color": "#3388FF", "titulo": "Diamante Guanche"}
}

# -----------------------------------------------------------------------------
# 2. CARGA DE CANTONES BENAHOARITAS
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
# 3. PROCESAMIENTO DE ARCHIVOS GPX Y PERSISTENCIA
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
        tipo = "⭕ Ruta Circular (Conquista Interior)"
    else:
        geom_conquista = geom_utm.buffer(franja_m)
        tipo = f"🚩 Ruta Lineal (Incursión {int(franja_m)}m)"
        
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
# 4. BARRA LATERAL DOCENTE CON CONTRASEÑA
# -----------------------------------------------------------------------------
st.sidebar.title("🛡️ PANEL DE CONTROL")
pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Docente Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Cargar Ruta GPX")
    
    alumno_sel = st.sidebar.selectbox("Seleccionar Alumno/a (11 Guerreros)", list(ALUMNOS_OFICIALES.keys()))
    info_est = ALUMNOS_OFICIALES[alumno_sel]
    
    st.sidebar.info(f"**Escudo:** {info_est['escudo']} {info_est['titulo']} | **Color:** {info_est['color']}")
    
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
                st.sidebar.success(f"¡Territorio registrado para {alumno_sel}!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX no válido.")
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
    st.sidebar.info("👁️ **Modo Estudiante (Solo Lectura)**")

# -----------------------------------------------------------------------------
# 5. CÁLCULO DE SOLAPAMIENTOS Y RANKINGS
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
                escudo = ALUMNOS_OFICIALES.get(alumno, {}).get("escudo", "🛡️")
                filas.append({
                    "Cantón": nombre_canton,
                    "Alumno/a": f"{escudo} {alumno}",
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm = calcular_dominios_actuales()
cantones_gdf = cargar_cantones_la_palma()

# -----------------------------------------------------------------------------
# 6. FUNCIÓN DE ANÁLISIS DETALLADO DEL HISTORIAL (ROBOS Y CANTONES)
# -----------------------------------------------------------------------------
def analizar_historial_completo(actividades, cantones_gdf):
    cantones_utm = cantones_gdf.to_crs("EPSG:32628")
    filas_historial = []
    
    dominios_temporales = {}
    
    for idx, act in enumerate(actividades):
        alumno = act['alumno']
        geom = act['geometria_utm']
        fecha_str = act['fecha'].strftime("%Y-%m-%d %H:%M")
        escudo = ALUMNOS_OFICIALES.get(alumno, {}).get("escudo", "🛡️")
        
        # 1. Identificar Cantones en los que transcurre la ruta
        cantones_afectados = []
        for _, c_row in cantones_utm.iterrows():
            c_nom = c_row['canton']
            c_geom = c_row['geometry']
            if geom.intersects(c_geom) and geom.intersection(c_geom).area > 0.1:
                cantones_afectados.append(c_nom)
                
        str_cantones = ", ".join(cantones_afectados) if cantones_afectados else "Fuera de Cantón"
        
        # 2. Identificar Territorio Robado a otros compañeros
        robos = []
        total_m2_robados = 0.0
        
        for otro_alumno, otro_geom in dominios_temporales.items():
            if otro_alumno != alumno and otro_geom is not None and not getattr(otro_geom, 'is_empty', True):
                if geom.intersects(otro_geom):
                    intersec = geom.intersection(otro_geom)
                    m2_robados = intersec.area
                    if m2_robados > 1.0:
                        ha_robadas = m2_robados / 10000.0
                        total_m2_robados += m2_robados
                        escudo_otro = ALUMNOS_OFICIALES.get(otro_alumno, {}).get("escudo", "🛡️")
                        robos.append(f"{ha_robadas:.2f} ha a {escudo_otro} {otro_alumno}")
                        
        if robos:
            total_ha_robadas = total_m2_robados / 10000.0
            str_robado = f"⚔️ <b>{total_ha_robadas:.2f} ha</b> (" + ", ".join(robos) + ")"
        else:
            str_robado = "🕊️ 0.00 ha (Sin robos)"
            
        # Actualizar dominios_temporales para la siguiente iteración
        for al in list(dominios_temporales.keys()):
            if dominios_temporales[al] is not None and not getattr(dominios_temporales[al], 'is_empty', True):
                dominios_temporales[al] = dominios_temporales[al].difference(geom)
                
        if alumno not in dominios_temporales or dominios_temporales[alumno] is None or getattr(dominios_temporales[alumno], 'is_empty', True):
            dominios_temporales[alumno] = geom
        else:
            dominios_temporales[alumno] = dominios_temporales[alumno].union(geom)
            
        filas_historial.append({
            "Fecha / Hora": fecha_str,
            "Guerrero/a": f"<b>{escudo} {alumno}</b>",
            "Cantón / Cantones": f"📍 {str_cantones}",
            "Territorio Robado": str_robado,
            "Tipo de Incursión": act['tipo'],
            "GPX": act['archivo']
        })
        
    return filas_historial

# -----------------------------------------------------------------------------
# 7. PESTAÑAS PRINCIPALES DE LA APLICACIÓN
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

with tab1:
    st.write("### 📍 Mapa de Dominio Territorial")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=10,
        min_zoom=10,
        tiles="OpenStreetMap"
    )
    m.fit_bounds([[28.40, -18.05], [28.90, -17.65]])
    
    # Capa de los 12 Cantones
    for _, row in cantones_gdf.iterrows():
        folium.GeoJson(
            sg.mapping(row['geometry']),
            style_function=lambda x: {
                'fillColor': '#21262d',
                'color': '#ffd700',
                'weight': 1.5,
                'fillOpacity': 0.15,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Municipio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Dominios de Alumnos con Escudos e Insignias Flotantes
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            perf = ALUMNOS_OFICIALES.get(alumno, {"escudo": "🛡️", "color": "#00E5FF", "titulo": "Guerrero/a"})
            
            # Polígono translúcido con el color de guerra
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=perf['color']: {
                    'fillColor': col,
                    'color': col,
                    'weight': 2.5,
                    'fillOpacity': 0.65
                },
                tooltip=f"<b>{perf['escudo']} {alumno} ({perf['titulo']})</b><br>Dominio: {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Marcador con el Escudo en el centroide de la conquista
            centroide = geom_wgs.centroid
            folium.Marker(
                location=[centroide.y, centroide.x],
                icon=folium.DivIcon(
                    html=f"""<div style="
                        font-size: 22px;
                        background: #161b22;
                        border: 2px solid {perf['color']};
                        border-radius: 50%;
                        width: 36px;
                        height: 36px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        box-shadow: 0 0 10px {perf['color']};
                    ">{perf['escudo']}</div>"""
                ),
                tooltip=f"<b>Dominio de {alumno}</b>"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        perf = ALUMNOS_OFICIALES.get(alumno, {"escudo": "🛡️", "titulo": "Guerrero/a"})
        ranking_data.append({
            "Guerrero/a": f"{perf['escudo']} {alumno}",
            "Título": perf['titulo'],
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Guerrero/a", "Título", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han registrado rutas. Utiliza el panel lateral para subir los primeros archivos GPX.")

with tab3:
    st.write("### 👑 Menceyes por Cantón")
    df_cantones = calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf)
    
    if not df_cantones.empty:
        cantones_conquistados = df_cantones["Cantón"].unique()
        
        st.write("#### 🤴 Líderes Actuales (Menceyes de Cantón)")
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
        
        st.write(f"### Clasificación en el Cantón de **{canton_sel}**")
        st.dataframe(
            df_canton_especifico[["Alumno/a", "Hectáreas (ha)", "% Conquistado del Cantón", "Superficie (m²)"]],
            use_container_width=True
        )
    else:
        st.info("Ningún cantón ha sido conquistado todavía.")

with tab4:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    
    if st.session_state.actividades:
        filas_hist = analizar_historial_completo(st.session_state.actividades, cantones_gdf)
        
        html_tabla = """
        <table class="tabla-libro-guerra">
            <thead>
                <tr>
                    <th>Fecha / Hora</th>
                    <th>Guerrero/a</th>
                    <th>📍 Cantón / Cantones</th>
                    <th>⚔️ Territorio Robado</th>
                    <th>Tipo de Incursión</th>
                    <th>Archivo GPX</th>
                </tr>
            </thead>
            <tbody>
        """
        for f in filas_hist:
            html_tabla += f"""
                <tr>
                    <td><b>{f['Fecha / Hora']}</b></td>
                    <td>{f['Guerrero/a']}</td>
                    <td>{f['Cantón / Cantones']}</td>
                    <td>{f['Territorio Robado']}</td>
                    <td>{f['Tipo de Incursión']}</td>
                    <td><code>{f['GPX']}</code></td>
                </tr>
            """
        html_tabla += """
            </tbody>
        </table>
        """
        
        st.markdown(html_tabla, unsafe_allow_html=True)
    else:
        st.info("Aún no se han registrado actividades en el Libro de Guerra.")
