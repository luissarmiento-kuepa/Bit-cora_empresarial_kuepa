import streamlit as st
import pandas as pd
from groq import Groq
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="MentorIA KP - Técnicos Laborales", page_icon="🎓", layout="wide")

# --- 2. ESTILOS VISUALES (BRANDING KUEPA) ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&family=Montserrat:wght@400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Barlow', sans-serif;
        color: #292929;
        background-color: #FAFAFA;
    }
    
    h1, h2, h3 {
        color: #FD531E !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
    }

    .stButton>button {
        background-color: #FD531E;
        color: #FAFAFA;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #149852; 
        color: #FAFAFA;
        border: none;
        transform: scale(1.02);
    }

    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
        font-family: 'Montserrat', sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        border-bottom-color: #FD531E;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
        color: #FD531E;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA (GROQ) ---
try:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave 'GROQ_API_KEY' en los Secrets de Streamlit.")
        st.stop()
    
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    MODELO_GROQ = "llama-3.3-70b-versatile" 
except Exception as e:
    st.error(f"⚠️ Error de configuración con Groq: {e}")
    st.stop()

# --- 4. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        # BITÁCORA - GOOGLE SHEETS
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        df_ent = pd.read_csv(URL, dtype=str)
        df_ent.columns = df_ent.columns.str.strip()
        
        target = next((c for c in df_ent.columns if "empresa" in c.lower() or "asociadas" in c.lower()), df_ent.columns[0])
        df_ent.rename(columns={target: 'Empresa'}, inplace=True)
        
        # Validar si existe la columna Sector, si no, crear una genérica
        sector_target = next((c for c in df_ent.columns if "sector" in c.lower()), None)
        if sector_target:
            df_ent.rename(columns={sector_target: 'Sector'}, inplace=True)
        else:
            df_ent['Sector'] = 'General'

        df_ent.fillna("No disponible", inplace=True)

        # PROGRAMAS - GITHUB
        try:
            df_p = pd.read_csv("programas.csv", dtype=str)
            df_p.columns = df_p.columns.str.strip()
            if 'Perfil_Del_Egresado' in df_p.columns:
                df_p.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
            df_p = pd.DataFrame({'Programa': ['General'], 'Perfil': ['Técnico Kuepa']})

        return df_ent, df_p
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None

df, df_prog = load_data()
if df is None: st.stop()

# --- Extraer Sectores Únicos o usar lista por defecto ---
sectores_disponibles = [s for s in df['Sector'].unique() if s != "No disponible"]
if not sectores_disponibles:
    sectores_disponibles = ["Tecnología", "Finanzas y Contabilidad", "Salud", "Comercio y Retail", "Servicios al Cliente", "Manufactura", "Logística"]

# --- 5. INTERFAZ PRINCIPAL ---
if os.path.exists("logo-Kuepa.png"):
    st.image("logo-Kuepa.png", width=250)

st.title("MentorIA KP - Técnicos Laborales KUEPA")
st.markdown("---")

t1, t2 = st.tabs(["👨‍🏫 DOCENTES", "🎓 ESTUDIANTES"])

