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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Personalizado
st.markdown("""
<style>
    /* Fondo principal y textos */
    .stApp {
        background-color: #0d1117;
        color: #f0f6fc;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Encabezado Principal */
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
        color: #ffffff;
        font-size: 1.05rem;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Pestañas Principales en Blanco y Negrita */
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
        font-size: 1.05rem !important;
        padding: 10px 20px;
        border: 1px solid #484f58;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
        border: 2px solid #ffffff !important;
    }

    /* Tarjetas de Métricas de Menceyes */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 5px solid #ffd700;
        border-radius: 8px;
        padding: 14px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.4);
    }
    div[data-testid="stMetricLabel"] {
        color: #ffd700 !important;
        font-weight: bold;
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 1.4rem !important;
    }

    /* BARRA LATERAL Y INPUTS DEL DOCENTE - CONTRASTE EN NEGRO Y FONDO BLANCO */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 2px solid #30363d;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label {
        color: #ffd700 !important;
        font-weight: 700 !important;
    }

    /* Cuadros de texto, contraseña, fecha y hora en NEGRO sobre fondo BLANCO */
    section[data-testid="stSidebar"] input[type="text"],
    section[data-testid="stSidebar"] input[type="password"],
    section[data-testid="stSidebar"] input[type="date"],
    section[data-testid="stSidebar"] input[type="time"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] div {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: 2px solid #ffd700 !important;
    }

    /* Selectbox de Streamlit en blanco y negro */
    div[data-baseweb="select"] * {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Botones de la barra lateral */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #21262d !important;
        color: #ffd700 !important;
        font-weight: 800 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 8px !important;
        width: 100%;
        padding: 10px;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
    }

    /* File Uploader en la barra lateral */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background-color: #0d1117 !important;
        border: 2px dashed #ffd700 !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo Organización de Itinerarios (OHI)</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BANNER CON TEMPORIZADOR DINÁMICO EN TIEMPO REAL (JS)
# -----------------------------------------------------------------------------
FECHA_LIMITE_ISO = "2027-05-30T23:59:59"

components.html(f"""
<div id="countdown-banner" style="
    background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
    border: 2px solid #ffd700;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
    color: #ffffff;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    margin-bottom: 10px;
">
    <div style="font-size: 1.1rem; font-weight: 800; color: #ffd700; text-transform: uppercase; letter-spacing: 1px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTAS GPX (Cierre: 30 de Mayo - 23:59)
    </div>
    <div id="timer-display" style="font-size: 1.6rem; font-weight: 900; color: #ffffff; margin-top: 6px;">
        Cargando cuenta atrás...
    </div>
</div>

<script>
    const targetDate = new Date("{FECHA_LIMITE_ISO}").getTime();

    function updateCountdown() {{
        const now = new Date().getTime();
        const distance = targetDate - now;

        if (distance < 0) {{
            document.getElementById("timer-display").innerHTML = "<span style='color: #ef4444;'>🛑 CAMPAÑA FINALIZADA</span>";
            return;
        }}

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById("timer-display").innerHTML = 
            "⏳ <span style='color: #a855f7;'>" + days + "</span> Días | " +
            "<span style='color: #38bdf8;'>" + String(hours).padStart(2, '0') + "</span>h : " +
            "<span style='color: #4ade80;'>" + String(minutes).padStart(2, '0') + "</span>m : " +
            "<span style='color: #facc15;'>" + String(seconds).padStart(2, '0') + "</span>s restantes";
    }}

    updateCountdown();
    setInterval(updateCountdown, 1000);
</script>
""", height=105)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# 3. BASE DE DATOS DE LOS 11 ESTUDIANTES DEL GRUPO
# -----------------------------------------------------------------------------
ESTUDIANTES_OFICIALES = {
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
# 4. CARGA DE CANTONES Y PROCESAMIENTO GEOGRÁFICO
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
        return None, "Error: Puntos insuficientes"
        
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
# 5. BARRA LATERAL (CONTROL DOCENTE)
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DOCENTE")

pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Acceso Docente Concedido")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Cargar Ruta GPX")
    
    lista_alumnos = list(ESTUDIANTES_OFICIALES.keys())
    alumno_sel = st.sidebar.selectbox("Seleccionar Alumno/a", lista_alumnos)
    info_est = ESTUDIANTES_OFICIALES[alumno_sel]
    
    st.sidebar.info(f"**Escudo:** {info_est['escudo']} {info_est['titulo']}")
    
    fecha_ruta = st.sidebar.date_input("Fecha de la Ruta", value=datetime.now())
    hora_ruta = st.sidebar.time_input("Hora de la Ruta", value=datetime.now().time())
    archivo_gpx = st.sidebar.file_uploader("Subir archivo .gpx", type=["gpx"])
    
    if st.sidebar.button("⚔️ CONQUISTAR TERRITORIO"):
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
                st.sidebar.success(f"¡Ruta de {alumno_sel} registrada con éxito!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX sin puntos válidos.")
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
    st.sidebar.info("👁️ **Modo Estudiante** - Registro público de la Conquista de los 12 Cantones.")

# -----------------------------------------------------------------------------
# 6. CÁLCULOS TERRITORIALES, INTERSECCIONES Y ROBOS
# -----------------------------------------------------------------------------
cantones_gdf = cargar_cantones_la_palma()

def calcular_historial_y_dominios_actuales():
    dominios = {}
    historial_procesado = []
    cantones_utm = cantones_gdf.to_crs("EPSG:32628")
    
    for act in st.session_state.actividades:
        alumno = act['alumno']
        nueva_geom = act['geometria_utm']
        escudo = ESTUDIANTES_OFICIALES.get(alumno, {}).get('escudo', '🛡️')
        
        # 1. Identificar cantones por los que discurre la ruta
        cantones_intersectados = []
        for _, c_row in cantones_utm.iterrows():
            if nueva_geom.intersects(c_row['geometry']):
                cantones_intersectados.append(c_row['canton'])
                
        str_cantones = ", ".join(cantones_intersectados) if cantones_intersectados else "Fuera de Cantón"
        
        # 2. Calcular robos a otros compañeros
        robos = {}
        area_robada_total = 0.0
        
        for al_existente in list(dominios.keys()):
            if al_existente != alumno and dominios[al_existente] is not None and not getattr(dominios[al_existente], 'is_empty', True):
                interseccion_robo = dominios[al_existente].intersection(nueva_geom)
                if not getattr(interseccion_robo, 'is_empty', True):
                    area_m2 = interseccion_robo.area
                    if area_m2 > 10.0: # Umbral de más de 10m²
                        escudo_victima = ESTUDIANTES_OFICIALES.get(al_existente, {}).get('escudo', '🛡️')
                        robos[f"{escudo_victima} {al_existente}"] = area_m2 / 10000.0 # en hectáreas
                        area_robada_total += (area_m2 / 10000.0)
                        
                        # Restar territorio al compañero robado
                        dominios[al_existente] = dominios[al_existente].difference(nueva_geom)
                        
        if alumno not in dominios or dominios[alumno] is None or getattr(dominios[alumno], 'is_empty', True):
            dominios[alumno] = nueva_geom
        else:
            dominios[alumno] = dominios[alumno].union(nueva_geom)
            
        # Formatear texto de robo
        if robos:
            desglose = ", ".join([f"{ha:.2f} ha a {vic}" for vic, ha in robos.items()])
            txt_robo = f"⚔️ <b>{area_robada_total:.2f} ha</b> ({desglose})"
        else:
            txt_robo = "🕊️ 0.00 ha (Sin robos)"
            
        historial_procesado.append({
            "fecha": act['fecha'].strftime("%Y-%m-%d %H:%M"),
            "alumno": f"{escudo} {alumno}",
            "cantones": f"📍 {str_cantones}",
            "robo": txt_robo,
            "tipo": act['tipo'],
            "archivo": act['archivo']
        })
        
    return dominios, historial_procesado

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
                escudo = ESTUDIANTES_OFICIALES.get(alumno, {}).get('escudo', '🛡️')
                filas.append({
                    "Cantón": nombre_canton,
                    "Alumno/a": f"{escudo} {alumno}",
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm, historial_completo = calcular_historial_y_dominios_actuales()

# -----------------------------------------------------------------------------
# 7. INTERFAZ WEB CON PESTAÑAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

with tab1:
    st.write("### 📍 Mapa Táctico Ilustrado de La Palma")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=10,
        min_zoom=10,
        max_zoom=18,
        max_bounds=True,
        tiles="OpenStreetMap"
    )
    m.fit_bounds([[28.35, -18.05], [28.95, -17.60]])
    
    # Capa de Cantones
    for _, row in cantones_gdf.iterrows():
        folium.GeoJson(
            sg.mapping(row['geometry']),
            style_function=lambda x: {
                'fillColor': '#e2e8f0',
                'color': '#d97706',
                'weight': 2.0,
                'fillOpacity': 0.15,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Territorio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Dominios de Estudiantes
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            perf = ESTUDIANTES_OFICIALES.get(alumno, {"escudo": "🛡️", "color": "#00E5FF"})
            color = perf['color']
            escudo = perf['escudo']
            
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=color: {
                    'fillColor': col,
                    'color': col,
                    'weight': 3.0,
                    'fillOpacity': 0.60
                },
                tooltip=f"<b>{escudo} Dominio de:</b> {alumno}<br><b>Superficie:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Insignia flotante con el Escudo en el Centroide de la Conquista
            centroide = geom_wgs.centroid
            icon_html = f'''<div style="font-size: 22px; background: #0d1117; border: 2px solid {color}; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 6px rgba(0,0,0,0.6);">{escudo}</div>'''
            
            folium.Marker(
                location=[centroide.y, centroide.x],
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"<b>{escudo} {alumno}</b>"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        escudo = ESTUDIANTES_OFICIALES.get(alumno, {}).get('escudo', '🛡️')
        ranking_data.append({
            "Conquistador/a": f"{escudo} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Conquistador/a", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no hay territorios conquistados. El docente debe registrar las primeras rutas GPX.")

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
                    value=f"👑 {lider['Alumno/a']}",
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
# TAB 4: LIBRO DE GUERRA (TABLA CON FONDO BLANCO Y RENDER HTML CORRECTO)
# -----------------------------------------------------------------------------
with tab4:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    st.markdown("*Historial cronológico de incursiones territoriales, cantones afectados y re-conquistas.*")
    
    if historial_completo:
        filas_html = ""
        for act in reversed(historial_completo):
            filas_html += f"""
            <tr style="border-bottom: 1px solid #cbd5e1; background-color: #ffffff;">
                <td style="padding: 12px; color: #111111; font-weight: 700;">{act['fecha']}</td>
                <td style="padding: 12px; color: #111111; font-weight: 800; font-size: 1.05rem;">{act['alumno']}</td>
                <td style="padding: 12px; color: #0f172a; font-weight: 600;">{act['cantones']}</td>
                <td style="padding: 12px; color: #111111; font-weight: 600;">{act['robo']}</td>
                <td style="padding: 12px; color: #334155; font-weight: 600;">{act['tipo']}</td>
                <td style="padding: 12px; color: #0284c7; font-family: monospace; font-size: 0.9rem;">{act['archivo']}</td>
            </tr>
            """
            
        tabla_html = f"""
        <div style="
            background-color: #ffffff;
            border: 2px solid #ffd700;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            margin-top: 15px;
            overflow-x: auto;
        ">
            <table style="
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                font-family: 'Segoe UI', Tahoma, sans-serif;
            ">
                <thead>
                    <tr style="background-color: #161b22; border-bottom: 3px solid #ffd700;">
                        <th style="padding: 12px; color: #ffd700; font-weight: 800; font-size: 1rem;">📅 Fecha/Hora</th>
                        <th style="padding: 12px; color: #ffd700; font-weight: 800; font-size: 1rem;">👑 Conquistador/a</th>
                        <th style="padding: 12px; color: #ffd700; font-weight: 800; font-size: 1rem;">📍 Cantón / Cantones</th>
                        <th style="padding: 12px; color: #ffd700; font-weight: 800; font-size: 1rem;">⚔️ Territorio Robado</th>
                        <th style="padding: 12px; color: #ffd700; font-weight: 800; font-size: 1rem;">🚩 Tipo de Ruta</th>
                        <th style="padding: 12px; color: #ffd700; font-weight: 800; font-size: 1rem;">📁 Archivo GPX</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(tabla_html, unsafe_allow_html=True)
    else:
        st.info("El Libro de Guerra está limpio. El docente debe cargar los primeros archivos GPX.")
