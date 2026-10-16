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
    page_title="La Conquista de los Cantones - OHI La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS personalizado para emular la estética de "Run An Empire"
RUN_AN_EMPIRE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800;900&family=Oswald:wght@500;700&family=Rajdhani:wght@600;700&display=swap');

/* Fondo oscuro general tipo juego de estrategia */
.stApp {
    background-color: #0B0E14;
    color: #E2E8F0;
    font-family: 'Rajdhani', sans-serif;
}

/* Encabezado principal tipo Bánner Imperial */
.empire-header {
    background: linear-gradient(135deg, #1F190A 0%, #3D2D0C 50%, #171105 100%);
    border: 2px solid #D4AF37;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(212, 175, 55, 0.25), inset 0 0 15px rgba(212, 175, 55, 0.1);
}

.empire-title {
    font-family: 'Cinzel', serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: #FFD700;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-shadow: 0 0 12px rgba(255, 215, 0, 0.6), 2px 2px 4px #000000;
    margin: 0;
}

.empire-subtitle {
    font-family: 'Oswald', sans-serif;
    font-size: 1.1rem;
    color: #E5C158;
    letter-spacing: 1.5px;
    margin-top: 8px;
    text-transform: uppercase;
}

/* Tarjetas y Métricas estilo Panel de Control Estratégico */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, #18202C 0%, #0F151F 100%);
    border: 1px solid #D4AF37;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6);
}

div[data-testid="stMetricLabel"] {
    color: #FFD700 !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 1rem !important;
    text-transform: uppercase;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 700 !important;
}

