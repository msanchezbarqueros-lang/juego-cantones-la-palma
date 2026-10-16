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
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO OSCURO "RUN AN EMPIRE"
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="La Conquista de los Cantones - La Palma",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Oscuro Estilo Videojuego de Estrategia con alto contraste
st.markdown("""
<style>
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
        margin-bottom: 15px;
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
        color: #ffffff;
        font-size: 1rem;
        margin-top: 5px;
        font-weight: 600;
    }

    /* Banner de Cuenta Atrás */
    .countdown-box {
        background: #161b22;
        border: 1px solid #ffd700;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .countdown-title {
        color: #ffd700;
        font-size: 0.95rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .countdown-time {
        color: #00ffcc;
        font-size: 1.3rem;
        font-weight: 800;
        letter-spacing: 1px;
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
        font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffd700 !important;
        color: #0d1117 !important;
    }

    /* Tarjetas Métricas */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-left: 4px solid #ffd700;
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
    
    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
</style>

<div class="header-box">
    <div class="header-title">🌋 LA CONQUISTA DE LOS CANTONES</div>
    <div class="header-subtitle">Estrategia Territorial Benahoarita | Módulo OHI - La Palma</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# RELOJ CUENTA ATRÁS (LÍMITE: 30 DE MAYO A LAS 23:59)
# -----------------------------------------------------------------------------
FECHA_LIMITE = datetime(2027, 5, 30, 23, 59, 59)
ahora = datetime.now()
diferencia = FECHA_LIMITE - ahora

if diferencia.total_seconds() > 0:
    dias = diferencia.days
    horas, rem = divmod(diferencia.seconds, 3600)
    minutos, segundos = divmod(rem, 60)
    texto_cuenta_atras = f"⏳ {dias} días | {horas:02d}h {minutos:02d}m {segundos:02d}s restantes"
else:
    texto_cuenta_atras = "🛑 CAMPAÑA FINALIZADA (Fecha límite alcanzada)"

st.markdown(f"""
<div class="countdown-box">
    <div class="countdown-title">⏰ TIEMPO RESTANTE PARA REGISTRAR RUTAS GPX (Cierre: 30 de Mayo - 23:59)</div>
    <div class="countdown-time">{texto_cuenta_atras}</div>
</div>
""", unsafe_allow_html=True)

DATA_FILE = "actividades.json"
PERFILES_FILE = "perfiles.json"
PASSWORD_DOCENTE = "ohi2026"

OPCIONES_ESCUDOS = {
    "🦅 Águila de Cumbre": "🦅",
    "🛡️ Escudo de Guerra": "🛡️",
    "🌋 Volcán Tajogaite": "🌋",
    "⚔️ Lanzas Cruzadas": "⚔️",
    "🐆 Leopardo Benahoarita": "🐆",
    "☀️ Sol de Roque": "☀️",
    "👑 Corona de Mencey": "👑",
    "🐺 Lobo de la Caldera": "🐺",
    "🔱 Tridente del Mar": "🔱",
    "🏹 Arco Cazador": "🏹"
}

OPCIONES_COLORES = {
    "Rosa Neón": "#FF0055",
    "Cian Eléctrico": "#00E5FF",
    "Verde Neón": "#00FF66",
    "Oro Benahoarita": "#FFCC00",
    "Morado Imperial": "#AA00FF",
    "Naranja Fuego": "#FF6600",
    "Turquesa": "#00FFCC",
    "Magenta": "#FF00AA",
    "Verde Lima": "#76FF03",
    "Violeta": "#D500F9"
}

# -----------------------------------------------------------------------------
# 2. DEFINICIÓN Y CARGA DE CANTONES
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
# 3. PROCESAMIENTO Y PERSISTENCIA
# -----------------------------------------------------------------------------
def procesar_puntos_gpx(puntos, max_dist_cierre_m=100.0, franja_m=30.0):
    if len(puntos) < 3:
        return None, "Error: GPX insuficiente"
        
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

def cargar_perfiles_persistentes():
    if not os.path.exists(PERFILES_FILE):
        return {}
    try:
        with open(PERFILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def guardar_perfiles_persistentes(perfiles):
    with open(PERFILES_FILE, "w", encoding="utf-8") as f:
        json.dump(perfiles, f, ensure_ascii=False, indent=2)

# -----------------------------------------------------------------------------
# 4. ESTADO DE LA SESIÓN Y CONFIGURACIÓN DE PERFILES
# -----------------------------------------------------------------------------
if 'actividades' not in st.session_state:
    st.session_state.actividades = cargar_actividades_persistentes()

if 'perfiles' not in st.session_state:
    st.session_state.perfiles = cargar_perfiles_persistentes()

# -----------------------------------------------------------------------------
# 5. BARRA LATERAL DOCENTE
# -----------------------------------------------------------------------------
st.sidebar.title("⚔️ PANEL DE CONTROL")
pwd_input = st.sidebar.text_input("🔑 Contraseña Docente", type="password")

if pwd_input == PASSWORD_DOCENTE:
    st.sidebar.success("🔓 Modo Docente Activo")
    st.sidebar.markdown("---")
    st.sidebar.subheader("📤 Cargar Ruta y Personalizar Alumno")
    
    nombre_alumno = st.sidebar.text_input("Nombre del Alumno/a", value="Alumno 1")
    
    col1_side, col2_side = st.sidebar.columns(2)
    with col1_side:
        nombre_escudo_sel = st.selectbox("🛡️ Escudo / Blasón", list(OPCIONES_ESCUDOS.keys()))
        escudo_sel = OPCIONES_ESCUDOS[nombre_escudo_sel]
    with col2_side:
        nombre_color_sel = st.selectbox("🎨 Color de Guerra", list(OPCIONES_COLORES.keys()))
        color_sel = OPCIONES_COLORES[nombre_color_sel]

    fecha_ruta = st.sidebar.date_input("Fecha de la Ruta", value=datetime.now())
    hora_ruta = st.sidebar.time_input("Hora de la Ruta", value=datetime.now().time())
    archivo_gpx = st.sidebar.file_uploader("Subir archivo .gpx", type=["gpx"])
    
    if st.sidebar.button("⚡ CONQUISTAR TERRITORIO"):
        if archivo_gpx is not None and nombre_alumno.strip():
            alumno_clean = nombre_alumno.strip()
            fecha_completa = datetime.combine(fecha_ruta, hora_ruta)
            puntos = extraer_puntos_gpx(archivo_gpx)
            geom, tipo = procesar_puntos_gpx(puntos)
            
            if geom is not None:
                # Actualizar perfil del alumno
                st.session_state.perfiles[alumno_clean] = {
                    "escudo": escudo_sel,
                    "color": color_sel
                }
                guardar_perfiles_persistentes(st.session_state.perfiles)
                
                # Registrar actividad
                st.session_state.actividades.append({
                    'alumno': alumno_clean,
                    'fecha': fecha_completa,
                    'geometria_utm': geom,
                    'tipo': tipo,
                    'archivo': archivo_gpx.name,
                    'puntos': puntos
                })
                st.session_state.actividades.sort(key=lambda x: x['fecha'])
                guardar_actividades_persistentes(st.session_state.actividades)
                
                st.sidebar.success(f"¡Ruta de {escudo_sel} {alumno_clean} registrada!")
                st.rerun()
            else:
                st.sidebar.error("Archivo GPX sin datos válidos.")
        else:
            st.sidebar.warning("Introduce nombre y selecciona archivo GPX.")
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Reiniciar Campaña"):
        st.session_state.actividades = []
        st.session_state.perfiles = {}
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        if os.path.exists(PERFILES_FILE):
            os.remove(PERFILES_FILE)
        st.sidebar.success("Campaña reiniciada.")
        st.rerun()
else:
    st.sidebar.info("👁️ **Modo Estudiante (Solo Lectura)**")

# Helper para obtener perfil
def get_perfil(alumno):
    if alumno in st.session_state.perfiles:
        return st.session_state.perfiles[alumno]
    else:
        # Fallback determinista
        alumnos_unicos = sorted(list(set([act['alumno'] for act in st.session_state.actividades])))
        idx = alumnos_unicos.index(alumno) if alumno in alumnos_unicos else 0
        lista_colores = list(OPCIONES_COLORES.values())
        lista_escudos = list(OPCIONES_ESCUDOS.values())
        return {
            "escudo": lista_escudos[idx % len(lista_escudos)],
            "color": lista_colores[idx % len(lista_colores)]
        }

# -----------------------------------------------------------------------------
# 6. CÁLCULO DE SOLAPAMIENTO Y COBERTURA
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
                perfil = get_perfil(alumno)
                filas.append({
                    "Cantón": nombre_canton,
                    "Alumno/a": f"{perfil['escudo']} {alumno}",
                    "Nombre_Raw": alumno,
                    "Superficie (m²)": round(area_m2, 2),
                    "Hectáreas (ha)": round(area_m2 / 10000.0, 2),
                    "% Conquistado del Cantón": round(pct, 2)
                })
                
    return pd.DataFrame(filas)

dominios_utm = calcular_dominios_actuales()
cantones_gdf = cargar_cantones_la_palma()

# -----------------------------------------------------------------------------
# 7. INTERFAZ WEB PRINCIPAL
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
                'fillColor': '#21262d',
                'color': '#e76f51',
                'weight': 1.5,
                'fillOpacity': 0.12,
                'dashArray': '4, 4'
            },
            tooltip=f"<b>🏛️ Cantón:</b> {row['canton']}<br><b>Territorio:</b> {row.get('municipio', 'N/A')}"
        ).add_to(m)
        
    # Capa de Dominios de Estudiantes con Escudo e Insignia
    for alumno, geom in dominios_utm.items():
        if geom is not None and not getattr(geom, 'is_empty', True):
            perfil = get_perfil(alumno)
            color_usr = perfil['color']
            escudo_usr = perfil['escudo']
            
            gdf_m = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:32628").to_crs("EPSG:4326")
            geom_wgs = gdf_m.geometry.iloc[0]
            area_m2 = geom.area
            
            # Polígono coloreado con el color personalizado del usuario
            folium.GeoJson(
                sg.mapping(geom_wgs),
                style_function=lambda x, c=color_usr: {
                    'fillColor': c,
                    'color': c,
                    'weight': 2.5,
                    'fillOpacity': 0.55
                },
                tooltip=f"<b>{escudo_usr} Conquistador/a:</b> {alumno}<br><b>Superficie:</b> {round(area_m2/10000, 2)} ha ({round(area_m2/1000000, 3)} km²)"
            ).add_to(m)
            
            # Marcador con Escudo / Insignia en el Centroide de la Zona Conquistada
            centroide = geom_wgs.centroid
            html_icon = f"""
            <div style="
                background-color: {color_usr};
                border: 2px solid #ffffff;
                border-radius: 50%;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 16px;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.6);
            ">
                {escudo_usr}
            </div>
            """
            folium.Marker(
                location=[centroide.y, centroide.x],
                icon=folium.DivIcon(html=html_icon),
                popup=f"<b>{escudo_usr} {alumno}</b><br>Dominio: {round(area_m2/10000, 2)} ha"
            ).add_to(m)
            
    components.html(m._repr_html_(), height=650)

with tab2:
    st.write("### 🏆 Ranking General de la Isla")
    ranking_data = []
    for alumno, geom in dominios_utm.items():
        area_m2 = geom.area if (geom is not None and not getattr(geom, 'is_empty', True)) else 0.0
        perfil = get_perfil(alumno)
        ranking_data.append({
            "Mencey": f"{perfil['escudo']} {alumno}",
            "Superficie (km²)": round(area_m2 / 1_000_000.0, 4),
            "Superficie (Hectáreas)": round(area_m2 / 10_000.0, 2),
            "Superficie (m²)": round(area_m2, 2)
        })
        
    if ranking_data:
        df_ranking = pd.DataFrame(ranking_data).sort_values(by="Superficie (m²)", ascending=False)
        df_ranking.index = range(1, len(df_ranking) + 1)
        st.dataframe(df_ranking[["Mencey", "Superficie (km²)", "Superficie (Hectáreas)", "Superficie (m²)"]], use_container_width=True)
    else:
        st.info("Aún no se han registrado rutas GPX.")

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
            perfil = get_perfil(act['alumno'])
            historial.append({
                "Fecha/Hora": act['fecha'].strftime("%Y-%m-%d %H:%M"),
                "Conquistador/a": f"{perfil['escudo']} {act['alumno']}",
                "Tipo de Incursión": act['tipo'],
                "Archivo GPX": act['archivo']
            })
        st.table(pd.DataFrame(historial))
    else:
        st.info("El historial está limpio.")
