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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Global de Alto Contraste
st.markdown("""
<style>
    /* Fondo principal y textos generales */
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
        color: #c9d1d9;
        font-size: 1rem;
        margin-top: 5px;
    }

    /* Pestañas (Tabs) en Blanco sobre Oscuro */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #161b22;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #21262d;
        color: #ffffff !important;
        border-radius: 6px;
        font-weight: bold;
        font-size: 1rem;
        padding: 8px 16px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] div p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        border: 1px solid #ffd700 !important;
    }
    .stTabs [aria-selected="true"] div p {
        color: #0d1117 !important;
        font-weight: 800 !important;
    }
    
    /* Tarjetas de Métricas */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 5px solid #ffd700;
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

    /* Barra lateral y Controles de Formulario */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 2px solid #ffd700;
    }
    section[data-testid="stSidebar"] label p {
        color: #ffd700 !important;
        font-weight: bold !important;
        font-size: 0.95rem !important;
    }
    
    /* Inputs con letras NEGRAS sobre fondo blanco para legibilidad impecable */
    div[data-baseweb="input"] input, div[data-baseweb="select"] div {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 6px !important;
    }
    input[type="text"], input[type="password"], input[type="number"], .stDateInput input, .stTimeInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        font-weight: 800 !important;
        border: 2px solid #ffd700 !important;
    }
    
    /* Botones de la Barra Lateral */
    .stButton>button {
        background-color: #21262d;
        color: #ffd700 !important;
        font-weight: bold;
        border: 2px solid #ffd700;
        border-radius: 8px;
        padding: 10px 20px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ffd700;
        color: #0d1117 !important;
        font-weight: 800;
    }
    
    /* Cargador de archivos GPX */
    section[data-testid="stFileUploader"] {
        background-color: #21262d;
        border: 2px dashed #ffd700;
        border-radius: 8px;
        padding: 10px;
    }
    section[data-testid="stFileUploader"] label span, section[data-testid="stFileUploader"] small {
        color: #ffffff !important;
        font-weight: bold !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI - La Palma</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BANNER DE CUENTA ATRÁS DINÁMICA EN TIEMPO REAL
# -----------------------------------------------------------------------------
# Fecha Límite Oficial: 30 de Mayo de 2027 a las 23:59:59
FECHA_LIMITE_ISO = "2027-05-30T23:59:59"

components.html(f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .countdown-container {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid #ffd700;
        border-radius: 10px;
        padding: 12px 20px;
        text-align: center;
        font-family: 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        margin-bottom: 10px;
    }}
    .countdown-title {{
        color: #ffd700;
        font-size: 0.95rem;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .countdown-timer {{
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: 900;
        letter-spacing: 2px;
        text-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
    }}
</style>
</head>
<body>
<div class="countdown-container">
    <div class="countdown-title">⏰ TIEMPO RESTANTE PARA ENVIAR RUTA GPX (Cierre: 30 de Mayo de 2027 - 23:59)</div>
    <div class="countdown-timer" id="timer">Cargando cuenta atrás...</div>
</div>

<script>
    const targetDate = new Date("{FECHA_LIMITE_ISO}").getTime();

    function updateCountdown() {{
        const now = new Date().getTime();
        const distance = targetDate - now;

        if (distance < 0) {{
            document.getElementById("timer").innerHTML = "🛑 CAMPAÑA FINALIZADA";
            document.getElementById("timer").style.color = "#ff4d4d";
            return;
        }}

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById("timer").innerHTML = 
            "⏳ " + days + " Días | " + 
            (hours < 10 ? "0" : "") + hours + "h : " + 
            (minutes < 10 ? "0" : "") + minutes + "m : " + 
            (seconds < 10 ? "0" : "") + seconds + "s restantes";
    }}

    updateCountdown();
    setInterval(updateCountdown, 1000);
</script>
</body>
</html>
""", height=90)

DATA_FILE = "actividades.json"
PASSWORD_DOCENTE = "ohi2026"

# -----------------------------------------------------------------------------
# 3. BASE DE DATOS DE LOS 11 ESTUDIANTES (ESCUDOS Y COLORES ASIGNADOS)
# -----------------------------------------------------------------------------
ESTUDIANTES = {
    "Estrella": {"escudo": "⭐", "titulo": "Estrella de Cima", "color": "#FF0055"},
    "Yassine":  {"escudo": "🦅", "titulo": "Águila de Cumbre", "color": "#00E5FF"},
    "Fabián":   {"escudo": "⚔️", "titulo": "Lanzas Cruzadas", "color": "#00FF66"},
    "Claudia":  {"escudo": "👑", "titulo": "Corona de Mencey", "color": "#FFCC00"},
    "Matías":   {"escudo": "🌋", "titulo": "Volcán Tajogaite", "color": "#FF6600"},
    "Yeray":    {"escudo": "🛡️", "titulo": "Escudo Táctico", "color": "#AA00FF"},
    "Adrián":   {"escudo": "☀️", "titulo": "Sol de Roque", "color": "#76FF03"},
    "Yamila":   {"escudo": "🌙", "titulo": "Luna Aborigen", "color": "#00FFCC"},
    "Gabriel":  {"escudo": "⚡", "titulo": "Rayo de Cima", "color": "#D500F9"},
    "Juanmi":   {"escudo": "🔥", "titulo": "Fuego de Cumbre", "color": "#FF3333"},
    "Paula":    {"escudo": "💎", "titulo": "Diamante Guanche", "color": "#3388FF"}
}

