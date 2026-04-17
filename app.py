import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine - Modelo Operativo", page_icon="🎓", layout="wide")

# --- CONFIGURACIÓN DE IA ---
# Streamlit leerá la clave de forma secreta y segura en la nube
API_KEY = st.secrets["GEMINI_API_KEY"]
if API_KEY:
    genai.configure(api_key=API_KEY)

def get_gemini_model():
    try:
        modelos = genai.list_models()
        for m in modelos:
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return genai.GenerativeModel(m.name)
        return genai.GenerativeModel('gemini-pro')
    except Exception:
        return genai.GenerativeModel('gemini-2.0-flash')

model = get_gemini_model()

# --- CARGAR DATOS DINÁMICOS ---
@st.cache_data(ttl=600)
def load_data():
    try:
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        df_empresas = pd.read_csv(SHEET_URL)
        df_empresas.columns = df_empresas.columns.str.strip()
        if 'Empresas asociadas' in df_empresas.columns:
            df_empresas.rename(columns={'Empresas asociadas': 'Empresa'}, inplace=True)
        df_empresas.fillna("Información no disponible", inplace=True)
        
        try:
            df_programas = pd.read_csv("programas.csv", sep=None, engine='python', encoding='utf-8-sig')
            df_programas.columns = df_programas.columns.str.strip()
            if 'Perfil_Del_Egresado' in df_programas.columns:
                df_programas.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
            df_programas = pd.DataFrame({'Programa': ['General'], 'Competencias': ['Operativas']})

        return df_empresas, df_programas
    except Exception as e:
        st.error(f"Error en base de datos: {e}")
        return None, None

df, df_prog = load_data()

# --- INTERFAZ ---
st.title("🎓 Kuepa Insight Engine")

tab1, tab2, tab3 = st.tabs(["👨‍🏫 DOCENTES", "🎓 ESTUDIANTES", "💼 GESTORES"])

# ==========================================
# PESTAÑA 1: DOCENTES (ENFOQUE OPERATIVO + OFIMÁTICA + IA)
# ==========================================
with tab1:
    st.header("🛠️ Diseñador de Retos Técnicos Operativos")
    st.info("Genera retos enfocados en productividad, herramientas ofimáticas e IA aplicada.")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        prog_seleccionado = st.selectbox("Programa Técnico:", df_prog['Programa'].unique())
        tema_clase = st.text_input("Tema técnico del día:", placeholder="Ej: Control de inventarios, Dashboard de ventas...")
        modalidad = st.radio("Dinámica:", ["Individual", "Grupal"])
        
    with c2:
        empresas_sel = st.multiselect("Empresas de los estudiantes:", options=df['Empresa'].unique())

    if st.button("🚀 Generar Reto 'Aprender Haciendo'", key="btn_profe"):
        if not tema_clase or not empresas_sel:
            st.warning("Completa el tema y las empresas.")
        else:
            with st.spinner("Construyendo escenario de simulación operativa..."):
                # Consolidación de contexto
                df_contexto = df[df['Empresa'].isin(empresas_sel)]
                resumen_emp = "\n".join([f"- {r['Empresa']} ({r['Sector']}): {r['Funciones 1']}" for _, r in df_contexto.iterrows()])
                data_prog = df_prog[df_prog['Programa'] == prog_seleccionado].iloc[0]

                # --- EL PROMPT MAESTRO ACTUALIZADO ---
                prompt = f"""
                Actúa como Lead Técnico de Kuepa. Diseña un reto basado en el modelo 'Aprender Haciendo'.
                POBLACIÓN: Jóvenes y adultos en formación técnica operativa.
                TEMA: {tema_clase} | MODALIDAD: {modalidad}
                PROGRAMA: {prog_seleccionado} | COMPETENCIAS: {data_prog.get('Competencias')}

                CONTEXTO EMPRESARIAL:
                {resumen_emp}

                REGLAS DE ORO DE KUEPA:
                1. Mínima teoría: Prohibido "investigar y documentar" como tarea principal. 
                2. Protagonismo Ofimático: El reto DEBE exigir el uso de Google Sheets/Excel (nivel intermedio: tablas, fórmulas de búsqueda, filtros, o gráficas).
                3. IA como Copiloto: Sugiere el uso de herramientas de IA gratuitas (Perplexity para búsqueda rápida, Claude para redacción, Canva Magic para diseño, o ChatGPT para fórmulas).
                4. Pensamiento Estratégico: El reto debe pedir un análisis de los datos (Ej: "¿Qué decisión tomarías basándote en esta tabla?").

                ESTRUCTURA DE RESPUESTA:
                1. 🏢 **El Escenario Laboral:** Una situación real en el puesto de trabajo.
                2. 🛠️ **Misión Técnica (Uso de Herramientas):** - Paso 1: Usar IA para estructurar la solución.
                   - Paso 2: Ejecución en Sheets/Docs (Indicar qué fórmulas o funciones usar).
                3. 🧠 **Pensamiento Estratégico:** La pregunta clave que el estudiante debe responder tras procesar la información.
                4. ✅ **Entregable Profesional:** (Ej: Tabla comparativa en Sheets con análisis gráfico, Presentación de 3 slides con solución, Hoja de cálculo con fórmulas).
                """
                
                response = model.generate_content(prompt)
                st.success(f"🎯 Reto {modalidad} Operativo:")
                st.write(response.text)

# (Se mantienen pestañas 2 y 3 con la misma lógica de conexión al Drive)
with tab2:
    st.header("Simulador de Cultura")
    empresa_est = st.selectbox("Empresa:", df['Empresa'].unique(), key="est_emp")
    data_est = df[df['Empresa'] == empresa_est].iloc[0]
    st.error(f"🚨 **ALERTA:** {data_est.get('Motivos comunes de fracaso ', 'Sin alertas.')}")

with tab3:
    st.header("Briefing de Cuenta")
    empresa_gest = st.selectbox("Empresa:", df['Empresa'].unique(), key="gest_emp")
    data_gest = df[df['Empresa'] == empresa_gest].iloc[0]
    st.metric("Estado", data_gest.get('ESTADO', 'N/A'))
