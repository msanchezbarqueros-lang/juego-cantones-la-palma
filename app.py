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

# Estilo CSS Oscuro con Máximo Contraste
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
        background-color: #161b22 !important;
        border: 1.5px solid #ffd700 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
    }
    input {
        color: #ffffff !important;
        background-color: transparent !important;
        font-weight: bold !important;
    }
    
    /* Selector de Fecha y Hora en Fondo Blanco y Texto Negro */
    div[data-testid="stDateInput"] input, div[data-testid="stTimeInput"] input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 4px !important;
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
# 7. CÁLCULO DE SOLAPAMIENTOS Y RE-CONQUISTAS
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

# -----------------------------------------------------------------------------
# 8. INTERFAZ PRINCIPAL CON LAS 5 PESTAÑAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "⚡ CLASIFICACIÓN SEMANAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

# -----------------------------------------------------------------------------
# TAB 1: MAPA DE DOMINIO
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

    # Marcadores Flotantes de Escudo por Cada Ruta Individual
    for act in st.session_state.actividades:
        al = act['alumno']
        puntos = act.get('puntos', [])
        tipo = act.get('tipo', '')
        perf = ESTUDIANTES.get(al, {"escudo": "🛡️", "color": "#00E5FF"})
        color = perf["color"]
        escudo = perf["escudo"]
        
        if puntos and len(puntos) >= 3:
            is_circular = "⭕" in tipo or "Bucle" in tipo or "Circular" in tipo
            
            if is_circular:
                # Si la ruta es circular, el icono aparece en el centro de la forma
                try:
                    p_center = sg.Polygon(puntos).centroid
                    lat, lon = p_center.y, p_center.x
                except Exception:
                    p_center = sg.LineString(puntos).interpolate(0.5, normalized=True)
                    lat, lon = p_center.y, p_center.x
            else:
                # Si la ruta es lineal, el icono aparece encima de la línea (midpoint)
                p_mid = sg.LineString(puntos).interpolate(0.5, normalized=True)
                lat, lon = p_mid.y, p_mid.x
                
            icon_html = f'<div style="background-color: #161b22; border: 2.5px solid {color}; border-radius: 50%; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center; font-size: 17px; box-shadow: 0 0 10px {color};">{escudo}</div>'
            
            folium.Marker(
                location=[lat, lon],
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"<b>{escudo} Guerrero: {al}</b><br>📁 {act.get('archivo', 'gpx')}<br>📅 {act['fecha'].strftime('%Y-%m-%d %H:%M')}<br>🚩 {tipo}"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

# -----------------------------------------------------------------------------
# TAB 2: CLASIFICACIÓN GENERAL
# -----------------------------------------------------------------------------
with tab2:
    st.write("### 🏆 Ranking General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        perf = ESTUDIANTES.get(alumno, {"escudo": "🛡️"})
        ranking_data.append({
            "Guerrero/a": f"{perf['escudo']} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Guerrero/a", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han registrado rutas. El profesor debe registrar los primeros tracks GPX.")

# -----------------------------------------------------------------------------
# TAB 3: CLASIFICACIÓN SEMANAL
# -----------------------------------------------------------------------------
with tab3:
    st.write("### ⚡ Clasificación Semanal de Conquista")
    
    if st.session_state.actividades:
        # Agrupar actividades por semana
        semanas_dict = {}
        for act in st.session_state.actividades:
            f = act['fecha']
            year, week, _ = f.isocalendar()
            key = f"{year}-W{week:02d}"
            
            # Calcular rango de fechas de esa semana
            f_inicio = f - timedelta(days=f.weekday())
            f_fin = f_inicio + timedelta(days=6)
            str_rango = f"Semana {week} ({f_inicio.strftime('%d %b')} - {f_fin.strftime('%d %b %Y')})"
            
            if key not in semanas_dict:
                semanas_dict[key] = {
                    "label": str_rango,
                    "actividades": []
                }
            semanas_dict[key]["actividades"].append(act)
            
        # Determinar semana actual y semana anterior
        now_dt = datetime.now()
        cur_year, cur_week, _ = now_dt.isocalendar()
        prev_dt = now_dt - timedelta(days=7)
        prev_year, prev_week, _ = prev_dt.isocalendar()
        key_prev = f"{prev_year}-W{prev_week:02d}"
        key_cur = f"{cur_year}-W{cur_week:02d}"
        
        # Generar lista de semanas elegibles
        opciones_semanas = []
        keys_semanas = sorted(list(semanas_dict.keys()), reverse=True)
        
        # Si la semana previa no tiene rutas grabadas pero queremos listarla, podemos construirla
        for k in keys_semanas:
            lbl = semanas_dict[k]["label"]
            if k == key_prev:
                lbl += " ⭐ [SEMANA ANTERIOR]"
            elif k == key_cur:
                lbl += " 🚩 [SEMANA ACTUAL]"
            opciones_semanas.append((lbl, k))
            
        # Índice por defecto: la semana anterior si existe, o la primera opción
        idx_def = 0
        for idx, (lbl, k) in enumerate(opciones_semanas):
            if k == key_prev:
                idx_def = idx
                break
                
        semana_sel_lbl = st.selectbox(
            "📅 Seleccionar Semana de Campaña para Inspeccionar:",
            [o[0] for o in opciones_semanas],
            index=idx_def
        )
        
        key_sel = [o[1] for o in opciones_semanas if o[0] == semana_sel_lbl][0]
        acts_semana = semanas_dict[key_sel]["actividades"]
        
        # Calcular ranking de la semana seleccionada
        cantones_utm = cantones_gdf.to_crs("EPSG:32628")
        stats_semana = {}
        for act in acts_semana:
            al = act['alumno']
            geom = act['geometria_utm']
            area_m2 = geom.area
            
            # Detectar cantones cruzados
            cants_cruzados = []
            for _, crow in cantones_utm.iterrows():
                if geom.intersects(crow['geometry']):
                    cants_cruzados.append(crow['canton'])
                    
            if al not in stats_semana:
                stats_semana[al] = {
                    "area_m2": 0.0,
                    "rutas": 0,
                    "cantones": set()
                }
            stats_semana[al]["area_m2"] += area_m2
            stats_semana[al]["rutas"] += 1
            stats_semana[al]["cantones"].update(cants_cruzados)
            
        # Generar DataFrame semanal
        filas_sem = []
        for al, data in stats_semana.items():
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️"})
            cants_str = ", ".join(sorted(list(data["cantones"]))) if data["cantones"] else "Ninguno"
            filas_sem.append({
                "Guerrero/a": f"{perf['escudo']} {al}",
                "Hectáreas Sumadas (ha)": round(data["area_m2"] / 10000.0, 2),
                "Superficie (m²)": round(data["area_m2"], 2),
                "Rutas Realizadas": data["rutas"],
                "Cantones Explorados": cants_str,
                "raw_m2": data["area_m2"]
            })
            
        df_sem = pd.DataFrame(filas_sem).sort_values(by="raw_m2", ascending=False)
        
        # Podio Semanal
        if not df_sem.empty:
            lider_sem = df_sem.iloc[0]
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #21262d 0%, #161b22 100%);
                border: 2px solid #ffd700;
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
            ">
                <div style="color: #ffd700; font-size: 1.1rem; font-weight: bold;">🥇 CAMPEÓN/A DE LA SEMANA</div>
                <div style="color: #ffffff; font-size: 1.8rem; font-weight: 800; margin: 6px 0;">{lider_sem['Guerrero/a']}</div>
                <div style="color: #00FF66; font-size: 1.2rem; font-weight: bold;">+ {lider_sem['Hectáreas Sumadas (ha)']} ha ganadas en esta semana ({lider_sem['Rutas Realizadas']} rutas)</div>
            </div>
            """, unsafe_allow_html=True)
            
            df_sem["Posición"] = [f"🥇 1.º", "🥈 2.º", "🥉 3.º"] + [f"🏅 {i}º" for i in range(4, len(df_sem) + 1)] if len(df_sem) >= 3 else [f"🏅 {i+1}º" for i in range(len(df_sem))]
            df_sem = df_sem[["Posición", "Guerrero/a", "Hectáreas Sumadas (ha)", "Superficie (m²)", "Rutas Realizadas", "Cantones Explorados"]]
            st.dataframe(df_sem, use_container_width=True)
    else:
        st.info("Aún no hay rutas registradas para calcular las clasificaciones semanales.")

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
# TAB 5: LIBRO DE GUERRA
# -----------------------------------------------------------------------------
with tab5:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    
    if st.session_state.actividades:
        cantones_utm = cantones_gdf.to_crs("EPSG:32628")
        
        # Calcular cronológicamente las incursiones y robos
        dominios_historicos = {}
        filas_html = []
        
        for act in st.session_state.actividades:
            al = act['alumno']
            geom = act['geometria_utm']
            fecha_str = act['fecha'].strftime("%Y-%m-%d %H:%M")
            tipo = act['tipo']
            archivo = act['archivo']
            perf = ESTUDIANTES.get(al, {"escudo": "🛡️"})
            escudo_nombre = f"{perf['escudo']} {al}"
            
            # Detectar cantones cruzados por la ruta
            cantones_afectados = []
            for _, crow in cantones_utm.iterrows():
                if geom.intersects(crow['geometry']):
                    cantones_afectados.append(crow['canton'])
            cantones_str = "📍 " + ", ".join(cantones_afectados) if cantones_afectados else "📍 En tránsito"
            
            # Calcular robos
            robos_dict = {}
            area_robada_total = 0.0
            
            for prev_al, prev_geom in dominios_historicos.items():
                if prev_al != al and prev_geom is not None and not getattr(prev_geom, 'is_empty', True):
                    interseccion = geom.intersection(prev_geom)
                    if not getattr(interseccion, 'is_empty', True):
                        area_int = interseccion.area
                        if area_int > 1.0: # Umbral mínimo de 1 m²
                            robos_dict[prev_al] = area_int
                            area_robada_total += area_int
                            
            # Actualizar dominios históricos
            for prev_al in list(dominios_historicos.keys()):
                if dominios_historicos[prev_al] is not None and not getattr(dominios_historicos[prev_al], 'is_empty', True):
                    dominios_historicos[prev_al] = dominios_historicos[prev_al].difference(geom)
                    
            if al not in dominios_historicos or dominios_historicos[al] is None or getattr(dominios_historicos[al], 'is_empty', True):
                dominios_historicos[al] = geom
            else:
                dominios_historicos[al] = dominios_historicos[al].union(geom)
                
            # Formatear texto de robos
            if robos_dict:
                desglose = []
                for victim, a_m2 in robos_dict.items():
                    v_perf = ESTUDIANTES.get(victim, {"escudo": "🛡️"})
                    desglose.append(f"{round(a_m2/10000.0, 2)} ha a {v_perf['escudo']} {victim}")
                str_robos = f"⚔️ <b>{round(area_robada_total/10000.0, 2)} ha</b> ({', '.join(desglose)})"
            else:
                str_robos = "🕊️ 0.00 ha (Sin robos)"
                
            filas_html.append(f"""
            <tr style="border-bottom: 1px solid #e2e8f0; background-color: #ffffff;">
                <td style="padding: 12px; color: #111111; font-weight: 700; white-space: nowrap;">{fecha_str}</td>
                <td style="padding: 12px; color: #111111; font-weight: 800; font-size: 1.05rem; white-space: nowrap;">{escudo_nombre}</td>
                <td style="padding: 12px; color: #0f172a; font-weight: 600;">{cantones_str}</td>
                <td style="padding: 12px; color: #111111; font-weight: 600;">{str_robos}</td>
                <td style="padding: 12px; color: #334155; font-weight: 600;">{tipo}</td>
                <td style="padding: 12px; color: #0284c7; font-family: monospace; font-size: 0.9rem;"><code>{archivo}</code></td>
            </tr>
            """)
            
        tabla_html = f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 10px;
            max-height: 550px;
            overflow-y: auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        ">
            <table style="width: 100%; border-collapse: collapse; text-align: left; font-family: sans-serif;">
                <thead>
                    <tr style="background-color: #161b22; color: #ffd700; border-bottom: 2px solid #ffd700;">
                        <th style="padding: 12px; font-weight: 800; border-top-left-radius: 6px;">📅 Fecha/Hora</th>
                        <th style="padding: 12px; font-weight: 800;">👑 Conquistador/a</th>
                        <th style="padding: 12px; font-weight: 800;">📍 Cantón / Cantones</th>
                        <th style="padding: 12px; font-weight: 800;">⚔️ Territorio Robado</th>
                        <th style="padding: 12px; font-weight: 800;">🚩 Tipo de Ruta</th>
                        <th style="padding: 12px; font-weight: 800; border-top-right-radius: 6px;">📁 Archivo GPX</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(filas_html)}
                </tbody>
            </table>
        </div>
        """
        components.html(tabla_html, height=580, scrolling=True)
    else:
        st.info("El historial de guerra está limpio.")
