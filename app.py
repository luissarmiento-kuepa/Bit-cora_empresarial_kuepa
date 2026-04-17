import streamlit as st
import pandas as pd
from groq import Groq
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="MentorIA KP - Técnicos Laborales", page_icon="🎓", layout="wide")

# --- 2. ESTILOS VISUALES (DARK MODE & BRANDING KUEPA) ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&family=Montserrat:wght@700;800&display=swap');

    /* Fondo principal Dark de Kuepa */
    [data-testid="stAppViewContainer"] {
        background-color: #292929;
        color: #FAFAFA;
        font-family: 'Barlow', sans-serif;
    }

    /* Ajuste de Sidebar y Headers */
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: rgba(0,0,0,0);
    }

    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        text-transform: uppercase;
        letter-spacing: -0.5px;
    }

    h1 { color: #FD531E !important; font-size: 2.5rem !important; }
    h2 { color: #FD531E !important; border-bottom: 2px solid #FD531E; padding-bottom: 10px; }

    /* Estilo de Tarjetas de Actividad */
    .activity-box {
        background-color: #333333;
        border-left: 5px solid #FD531E;
        padding: 25px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .rubric-box {
        background-color: #1e1e1e;
        border: 1px dashed #149852;
        padding: 20px;
        border-radius: 10px;
        margin-top: 30px;
    }

    /* Botones */
    .stButton>button {
        background-color: #FD531E;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 25px;
        font-weight: 700;
        width: 100%;
    }

    .stButton>button:hover {
        background-color: #149852;
        border: none;
        color: white;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }

    .stTabs [data-baseweb="tab-list"] button {
        background-color: #333333;
        color: #888888;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #FD531E;
        color: white !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE IA (GROQ) ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    MODELO_GROQ = "llama-3.3-70b-versatile" 
except Exception:
    st.error("❌ Error de conexión. Revisa tus Secrets.")
    st.stop()

# --- 4. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df_ent = pd.read_csv(URL, dtype=str)
        df_ent.columns = df_ent.columns.str.strip()
        
        t_col = next((c for c in df_ent.columns if "empresa" in c.lower() or "asociadas" in c.lower()), df_ent.columns[0])
        df_ent.rename(columns={t_col: 'Empresa'}, inplace=True)
        
        s_col = next((c for c in df_ent.columns if "sector" in c.lower()), None)
        if s_col: df_ent.rename(columns={s_col: 'Sector'}, inplace=True)
        else: df_ent['Sector'] = 'General'
        
        df_ent.fillna("No disponible", inplace=True)

        try:
            df_p = pd.read_csv("programas.csv", dtype=str)
            if 'Perfil_Del_Egresado' in df_p.columns: df_p.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
            df_p = pd.DataFrame({'Programa': ['General'], 'Perfil': ['Técnico Laboral']})

        return df_ent, df_p
    except:
        return None, None

df, df_prog = load_data()
if df is None: st.stop()

sectores = [s for s in df['Sector'].unique() if s != "No disponible"]
if not sectores: sectores = ["Tecnología", "Salud", "Administración", "Logística"]

# --- 5. INTERFAZ ---
col_logo, _ = st.columns([1, 2])
with col_logo:
    if os.path.exists("logo-Kuepa.png"):
        st.image("logo-Kuepa.png", width=220)

st.title("MentorIA KP - Técnicos Laborales KUEPA")

tab1, tab2 = st.tabs(["👨‍🏫 MÓDULO DOCENTE", "🎓 MÓDULO ESTUDIANTE"])

# ==========================================
# DOCENTES
# ==========================================
with tab1:
    st.markdown("### 🛠️ Diseñador de Retos Profesionales")
    
    with st.container():
        c1, c2 = st.columns(2)
        p_sel = c1.selectbox("Programa:", sorted(df_prog['Programa'].unique()))
        t_filtro = c2.radio("Contexto:", ["Por Empresa", "Por Sector"], horizontal=True)
        
        if t_filtro == "Por Empresa":
            sel_e = st.selectbox("Empresa:", sorted(df['Empresa'].unique()))
            ctx = f"Empresa: {sel_e}. Bitácora: " + ", ".join([f"{k}:{v}" for k,v in df[df['Empresa']==sel_e].iloc[0].items()])
        else:
            sel_s = st.selectbox("Sector:", sorted(sectores))
            ctx = f"Sector Industrial: {sel_s}"
            
        tema = st.text_input("Tema de la sesión (ej. Conciliación bancaria, Empatía digital):")

    if st.button("🚀 GENERAR RETO DISRUPTIVO"):
        if tema:
            with st.spinner("Diseñando experiencia de aprendizaje..."):
                prompt = f"""
                Actúa como un Diseñador Instruccional Senior de Kuepa. Crea un reto de 20 min para el programa {p_sel} sobre {tema}.
                Contexto: {ctx}

                ESTRUCTURA DE RESPUESTA (Usa Markdown):
                ## 📝 EL ESCENARIO CREATIVO
                (Inventa una situación real, un problema o una historia breve del sector/empresa. Entrega aquí los DATOS BASE: cifras, correos, o descripción de una gráfica).

                ## 🎯 EL RETO (ACCIÓN)
                (Qué debe hacer el estudiante en 15 min de forma individual).

                ## 💻 ENTREGABLE TANGIBLE Y HERRAMIENTAS
                (Define UN producto digital claro. Obligatorio: Sugiere el uso de una herramienta gratuita (Google Suite, Canva, etc) Y describe cómo el estudiante debe usar una IA -como ChatGPT o Claude- de forma estratégica para mejorar ese entregable).

                ## 📋 RÚBRICA PARA EL DOCENTE
                (Crea una lista de 3 elementos clave que el docente debe validar en el entregable para darlo por aprobado).
                
                Tono: Profesional, minimalista, inspirador.
                """
                
                res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODELO_GROQ).choices[0].message.content
                
                # Dividir la respuesta por secciones para ponerlas en cajas
                sections = res.split("##")
                for section in sections:
                    if section.strip():
                        st.markdown(f'<div class="activity-box">## {section}</div>', unsafe_allow_html=True)
        else:
            st.warning("Escribe un tema primero.")

# ==========================================
# ESTUDIANTES
# ==========================================
with tab2:
    st.markdown("### 🛡️ Guía de Éxito en la Práctica")
    e_est = st.selectbox("Selecciona la empresa:", sorted(df['Empresa'].unique()))
    
    if st.button("🛡️ SOLICITAR MENTORÍA"):
        p_est = f"Como mentor de Kuepa, dame 3 consejos prácticos y motivadores para destacar en {e_est}. Habla de forma cercana y enfocada a la acción."
        res_est = client.chat.completions.create(messages=[{"role": "user", "content": p_est}], model=MODELO_GROQ).choices[0].message.content
        st.markdown(f'<div class="activity-box">{res_est}</div>', unsafe_allow_html=True)