# -----------------------------------------------------------------------------
# 4. CARGA DE CANTONES Y PROCESAMIENTO DE RUTAS GPX
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
        st.error(f"Error en persistencia: {e}")
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
# 5. BARRA LATERAL (MODO PROFESOR / ESTUDIANTE)
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DE CONTROL")
pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password", help="Ingresa 'ohi2026' para administrar.")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Docente Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Registrar Incursión GPX")
    
    lista_nombres = list(ESTUDIANTES.keys())
    nombre_alumno = st.sidebar.selectbox("Seleccionar Alumno/a", options=lista_nombres)
    
    info_est = ESTUDIANTES[nombre_alumno]
    st.sidebar.info(f"**Escudo:** {info_est['escudo']} {info_est['titulo']}")
    
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
                st.sidebar.success(f"¡Incursión de {info_est['escudo']} {nombre_alumno} registrada!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX no contiene un track válido.")
        else:
            st.sidebar.warning("Selecciona un archivo GPX.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Reiniciar Campaña (Borrar Todo)"):
        st.session_state.actividades = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.sidebar.success("¡Campaña reiniciada con éxito!")
        st.rerun()
else:
    st.sidebar.info("👁️ **Modo Estudiante (Solo Lectura)** - Consulta las clasificaciones y mapa de dominio en tiempo real.")

# -----------------------------------------------------------------------------
# 6. CÁLCULO DE DOMINIOS, CANTONES Y HISTORIAL DE ROBOS
# -----------------------------------------------------------------------------
cantones_gdf = cargar_cantones_la_palma()

def calcular_dominios_y_historial_guerra():
    dominios = {}
    historial_robos = []
    
    cantones_utm = cantones_gdf.to_crs("EPSG:32628")
    
    for act in st.session_state.actividades:
        alumno = act['alumno']
        geom_nueva = act['geometria_utm']
        info_actual = ESTUDIANTES.get(alumno, {"escudo": "🛡️", "color": "#3388FF"})
        
        # 1. Identificar cantones por los que pasa la ruta
        cantones_afectados = []
        for _, crow in cantones_utm.iterrows():
            if geom_nueva.intersects(crow['geometry']):
                cantones_afectados.append(crow['canton'])
        cantones_str = ", ".join(cantones_afectados) if cantones_afectados else "La Palma"
        
        # 2. Calcular territorio arrebatado a otros compañeros
        desglose_robos = []
        total_robado_m2 = 0.0
        
        for victim, victim_geom in dominios.items():
            if victim != alumno and victim_geom is not None and not getattr(victim_geom, 'is_empty', True):
                overlap = geom_nueva.intersection(victim_geom)
                if not getattr(overlap, 'is_empty', True) and overlap.area > 5.0:
                    area_ha = overlap.area / 10000.0
                    total_robado_m2 += overlap.area
                    v_info = ESTUDIANTES.get(victim, {"escudo": "🛡️"})
                    desglose_robos.append(f"{area_ha:.2f} ha a {v_info['escudo']} {victim}")
                    
        if total_robado_m2 > 5.0:
            robos_txt = f"⚔️ <b>{(total_robado_m2/10000.0):.2f} ha</b> (" + ", ".join(desglose_robos) + ")"
        else:
            robos_txt = "🕊️ 0.00 ha (Sin robos)"
            
        historial_robos.append({
            "fecha": act['fecha'].strftime("%Y-%m-%d %H:%M"),
            "alumno": f"{info_actual['escudo']} {alumno}",
            "cantones": f"📍 {cantones_str}",
            "robos": robos_txt,
            "tipo": act['tipo'],
            "archivo": act['archivo']
        })
        
        # 3. Restar territorio a las víctimas e integrar al conquistador
        for victim in list(dominios.keys()):
            if dominios[victim] is not None and not getattr(dominios[victim], 'is_empty', True):
                dominios[victim] = dominios[victim].difference(geom_nueva)
                
        if alumno not in dominios or dominios[alumno] is None or getattr(dominios[alumno], 'is_empty', True):
            dominios[alumno] = geom_nueva
        else:
            dominios[alumno] = dominios[alumno].union(geom_nueva)
            
    return dominios, historial_robos

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
                info_a = ESTUDIANTES.get(alumno, {"escudo": "🛡️"})
                filas.append({
                    "Cantón": nombre_canton,
                    "Alumno/a": f"{info_a['escudo']} {alumno}",
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm, historial_guerra = calcular_dominios_y_historial_guerra()

# -----------------------------------------------------------------------------
# 7. INTERFAZ Y PESTAÑAS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ MAPA DE DOMINIO",
    "🏆 CLASIFICACIÓN GENERAL",
    "👑 MENCEYES POR CANTÓN",
    "📜 LIBRO DE GUERRA"
])

