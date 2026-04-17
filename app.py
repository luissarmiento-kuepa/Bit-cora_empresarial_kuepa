import streamlit as st
import pandas as pd
from groq import Groq
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="MentorIA KP - Técnicos Laborales", page_icon="🎓", layout="wide")

# --- 2. ESTILOS VISUALES (BRANDING KUEPA) ---
# Usamos los colores oficiales: Naranja #FD531E, Gris Oscuro #292929, Verde #149852, Fondo #FAFAFA
# Tipografía: Montserrat como alternativa web a Gotham, y Barlow.
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&family=Montserrat:wght@400;700&display=swap');

    /* Tipografía general y fondo */
    html, body, [class*="css"]  {
        font-family: 'Barlow', sans-serif;
        color: #292929;
        background-color: #FAFAFA;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #FD531E !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
    }

    /* Botones primarios */
    .stButton>button {
        background-color: #FD531E;
        color: #FAFAFA;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #149852; /* Verde Kuepa en hover */
        color: #FAFAFA;
        border: none;
        transform: scale(1.02);
    }

    /* Estilo de las Pestañas (Tabs) */
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

# --- 5. INTERFAZ PRINCIPAL ---

# Cargar Logo si existe
if os.path.exists("logo-Kuepa.png"):
    st.image("logo-Kuepa.png", width=250)

st.title("MentorIA KP - Técnicos Laborales KUEPA")
st.markdown("---")

# Solo dos pestañas ahora
t1, t2 = st.tabs(["👨‍🏫 DOCENTES", "🎓 ESTUDIANTES"])

# ==========================================
# PESTAÑA 1: DOCENTES
# ==========================================
with t1:
    st.header("🛠️ Diseñador de Retos")
    c1, c2 = st.columns(2)
    with c1:
        p_sel = st.selectbox("Programa:", sorted(df_prog['Programa'].unique()))
    with c2:
        e_sel = st.selectbox("Empresa:", sorted(df['Empresa'].unique()), key="doc_e")
    
    tema = st.text_input("Tema de la clase:")
    
    if st.button("🚀 Generar Actividad"):
        if tema:
            with st.spinner("Groq procesando a la velocidad de la luz..."):
                try:
                    row = df[df['Empresa'] == e_sel].iloc[0]
                    contexto = "\n".join([f"{k}: {v}" for k, v in row.items()])
                    prompt = f"Como experto en Kuepa, crea un reto de 15 min sobre {tema} para el programa {p_sel} usando esta info de la empresa {e_sel}: {contexto}. Responde de forma estructurada: 1. Reto, 2. Herramientas y 3. KPI. Usa el tono de voz de Kuepa: inspirador, cercano, claro y enfocado en la acción."
                    
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=MODELO_GROQ,
                    )
                    st.markdown(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error de la IA: {e}")

# ==========================================
# PESTAÑA 2: ESTUDIANTES
# ==========================================
with t2:
    st.header("🛡️ Guía de Práctica")
    e_est = st.selectbox("Empresa:", sorted(df['Empresa'].unique()), key="est_e")
    
    if st.button("🛡️ Ver Consejos"):
        try:
            prompt = f"Dame 3 consejos clave para tener éxito en mi práctica profesional en la empresa {e_est}. Usa el tono de voz oficial de Kuepa: habla claro, sin tecnicismos innecesarios, usa un lenguaje humano y cercano. Motiva desde la acción y orienta dando seguridad. ¡Sé inspirador!"
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODELO_GROQ,
            )
            st.write(chat_completion.choices[0].message.content)
        except Exception as e: 
            st.error(f"Error: {e}")