/* Botones con estilo dorado de Acción */
.stButton>button {
    background: linear-gradient(180deg, #D4AF37 0%, #AA820A 100%) !important;
    color: #000000 !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border: 1px solid #FFE57F !important;
    border-radius: 6px !important;
    padding: 8px 16px !important;
    box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3) !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton>button:hover {
    background: linear-gradient(180deg, #FFE57F 0%, #D4AF37 100%) !important;
    box-shadow: 0 0 15px rgba(255, 215, 0, 0.7) !important;
    transform: translateY(-2px);
}

/* Pestañas estilizadas */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #121721;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid #2A3548;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Oswald', sans-serif !important;
    font-size: 1rem !important;
    text-transform: uppercase;
    color: #A0AEC0 !important;
    border-radius: 6px;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #2A3548 !important;
    color: #FFD700 !important;
    border: 1px solid #D4AF37 !important;
    font-weight: bold;
}

/* Estilo para las tablas */
.dataframe {
    background-color: #121721 !important;
    color: #F7FAFC !important;
    border: 1px solid #2A3548 !important;
}

/* Ajustes de la barra lateral */
section[data-testid="stSidebar"] {
    background-color: #0E131D !important;
    border-right: 1px solid #2A3548;
}
</style>
"""

st.markdown(RUN_AN_EMPIRE_CSS, unsafe_allow_html=True)

# Bánner Superior Principal
st.markdown("""
<div class="empire-header">
    <div class="empire-title">⚔️ LA CONQUISTA DE LOS CANTONES ⚔️</div>
    <div class="empire-subtitle">Estrategia Territorial Benahoarita • Isla de La Palma</div>
</div>
""", unsafe_allow_html=True)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"  # Contraseña para el modo profesor

# -----------------------------------------------------------------------------
# 2. CARGA DE CANTONES CON GEOJSON
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
# 3. PROCESAMIENTO GPX Y PERSISTENCIA DE DATOS
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
        st.error(f"Error cargando persistencia: {e}")
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

# -----------------------------------------------------------------------------
# 4. PALETA DE COLORES ÉPICA / NEÓN TIPO "RUN AN EMPIRE"
# -----------------------------------------------------------------------------
if 'actividades' not in st.session_state:
    st.session_state.actividades = cargar_actividades_persistentes()

# Colores de alta visibilidad tipo videojuegos sobre mapa oscuro
COLORES_IMPERIALES = [
    "#FF0055", "#00F0FF", "#39FF14", "#FFB703", "#9D4EDD",
    "#FF6B00", "#00E5FF", "#F72585", "#70E000", "#FF4800"
]

# -----------------------------------------------------------------------------
# 5. BARRA LATERAL CON MODO DOCENTE PROTEGIDO
# -----------------------------------------------------------------------------
st.sidebar.markdown("<h2 style='color:#FFD700; font-family:Cinzel;'>🛡️ CENTRO DE MANDO</h2>", unsafe_allow_html=True)

pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password", help="Acceso de administración")

es_docente = (pwd_input == PASSWORD_DOCENTE)

if es_docente:
    st.sidebar.success("🔓 MODO PROFESOR ACTIVO")
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color:#FFD700; font-family:Oswald;'>📤 REGISTRAR NUEVA INCURSIÓN GPX</h3>", unsafe_allow_html=True)
    
    nombre_alumno = st.sidebar.text_input("Nombre del Guerrero/a (Alumno/a)", value="Guerrero 1")
    fecha_ruta = st.sidebar.date_input("Fecha de la Incursión", value=datetime.now())
    hora_ruta = st.sidebar.time_input("Hora de Inicio", value=datetime.now().time())
    archivo_gpx = st.sidebar.file_uploader("Cargar pergamino .GPX", type=["gpx"])
    
    if st.sidebar.button("⚔️ CONQUISTAR TERRITORIO"):
        if archivo_gpx is not None and nombre_alumno.strip():
            fecha_completa = datetime.combine(fecha_ruta, hora_ruta)
            puntos = extraer_puntos_gpx(archivo_gpx)
            geom, tipo = procesar_puntos_gpx(puntos)
            
            if geom is not None:
                st.session_state.actividades.append({
                    'alumno': nombre_alumno.strip(),
                    'fecha': fecha_completa,
                    'geometria_utm': geom,
                    'tipo': tipo,
                    'archivo': archivo_gpx.name,
                    'puntos': puntos
                })
                st.session_state.actividades.sort(key=lambda x: x['fecha'])
                guardar_actividades_persistentes(st.session_state.actividades)
                st.sidebar.success(f"¡Territorio de {nombre_alumno} anexado al Imperio!")
                st.rerun()
            else:
                st.sidebar.error("El archivo GPX no contiene datos válidos.")
        else:
            st.sidebar.warning("Indica el nombre y adjunta el archivo GPX.")
            
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h4 style='color:#E53E3E;'>⚠️ ZONA DE REINICIO</h4>", unsafe_allow_html=True)
    if st.sidebar.button("💥 REINICIAR TODA LA COMPETICIÓN"):
        st.session_state.actividades = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.sidebar.success("¡El mapa ha sido reseteado por completo!")
        st.rerun()
else:
    st.sidebar.info("👁️ **MODO ESTUDIANTE (Solo Lectura)**\n\nNavega por el mapa, consulta el estado de tus reinos y revisa quién domina cada cantón.")

# -----------------------------------------------------------------------------
# 6. CÁLCULO DE SOLAPAMIENTO Y RE-CONQUISTA
# -----------------------------------------------------------------------------
def calcular_dominios_actuales():
    dominios = {}
    for act in st.session_state.actividades:
        alumno = act['alumno']
        nueva_geom = act['geometria_utm']
        
        for al in list(dominios.keys()):
            if dominios[al] is not None and not dominios[al].is_empty:
                dominios[al] = dominios[al].difference(nueva_geom)
                
        if alumno not in dominios or dominios[alumno] is None or dominios[alumno].is_empty:
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
            if geom_alumno is not None and not geom_alumno.is_empty:
                interseccion = geom_alumno.intersection(geom_canton)
                area_m2 = interseccion.area
            else:
                area_m2 = 0.0
                
            if area_m2 > 0:
                pct = (area_m2 / area_total_canton) * 100
                filas.append({
                    "Cantón": nombre_canton,
                    "Guerrero/a": alumno,
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm = calcular_dominios_actuales()
cantones_gdf = cargar_cantones_la_palma()
alumnos_unicos = list(set([act['alumno'] for act in st.session_state.actividades]))
mapa_colores = {al: COLORES_IMPERIALES[i % len(COLORES_IMPERIALES)] for i, al in enumerate(alumnos_unicos)}

# -----------------------------------------------------------------------------
# 7. INTERFAZ PRINCIPAL CON TEMA DE JUEGO
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "👑 MENCEYES DE CANTÓN",
    "📜 LIBRO DE GUERRA"
])

with tab1:
    st.markdown("<h3 style='color:#FFD700; font-family:Oswald;'>🗺️ ESTADO DEL TERRITORIO BENAHOARITA</h3>", unsafe_allow_html=True)
    
    # Mapa base con estilo oscuro "CartoDB dark_matter" tipo Run An Empire
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=11,
        tiles="CartoDB dark_matter",
        attr="CartoDB Dark Matter"
    )
    
    # Capa de Cantones Históricos
    for _, row in cantones_gdf.iterrows():
        folium.GeoJson(
            sg.mapping(row['geometry']),
            style_function=lambda x: {
                'fillColor': '#2A3548',
                'color': '#FFD700',
                'weight': 1.2,
                'fillOpacity': 0.15,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ CANTÓN:</b> {row['canton']}<br><b>📍 ZONA:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Dominios de Alumnos
    for alumno, geom in dominios_utm.items():
        if geom is not None and not geom.is_empty:
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            color = mapa_colores.get(alumno, "#FF0055")
            
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=color: {
                    'fillColor': col,
                    'color': '#FFFFFF',
                    'weight': 2,
                    'fillOpacity': 0.75
                },
                tooltip=f"<b>👑 CONQUISTADOR:</b> {alumno}<br><b>🏰 TERRITORIO:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.markdown("<h3 style='color:#FFD700; font-family:Oswald;'>🏆 SALÓN DE LA FAMA IMPERIAL</h3>", unsafe_allow_html=True)
    
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not geom.is_empty) else 0.0
        ranking_data.append({
            "Guerrero/a": alumno,
            "Dominio (km²)": round(area_m2 / 1_000_000.0, 4),
            "Hectáreas (ha)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = [f"Puesto {i+1}" for i in range(len(df_ranking))]
        st.dataframe(df_ranking[["Guerrero/a", "Dominio (km²)", "Hectáreas (ha)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han registrado incursiones en la isla. El docente debe subir los primeros archivos GPX.")

with tab3:
    st.markdown("<h3 style='color:#FFD700; font-family:Oswald;'>👑 TRONO DE LOS 12 CANTONES</h3>", unsafe_allow_html=True)
    
    df_cantones = calcular_ranking_detallado_por_canton(dominios_utm, cantones_gdf)
    
    if not df_cantones.empty:
        cantones_conquistados = df_cantones["Cantón"].unique()
        
        cols = st.columns(3)
        for i, cant in enumerate(cantones_conquistados):
            df_sub = df_cantones[df_cantones["Cantón"] == cant].sort_values(by="Superficie (m²)", ascending=False)
            lider = df_sub.iloc[0]
            
            with cols[i % 3]:
                st.metric(
                    label=f"🏛️ CANTÓN {cant.upper()}",
                    value=f"👑 {lider['Guerrero/a']}",
                    delta=f"{lider['Hectáreas (ha)']} ha ({lider['% del Cantón']}% controlado)"
                )
                
        st.markdown("---")
        canton_sel = st.selectbox("🔎 Explorar Cantón:", cantones_conquistados)
        df_canton_especifico = df_cantones[df_cantones["Cantón"] == canton_sel].sort_values(by="Superficie (m²)", ascending=False)
        df_canton_especifico.index = range(1, len(df_canton_especifico) + 1)
        
        st.dataframe(
            df_canton_especifico[["Guerrero/a", "Hectáreas (ha)", "% del Cantón", "Superficie (m²)"]],
            use_container_width=True
        )
    else:
        st.info("Sin conquistas registradas en los cantones.")

with tab4:
    st.markdown("<h3 style='color:#FFD700; font-family:Oswald;'>📜 REGISTRO CRONOLÓGICO DE INCURSIONES</h3>", unsafe_allow_html=True)
    
    if st.session_state.actividades:
        historial = [{
            "Fecha/Hora": act['fecha'].strftime("%Y-%m-%d %H:%M"),
            "Guerrero/a": act['alumno'],
            "Tipo de Incursión": act['tipo'],
            "Pergamino GPX": act['archivo']
        } for act in st.session_state.actividades]
        st.table(pd.DataFrame(historial))
    else:
        st.info("El libro de guerra está vacío.")