with tab1:
    st.write("### 📍 Mapa Interactivo de La Palma")
    
    m = folium.Map(
        location=[28.65, -17.86],
        zoom_start=10,
        min_zoom=10,
        max_zoom=18,
        max_bounds=True,
        tiles="OpenStreetMap"
    )
    m.fit_bounds([[28.40, -18.05], [28.90, -17.65]])
    
    # Capa de Cantones
    for _, row in cantones_gdf.iterrows():
        folium.GeoJson(
            sg.mapping(row['geometry']),
            style_function=lambda x: {
                'fillColor': '#f4a261',
                'color': '#d97706',
                'weight': 1.8,
                'fillOpacity': 0.15,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Municipio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Dominios de Estudiantes
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            info_al = ESTUDIANTES.get(alumno, {"escudo": "🛡️", "color": "#3388FF"})
            color = info_al['color']
            escudo = info_al['escudo']
            
            # Dibujar Polígono del Territorio
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, col=color: {
                    'fillColor': col,
                    'color': col,
                    'weight': 2.5,
                    'fillOpacity': 0.65
                },
                tooltip=f"<b>{escudo} Dominio de {alumno}:</b><br><b>Superficie:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Dibujar Insignia Flotante con el Escudo en el centroide
            centroide = geom_wgs.centroid
            icon_html = f"""
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
            ">{escudo}</div>
            """
            folium.Marker(
                location=[centroide.y, centroide.x],
                icon=folium.DivIcon(html=icon_html, icon_size=(32, 32), icon_anchor=(16, 16)),
                popup=f"<b>{escudo} {alumno}</b><br>{round(area_m2/10000, 2)} ha conquistadas"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Clasificación General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        info_a = ESTUDIANTES.get(alumno, {"escudo": "🛡️"})
        ranking_data.append({
            "Guerrero/a": f"{info_a['escudo']} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Guerrero/a", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han librado batallas. El docente debe registrar los primeros archivos GPX.")

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

with tab4:
    st.write("### 📜 Libro de Guerra y Registro de Incursiones")
    
    if historial_guerra:
        # Generar código HTML libre de sangrado para evitar que Streamlit renderice código Markdown
        rows_html = ""
        for h in historial_guerra:
            rows_html += f"""
            <tr>
                <td><b>{h['fecha']}</b></td>
                <td><b>{h['alumno']}</b></td>
                <td>{h['cantones']}</td>
                <td>{h['robos']}</td>
                <td>{h['tipo']}</td>
                <td><code style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px;">{h['archivo']}</code></td>
            </tr>
            """
            
        table_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background-color: transparent; margin: 0; padding: 5px; }}
            .war-table {{ width: 100%; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid #ffd700; }}
            .war-table th {{ background-color: #161b22; color: #ffd700; padding: 12px 15px; text-align: left; font-size: 0.95rem; border-bottom: 2px solid #ffd700; }}
            .war-table td {{ padding: 12px 15px; border-bottom: 1px solid #cbd5e1; color: #111111; font-size: 0.9rem; font-weight: 600; }}
            .war-table tr:nth-child(even) {{ background-color: #f8fafc; }}
            .war-table tr:hover {{ background-color: #f1f5f9; }}
        </style>
        </head>
        <body>
        <table class="war-table">
            <thead>
                <tr>
                    <th>📅 Fecha/Hora</th>
                    <th>👑 Conquistador/a</th>
                    <th>📍 Cantón / Cantones</th>
                    <th>⚔️ Territorio Robado</th>
                    <th>🚩 Tipo de Ruta</th>
                    <th>📁 Archivo GPX</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        </body>
        </html>
        """
        
        # 1. Renderizado seguro vía componentes iframe
        components.html(table_html, height=450, scrolling=True)
        
        st.markdown("---")
        st.write("#### 📊 Vista en Tabla Datos Interactiva")
        df_historial = pd.DataFrame([{
            "📅 Fecha/Hora": h['fecha'],
            "👑 Conquistador/a": h['alumno'],
            "📍 Cantón / Cantones": h['cantones'],
            "⚔️ Territorio Robado": h['robos'].replace('<b>', '').replace('</b>', ''),
            "🚩 Tipo de Ruta": h['tipo'],
            "📁 Archivo GPX": h['archivo']
        } for h in historial_guerra])
        st.dataframe(df_historial, use_container_width=True, hide_index=True)
        
    else:
        st.info("El historial de guerra está limpio. No hay incursiones registradas aún.")
