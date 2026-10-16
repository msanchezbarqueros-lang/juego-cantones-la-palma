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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO OSCURO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Oscuro de Alto Contraste
st.markdown("""
<style>
    /* Fondo principal y textos */
    .stApp {
        background-color: #0d1117;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Encabezado */
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
        color: #c9d1d9;
        font-size: 1rem;
        margin-top: 5px;
    }

    /* Tarjetas de Métricas */
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
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d;
        color: #ffffff !important;
        border-radius: 6px;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
    }
    
    /* Barra lateral y Controles */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Etiquetas y Contraste de Inputs */
    label, .stMarkdown, p, span, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    .stTextInput input, .stDateInput input, .stTimeInput input, .stSelectbox div {
        color: #ffffff !important;
        background-color: #0d1117 !important;
        border: 1px solid #ffd700 !important;
        font-weight: bold !important;
    }
    
    div[data-testid="stFileUploader"] {
        border: 2px dashed #ffd700 !important;
        border-radius: 10px;
        padding: 15px;
        background-color: #0d1117 !important;
    }
    div[data-testid="stFileUploader"] * {
        color: #ffffff !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI - La Palma</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. TEMPORIZADOR DINÁMICO EN TIEMPO REAL (HASTA EL 30 DE MAYO 23:59)
# -----------------------------------------------------------------------------
components.html("""
<div style="
    background-color: #161b22;
    border: 2px solid #ffd700;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    box-shadow: 0 4px 10px rgba(0,0,0,0.5);
">
    <div style="color: #ffd700; font-weight: bold; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px;">
        ⏰ TIEMPO RESTANTE PARA ENVIAR RUTA GPX (Cierre: 30 de Mayo - 23:59)
    </div>
    <div id="countdown" style="color: #ffffff; font-size: 1.8rem; font-weight: 800; margin-top: 5px; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);">
        Cargando cuenta atrás...
    </div>
</div>

<script>
    const targetDate = new Date("2026-05-30T23:59:59").getTime();
    
    function updateCountdown() {
        const now = new Date().getTime();
        const difference = targetDate - now;
        
        if (difference < 0) {
            document.getElementById("countdown").innerHTML = "🛑 CAMPAÑA FINALIZADA";
            return;
        }
        
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);
        
        document.getElementById("countdown").innerHTML = 
            "⏳ " + days + "d : " + 
            (hours < 10 ? "0" : "") + hours + "h : " + 
            (minutes < 10 ? "0" : "") + minutes + "m : " + 
            (seconds < 10 ? "0" : "") + seconds + "s";
    }
    
    updateCountdown();
    setInterval(updateCountdown, 1000);