# ==========================================
# PESTAÑA 1: DOCENTES
# ==========================================
with t1:
    st.header("🛠️ Diseñador de Retos Operativos (15-20 min)")
    st.info("💡 Genera actividades 100% aplicables. La IA creará escenarios creativos (casos, historias, datos) para que el estudiante resuelva de inmediato.")
    
    col1, col2 = st.columns(2)
    with col1:
        p_sel = st.selectbox("Programa Técnico:", sorted(df_prog['Programa'].unique()))
    
    with col2:
        tipo_filtro = st.radio("Enfocar el reto basado en:", ["Empresa Específica", "Sector de la Industria"])
        
        if tipo_filtro == "Empresa Específica":
            seleccion_entorno = st.selectbox("Selecciona la Empresa:", sorted(df['Empresa'].unique()), key="doc_e")
        else:
            seleccion_entorno = st.selectbox("Selecciona el Sector Industrial:", sorted(sectores_disponibles), key="doc_s")
    
    tema = st.text_input("Tema de la clase o competencia a desarrollar:", placeholder="Ej: Costos y balances, Servicio al cliente, Tablas dinámicas...")
    
    if st.button("🚀 Generar Actividad"):
        if tema:
            with st.spinner("Groq está diseñando un escenario único y creativo..."):
                try:
                    # Preparar el contexto
                    if tipo_filtro == "Empresa Específica":
                        row = df[df['Empresa'] == seleccion_entorno].iloc[0]
                        info_bruta = "\n".join([f"{k}: {v}" for k, v in row.items() if v != "No disponible"])
                        contexto_ia = f"Empresa Real ({seleccion_entorno}). Contexto de la bitácora: {info_bruta}"
                    else:
                        contexto_ia = f"Sector Industrial genérico: {seleccion_entorno}. Crea un escenario típico de este sector."

                    # PROMPT CON "MOTOR DE CREATIVIDAD" Y VARIABILIDAD
                    prompt = f"""
                    Actúa como un Lead Instructor de Kuepa. Diseña un reto práctico, inmersivo y realizable en 15-20 minutos sobre el tema '{tema}' para un estudiante de '{p_sel}'.
                    Contexto del negocio: {contexto_ia}

                    REGLA CRÍTICA DE ORO: El estudiante NO tiene acceso a internet ni a datos internos reales. DEBES CREAR Y ENTREGAR EL MATERIAL BASE para el reto.
                    
                    ¡SÉ MUY CREATIVO Y VARIADO! Para entregar el problema al estudiante, ELIGE ALEATORIAMENTE solo UNO de estos formatos (no uses siempre tablas):
                    - OPCIÓN A: Una historia o storytelling de un problema operativo que ocurrió hoy en la empresa.
                    - OPCIÓN B: La simulación de un correo electrónico, queja de cliente o mensaje de WhatsApp de un jefe pidiendo ayuda urgente.
                    - OPCIÓN C: La descripción en texto de una gráfica, dashboard o ilustración que el estudiante debe imaginar/interpretar.
                    - OPCIÓN D: Un caso de estudio real o inspirado en casos reales de esta industria.
                    - OPCIÓN E: Una pequeña tabla de datos crudos (máximo 5 filas).

                    Estructura obligatoria de tu respuesta:
                    1. 🎯 El Reto (Incluye aquí el material base creativo que elegiste para que el estudiante trabaje sobre él).
                    2. 🛠️ Entregable y Herramientas: (Qué debe hacer exactamente y en dónde, ej: redactar un correo de respuesta, un cálculo en Excel, un plan de 3 pasos).
                    3. 📊 KPI de Éxito: (Cómo sabrá el estudiante que su respuesta es correcta).

                    Tono: Inspirador, estilo Kuepa, retador, sin lenguaje académico aburrido. Empuja a la acción inmediata.
                    """
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=MODELO_GROQ,
                        temperature=0.85, # Aumentamos un poco la temperatura para que sea más creativo y no repita el mismo formato.
                    )
                    st.markdown(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error de la IA: {e}")

# ==========================================
# PESTAÑA 2: ESTUDIANTES
# ==========================================
with t2:
    st.header("🛡️ Guía de Práctica")
    e_est = st.selectbox("Empresa a la que vas a ingresar:", sorted(df['Empresa'].unique()), key="est_e")
    
    if st.button("🛡️ Ver Consejos de Supervivencia"):
        try:
            prompt = f"Dame 3 consejos clave para tener éxito en mi práctica profesional en la empresa {e_est}. Usa el tono de voz oficial de Kuepa: habla claro, sin tecnicismos innecesarios, usa un lenguaje humano y cercano. Motiva desde la acción y orienta dando seguridad. ¡Sé inspirador!"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODELO_GROQ,
            )
            st.write(chat_completion.choices[0].message.content)
        except Exception as e: 
            st.error(f"Error: {e}")
