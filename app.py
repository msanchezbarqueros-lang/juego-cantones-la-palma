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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO TÁCTICO "RUN AN EMPIRE"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Oscuro con Máximo Contraste para Todos los Botones y Formularios
st.markdown("""
<style>
    /* Fondo principal y textos */
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
        font-size: 1rem;
        margin-top: 5px;
    }

    /* Estilo para los botones en Streamlit */
    .stButton > button, div.stButton > button, button[kind="primary"], button[kind="secondary"] {
        background-color: #21262d !important;
        color: #ffd700 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover, div.stButton > button:hover {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
        border-color: #ffffff !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.6) !important;
    }

    /* Formulario de Entrada, Inputs y Selects */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #ffd700 !important;
        border-radius: 6px !important;
        color: #000000 !important;
    }
    input {
        color: #000000 !important;
        background-color: transparent !important;
        font-weight: bold !important;
    }
    
    /* Selector de Fecha y Hora con texto NEGRO sobre fondo blanco */
    div[data-testid="stDateInput"] input, div[data-testid="stTimeInput"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
    }
    label, p, span {
        color: #ffffff !important;
    }

    /* File Uploader (Subida de GPX) */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #161b22 !important;
        border: 2px dashed #ffd700 !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }
    section[data-testid="stFileUploadDropzone"] span {
        color: #ffffff !important;
    }
    section[data-testid="stFileUploadDropzone"] button {
        background-color: #21262d !important;
        color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
    }
    .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        border: 1px solid #ffffff !important;
    }
    .stTabs [aria-selected="true"] p, .stTabs [aria-selected="true"] span {
        color: #0d1117 !important;
        font-weight: 800 !important;
    }

    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-left: 5px solid #ffd700 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.6) !important;
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
        border-right: 1px solid #ffd700 !important;
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
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
">
    <div style="color: #ffd700; font-size: 0.95rem; font-weight: bold; letter-spacing: 1px; margin-bottom: 4px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTA GPX (Cierre: 30 de Mayo - 23:59)
    </div>
    <div id="timer" style="color: #ffffff; font-size: 1.5rem; font-weight: 800; font-family: monospace;">
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
# 7. CÁLCULO DE SOLAPAMIENTOS, ROBOS Y DOMINIOS
# -----------------------------------------------------------------------------
def calcular_dominios_y_robos():
    dominios = {}
    robos_realizados = {al: 0.0 for al in ESTUDIANTES.keys()}
    robos_sufridos = {al: 0.0 for al in ESTUDIANTES.keys()}
    registro_robos_actividad = []

    for act in st.session_state.actividades:
        alumno = act['alumno']
        nueva_geom = act['geometria_utm']
        
        robado_esta_ruta = 0.0
        desglose_robos = []
        
        for al_prev in list(dominios.keys()):
            if al_prev != alumno and dominios[al_prev] is not None and not getattr(dominios[al_prev], 'is_empty', True):
                interseccion = dominios[al_prev].intersection(nueva_geom)
                area_robada_m2 = interseccion.area
                if area_robada_m2 > 0.5:
                    robado_esta_ruta += area_robada_m2
                    robos_realizados[alumno] += area_robada_m2
                    robos_sufridos[al_prev] += area_robada_m2
                    
                    escudo_v = ESTUDIANTES.get(al_prev, {}).get("escudo", "🛡️")
                    desglose_robos.append(f"{round(area_robada_m2/10000.0, 2)} ha a {escudo_v} {al_prev}")
                    
                dominios[al_prev] = dominios[al_prev].difference(nueva_geom)
                
        if alumno not in dominios or dominios[alumno] is None or getattr(dominios[alumno], 'is_empty', True):
            dominios[alumno] = nueva_geom
        else:
            dominios[alumno] = dominios[alumno].union(nueva_geom)
            
        if robado_esta_ruta > 0.5:
            texto_robo = f"⚔️ <b>{round(robado_esta_ruta/10000.0, 2)} ha</b> ({', '.join(desglose_robos)})"
        else:
            texto_robo = "🕊️ 0.00 ha (Sin robos)"
            
        registro_robos_actividad.append(texto_robo)
            
    return dominios, robos_realizados, robos_sufridos, registro_robos_actividad

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

dominios_utm, robos_realizados, robos_sufridos, registro_robos_actividad = calcular_dominios_y_robos()
cantones_gdf = cargar_cantones_la_palma()

# -----------------------------------------------------------------------------
# 8. INTERFAZ PRINCIPAL CON PESTAÑAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "⚡ CLASIFICACIÓN SEMANAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

# -----------------------------------------------------------------------------
# TAB 1: MAPA DE DOMINIO CON ICONO EN CADA RUTA
# -----------------------------------------------------------------------------
with tab1:
    st.write("### 📍 Mapa Táctico de La Palma")
    
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
            
    # Iconos por Cada Ruta Individual Subida
    for act in st.session_state.actividades:
        alumno = act['alumno']
        puntos = act.get('puntos', [])
        tipo = act['tipo']
        archivo = act['archivo']
        fecha_str = act['fecha'].strftime("%Y-%m-%d %H:%M")
        
        perf = ESTUDIANTES.get(alumno, {"escudo": "🛡️", "color": "#00E5FF"})
        color = perf["color"]
        escudo = perf["escudo"]
        
        if len(puntos) >= 3:
            if "⭕" in tipo or "Bucle" in tipo:
                pol = sg.Polygon(puntos)
                p_ref = pol.centroid
            else:
                lin = sg.LineString(puntos)
                p_ref = lin.interpolate(0.5, normalized=True)
                
            icon_html = f'<div style="background-color: #161b22; border: 2px solid {color}; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 0 8px {color};">{escudo}</div>'
            
            folium.Marker(
                location=[p_ref.y, p_ref.x],
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"<b>{escudo} {alumno}</b><br>📁 {archivo}<br>📅 {fecha_str}<br>🚩 {tipo}"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

# -----------------------------------------------------------------------------
# TAB 2: CLASIFICACIÓN GENERAL
# -----------------------------------------------------------------------------
with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    for alumno, perf in ESTUDIANTES.items():
        geom = dominios_utm.get(alumno, None)
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        
        m2_robados = robos_realizados.get(alumno, 0.0)
        m2_perdidos = robos_sufridos.get(alumno, 0.0)
        
        ranking_data.append({
            "Guerrero/a": f"{perf['escudo']} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "km² que he robado (total)": round(m2_robados / 1_000_000.0, 4),
            "km² que me han robado (total)": round(m2_perdidos / 1_000_000.0, 4)
        })
        
    df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (km²)", ascending=False)
    df_ranking.index = range(1, len(df_ranking) + 1)
    st.dataframe(df_ranking, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: CLASIFICACIÓN SEMANAL (SEMANA ACTUAL Y ANTERIOR)
# -----------------------------------------------------------------------------
with tab3:
    st.write("### ⚡ Clasificación Semanal de Conquista")
    
    now = datetime.now()
    year_cur, week_cur, _ = now.isocalendar()
    
    dt_prev = now - timedelta(days=7)
    year_prev, week_prev, _ = dt_prev.isocalendar()
    
    opciones_semana = {
        f"Semana Actual (S{week_cur})": (year_cur, week_cur),
        f"Semana Anterior (S{week_prev})": (year_prev, week_prev)
    }
    
    sel_nombre = st.selectbox("📅 Seleccionar Semana de Campaña:", list(opciones_semana.keys()), index=1)
    target_year, target_week = opciones_semana[sel_nombre]
    
    actividades_semana = [
        act for act in st.session_state.actividades 
        if act['fecha'].isocalendar()[0] == target_year and act['fecha'].isocalendar()[1] == target_week
    ]
    
    if actividades_semana:
        rendimiento = {}
        cantones_utm = cantones_gdf.to_crs("EPSG:32628")
        
        for act in actividades_semana:
            al = act['alumno']
            geom = act['geometria_utm']
            area_m2 = geom.area
            
            if al not in rendimiento:
                rendimiento[al] = {'area_m2': 0.0, 'rutas': 0, 'cantones': set()}
                
            rendimiento[al]['area_m2'] += area_m2
            rendimiento[al]['rutas'] += 1
            
            for _, crow in cantones_utm.iterrows():
                if geom.intersects(crow['geometry']):
                    rendimiento[al]['cantones'].add(crow['canton'])
                    
        filas_sem = []
        for al, datos in rendimiento.items():
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️"})
            c_str = ", ".join(sorted(list(datos['cantones']))) if datos['cantones'] else "Sin cantón"
            filas_sem.append({
                "Alumno": al,
                "Guerrero/a": f"{perf['escudo']} {al}",
                "Hectáreas Sumadas (ha)": round(datos['area_m2'] / 10000.0, 2),
                "Superficie (m²)": round(datos['area_m2'], 2),
                "Rutas Realizadas": datos['rutas'],
                "Cantones Explorados": c_str
            })
            
        df_sem = pd.DataFrame(filas_sem).sort_values(by="Superficie (m²)", ascending=False)
        
        lider = df_sem.iloc[0]
        lider_perf = ESTUDIANTES.get(lider['Alumno'], {"escudo": "🥇"})
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1f242d 0%, #0d1117 100%); border: 2px solid #ffd700; border-radius: 10px; padding: 15px; margin-bottom: 20px; text-align: center;">
            <div style="color: #ffd700; font-size: 1.1rem; font-weight: bold;">🥇 CAMPEÓN/A DE LA {sel_nombre.upper()}</div>
            <div style="color: #ffffff; font-size: 2rem; font-weight: 800; margin: 8px 0;">{lider_perf['escudo']} {lider['Alumno']}</div>
            <div style="color: #00FF66; font-size: 1.2rem; font-weight: bold;">+{lider['Hectáreas Sumadas (ha)']} ha conquistadas en esta semana ({lider['Rutas Realizadas']} rutas)</div>
        </div>
        """, unsafe_allow_html=True)
        
        df_sem.index = [f"🏅 #{i+1}" for i in range(len(df_sem))]
        if len(df_sem) >= 1: df_sem.index.values[0] = "🥇 1º"
        if len(df_sem) >= 2: df_sem.index.values[1] = "🥈 2º"
        if len(df_sem) >= 3: df_sem.index.values[2] = "🥉 3º"
        
        st.dataframe(df_sem[["Guerrero/a", "Hectáreas Sumadas (ha)", "Superficie (m²)", "Rutas Realizadas", "Cantones Explorados"]], use_container_width=True)
    else:
        st.info(f"No hay incursiones registradas para la **{sel_nombre}**.")

