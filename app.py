import streamlit as st
import pandas as pd
from groq import Groq
import os

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="MentorIA KP - Técnicos Laborales", page_icon="🎓", layout="wide")

# --- 2. ESTILOS VISUALES (DARK MODE CORREGIDO) ---
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&family=Montserrat:wght@700;800&display=swap');

    [data-testid="stAppViewContainer"], .stApp {
        background-color: #292929;
        color: #FAFAFA;
        font-family: 'Barlow', sans-serif;
    }

    label p, 
    div[data-baseweb="radio"] div, 
    .stMarkdown p, 
    div[data-testid="stText"],
    .stSelectbox label,
    .stTextInput label {
        color: #FAFAFA !important;
        font-size: 1.05rem;
    }

    h1, h2, h3 {
        font-family: 'Montserrat', sans-serif;
        text-transform: uppercase;
        letter-spacing: -0.5px;
    }

    h1 { color: #FD531E !important; font-size: 2.5rem !important; }
    h2 { color: #FD531E !important; border-bottom: 2px solid #FD531E; padding-bottom: 10px; margin-bottom: 20px;}
    h3 { color: #FAFAFA !important; } 

    [data-testid="stImage"] img {
        background-color: #FAFAFA;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    .activity-box {
        background-color: #333333;
        border-left: 5px solid #FD531E;
        padding: 25px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        color: #FAFAFA !important;
    }
    
    .activity-box h2 {
        font-size: 1.4rem;
        border-bottom: none;
        margin-top: 0;
    }

    .stButton>button {
        background-color: #FD531E;
        color: white !important;
        border-radius: 5px;
        border: none;
        padding: 10px 25px;
        font-weight: 700;
        width: 100%;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #149852;
        border: none;
        color: white !important;
        transform: translateY(-2px);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 15px; }

    .stTabs [data-baseweb="tab-list"] button {
        background-color: #333333;
        color: #AAAAAA !important;
        border-radius: 8px 8px 0 0;
        padding: 10px 25px;
        border: none;
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

st.title("MentorIA KP - Técnicos Laborales")

tab1, tab2 = st.tabs(["👨‍🏫 MÓDULO DOCENTE", "🎓 MÓDULO ESTUDIANTE"])

# ==========================================
# DOCENTES
# ==========================================
with tab1:
    st.markdown("### 🛠️ Diseñador de Retos Profesionales")
    
    with st.container():
        c1, c2 = st.columns(2)
        p_sel = c1.selectbox("Programa:", sorted(df_prog['Programa'].unique()))
        t_filtro = c2.radio("Contexto de la actividad:", ["Por Empresa", "Por Sector"], horizontal=True)
        
        if t_filtro == "Por Empresa":
            sel_e = st.selectbox("Empresa Destino:", sorted(df['Empresa'].unique()))
            ctx = f"Empresa: {sel_e}. Bitácora: " + ", ".join([f"{k}:{v}" for k,v in df[df['Empresa']==sel_e].iloc[0].items()])
        else:
            sel_s = st.selectbox("Sector Industrial:", sorted(sectores))
            ctx = f"Sector Industrial: {sel_s}"
            
        c3, c4 = st.columns([2, 1])
        tema = c3.text_input("Tema de la sesión (ej. Conciliación bancaria, Empatía digital):")
        formato_recurso = c4.selectbox("Formato del Recurso:", [
            "🎲 Aleatorio (Recomendado por IA)", 
            "📊 Tabla de Datos", 
            "📈 Análisis de Gráfico / Tendencia", 
            "📖 Caso Real / Storytelling", 
            "✉️ Simulación de Comunicación", 
            "🕵️‍♂️ Diagnóstico de Error"
        ])

    if st.button("🚀 GENERAR RETO DISRUPTIVO"):
        if tema:
            with st.spinner("Diseñando experiencia de aprendizaje..."):
                
                # INSTRUCCIÓN CONDICIONAL SEGÚN EL FORMATO ELEGIDO
                if "Aleatorio" in formato_recurso:
                    instruccion_formato = """
                    EL INSTRUCTOR ELIGIÓ MODO ALEATORIO. 
                    ELIGE el formato que mejor se adapte al tema entre: Tabla de datos, Descripción de un gráfico, Caso de estudio, Simulación de correo/chat urgente, o Diagnóstico de un error en un proceso.
                    """
                elif "Tabla" in formato_recurso:
                    instruccion_formato = "OBLIGATORIO: Presenta el problema creando una pequeña tabla de datos crudos (máximo 5 filas) en formato Markdown para que el estudiante trabaje sobre ella."
                elif "Gráfico" in formato_recurso:
                    instruccion_formato = "OBLIGATORIO: Presenta el problema describiendo textualmente el comportamiento de una gráfica o indicador (ej. 'Las ventas de Enero fueron X y en Febrero cayeron a Y...')."
                elif "Caso Real" in formato_recurso:
                    instruccion_formato = "OBLIGATORIO: Presenta el problema narrando un caso real, historia o storytelling inmersivo de algo que ocurrió hoy en la empresa/sector."
                elif "Simulación" in formato_recurso:
                    instruccion_formato = "OBLIGATORIO: Presenta el problema simulando una comunicación real (ej. El texto exacto de un correo de un cliente furioso, o un WhatsApp urgente del jefe pidiendo ayuda)."
                elif "Diagnóstico" in formato_recurso:
                    instruccion_formato = "OBLIGATORIO: Presenta un proceso que se hizo MAL (un error en una factura, un mal servicio, un paso omitido) para que el estudiante actúe como auditor/solucionador."

                prompt = f"""
                Actúa como un Diseñador Instruccional Senior de Kuepa. Crea un reto de 20 min para el programa {p_sel} sobre el tema '{tema}'.
                Contexto: {ctx}

                {instruccion_formato}

                ESTRUCTURA DE RESPUESTA (Usa Markdown estricto con '##' para cada sección):
                ## 📝 EL ESCENARIO CREATIVO
                (Desarrolla aquí el problema siguiendo ESTRICTAMENTE el formato que se te ordenó arriba. NO asumas que el estudiante tiene acceso a datos de la empresa, entrégale todo aquí).

                ## 🎯 EL RETO (ACCIÓN)
                (Qué debe hacer el estudiante individualmente en 15 minutos).

                ## 💻 ENTREGABLE TANGIBLE Y HERRAMIENTAS
                (Define UN producto digital claro. Obligatorio: Sugiere el uso de una herramienta gratuita (Google Suite, Canva, etc) Y describe cómo el estudiante debe usar una IA -como ChatGPT o Claude- de forma estratégica para mejorar ese entregable).

                ## 📋 RÚBRICA PARA EL DOCENTE
                (Crea una lista de 3 elementos clave que el docente debe validar en el entregable para darlo por aprobado).
                
                Tono: Profesional, minimalista, inspirador.
                """
                
                try:
                    res = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model=MODELO_GROQ, temperature=0.7).choices[0].message.content
                    
                    sections = res.split("##")
                    for section in sections:
                        if section.strip():
                            st.markdown(f'<div class="activity-box"><h2>{section.splitlines()[0]}</h2><p>{"<br>".join(section.splitlines()[1:])}</p></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generando actividad: {e}")
        else:
            st.warning("Escribe un tema primero para generar el reto.")

# ==========================================
# ESTUDIANTES
# ==========================================
with tab2:
    st.markdown("### 🛡️ Guía de Éxito en la Práctica")
    e_est = st.selectbox("Selecciona tu empresa destino:", sorted(df['Empresa'].unique()))
    
    if st.button("🛡️ SOLICITAR CONSEJOS DE MENTORÍA"):
        with st.spinner("Conectando con tu mentor virtual..."):
            p_est = f"Como mentor de Kuepa, dame 3 consejos prácticos y motivadores para destacar en mi práctica en la empresa {e_est}. Habla de forma cercana y enfocada a la acción. Usa formato Markdown."
            try:
                res_est = client.chat.completions.create(messages=[{"role": "user", "content": p_est}], model=MODELO_GROQ).choices[0].message.content
                st.markdown(f'<div class="activity-box">{res_est}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generando consejos: {e}")