</script>
""", height=110)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# 3. BASE DE DATOS DE LOS 11 ALUMNOS CON SUS ESCUDOS Y COLORES NEÓN
# -----------------------------------------------------------------------------
ESTUDIANTES = {
    "Estrella": {"escudo": "⭐", "color": "#FF0055", "titulo": "Estrella de Cima"},
    "Yassine":  {"escudo": "🦅", "color": "#00E5FF", "titulo": "Águila de Cumbre"},
    "Fabián":   {"escudo": "⚔️", "color": "#00FF66", "titulo": "Lanzas Cruzadas"},
    "Claudia":  {"escudo": "👑", "color": "#FFCC00", "titulo": "Corona de Mencey"},
    "Matías":   {"escudo": "🌋", "color": "#FF6600", "titulo": "Volcán Tajogaite"},
    "Yeray":    {"escudo": "🛡️", "color": "#AA00FF", "titulo": "Escudo Táctico"},
    "Adrián":   {"escudo": "☀️", "color": "#76FF03", "titulo": "Sol de Roque"},
    "Yamila":   {"escudo": "🌙", "color": "#00FFCC", "titulo": "Luna Aborigen"},
    "Gabriel":  {"escudo": "⚡", "color": "#D500F9", "titulo": "Rayo de Cima"},
    "Juanmi":   {"escudo": "🔥", "color": "#FF3333", "titulo": "Fuego de Cumbre"},
    "Paula":    {"escudo": "💎", "color": "#3388FF", "titulo": "Diamante Guanche"}
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

if 'actividades' not in st.session_state:
    st.session_state.actividades = cargar_actividades_persistentes()

# -----------------------------------------------------------------------------
# 6. BARRA LATERAL CON CONTROL DE ACCESO
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DE CONTROL")

pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password", help="Acceso restringido para el profesorado.")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Docente Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Registrar Ruta GPX")
    
    lista_nombres = list(ESTUDIANTES.keys())
    nombre_alumno = st.sidebar.selectbox("Seleccionar Alumno/a:", lista_nombres)
    
    info_est = ESTUDIANTES[nombre_alumno]
    st.sidebar.info(f"Escudo: {info_est['escudo']} {info_est['titulo']} | Color: {info_est['color']}")
    
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
                    'alumno': nombre_alumno,
                    'fecha': fecha_completa,
                    'geometria_utm': geom,
                    'tipo': tipo,
                    'archivo': archivo_gpx.name,
                    'puntos': puntos
                })
                st.session_state.actividades.sort(key=lambda x: x['fecha'])
                guardar_actividades_persistentes(st.session_state.actividades)
                st.sidebar.success(f"¡Territorio de {nombre_alumno} registrado!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX sin datos válidos.")
        else:
            st.sidebar.warning("Selecciona un archivo GPX.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Reiniciar Campaña (Borrar Todo)"):
        st.session_state.actividades = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.sidebar.success("¡Campaña reiniciada!")
        st.rerun()

else:
    st.sidebar.info("👁️ Modo Estudiante (Solo Lectura)")

# -----------------------------------------------------------------------------
# 7. CÁLCULO DE SOLAPAMIENTOS Y COBERTURA POR CANTÓN
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
# 8. INTERFAZ WEB PRINCIPAL
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "MAPA DE DOMINIO",
    "CLASIFICACIÓN GENERAL",
    "MENCEYES POR CANTÓN",
    "LIBRO DE GUERRA"
])

with tab1:
    st.write("### 📍 Mapa Táctico de La Palma")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=10,
        min_zoom=10,
        tiles="OpenStreetMap",
        max_bounds=True
    )
    m.fit_bounds([[28.4, -18.05], [28.9, -17.65]])
    
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
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Territorio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Dominios de los Estudiantes con sus Escudos y Colores
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            perf = ESTUDIANTES.get(alumno, {"color": "#00E5FF", "escudo": "🛡️"})
            col = perf["color"]
            escudo = perf["escudo"]
            
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, color=col: {
                    'fillColor': color,
                    'color': color,
                    'weight': 3,
                    'fillOpacity': 0.6
                },
                tooltip=f"<b>{escudo} Conquistador/a:</b> {alumno}<br><b>Dominio:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Marcador de Escudo en el Centroide del Dominio
            centroid = geom_wgs.centroid
            icon_html = f'<div style="font-size:24px; text-shadow: 0 0 5px #000; text-align:center;">{escudo}</div>'
            folium.Marker(
                location=[centroid.y, centroid.x],
                icon=folium.DivIcon(html=icon_html),
                tooltip=f"<b>{escudo} {alumno}</b>"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
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
        st.info("Aún no se han librado batallas por el territorio. El docente debe registrar las primeras rutas GPX.")

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
        df_canton_especifico['Alumno/a'] = df_canton_especifico['Alumno/a'].apply(lambda x: f"{ESTUDIANTES.get(x, {}).get('escudo', '🛡️')} {x}")
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
        historial = [{
            "Fecha/Hora": act['fecha'].strftime("%Y-%m-%d %H:%M"),
            "Conquistador/a": f"{ESTUDIANTES.get(act['alumno'], {}).get('escudo', '🛡️')} {act['alumno']}",
            "Tipo de Incursión": act['tipo'],
            "Archivo GPX": act['archivo']
        } for act in st.session_state.actividades]
        st.table(pd.DataFrame(historial))
    else:
        st.info("El historial está limpio.")