# -----------------------------------------------------------------------------
# TAB 4: MENCEYES POR CANTÓN
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
# TAB 5: LIBRO DE GUERRA CON TABLA BLANCA SCROLLABLE Y DETALLE DE ROBOS
# -----------------------------------------------------------------------------
with tab5:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    
    if st.session_state.actividades:
        cantones_utm = cantones_gdf.to_crs("EPSG:32628")
        filas_html = []
        
        for idx, act in enumerate(st.session_state.actividades):
            al = act['alumno']
            fecha_str = act['fecha'].strftime("%Y-%m-%d %H:%M")
            tipo = act['tipo']
            archivo = act['archivo']
            geom = act['geometria_utm']
            
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️"})
            escudo = perf["escudo"]
            
            cantones_cruzados = []
            for _, crow in cantones_utm.iterrows():
                if geom.intersects(crow['geometry']):
                    cantones_cruzados.append(crow['canton'])
            cant_str = f"📍 {', '.join(cantones_cruzados)}" if cantones_cruzados else "📍 Fuera de Cantón"
            
            texto_robo = registro_robos_actividad[idx] if idx < len(registro_robos_actividad) else "🕊️ 0.00 ha (Sin robos)"
            bg_color = "#ffffff" if idx % 2 == 0 else "#f8fafc"
            
            filas_html.append(f"""
            <tr style="border-bottom: 1px solid #cbd5e1; background-color: {bg_color};">
                <td style="padding: 12px; color: #111111; font-weight: 700;">{fecha_str}</td>
                <td style="padding: 12px; color: #111111; font-weight: 800; font-size: 1.05rem;">{escudo} {al}</td>
                <td style="padding: 12px; color: #0f172a; font-weight: 600;">{cant_str}</td>
                <td style="padding: 12px; color: #111111; font-weight: 600;">{texto_robo}</td>
                <td style="padding: 12px; color: #334155; font-weight: 600;">{tipo}</td>
                <td style="padding: 12px; color: #0284c7; font-family: monospace; font-size: 0.9rem;">{archivo}</td>
            </tr>
            """)
            
        tabla_html = f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 10px;
            max-height: 600px;
            overflow-y: auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        ">
            <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.95rem;">
                <thead>
                    <tr style="background-color: #161b22; color: #ffd700; text-align: left; border-bottom: 2px solid #ffd700;">
                        <th style="padding: 12px;">📅 Fecha/Hora</th>
                        <th style="padding: 12px;">👑 Conquistador/a</th>
                        <th style="padding: 12px;">📍 Cantón / Cantones</th>
                        <th style="padding: 12px;">⚔️ Territorio Robado</th>
                        <th style="padding: 12px;">🚩 Tipo de Ruta</th>
                        <th style="padding: 12px;">📁 Archivo GPX</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(filas_html)}
                </tbody>
            </table>
        </div>
        """
        components.html(tabla_html, height=620)
    else:
        st.info("El historial de guerra está limpio.")
