import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine", page_icon="🎓", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (SECRETOS) ---
# Recuerda que en los Secrets de Streamlit debe estar: GEMINI_API_KEY = "tu_llave"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ Error con la API Key de Gemini. Verifica los Secrets en Streamlit Cloud.")
    st.stop()

# --- 3. FUNCIÓN DE CARGA DE DATOS (GOOGLE SHEETS + CSV) ---
@st.cache_data
def load_data():
    try:
        # --- CARGAR BITÁCORA DESDE GOOGLE SHEETS ---
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        df_empresas = pd.read_csv(SHEET_URL)
        df_empresas.columns = df_empresas.columns.str.strip()
        
        # Estandarizar nombre de la columna principal de empresas
        if 'Empresas asociadas' in df_empresas.columns:
            df_empresas.rename(columns={'Empresas asociadas': 'Empresa'}, inplace=True)
        
        df_empresas.fillna("Información no disponible", inplace=True)

        # --- CARGAR PROGRAMAS DESDE CSV LOCAL (GITHUB) ---
        try:
            df_programas = pd.read_csv("programas.csv", encoding='utf-8-sig')
            df_programas.columns = df_programas.columns.str.strip()
            # Ajustar nombre de columna de perfil si es necesario
            if 'Perfil_Del_Egresado' in df_programas.columns:
                df_programas.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
            # Respaldo si no encuentra el archivo programas.csv
            df_programas = pd.DataFrame({
                'Programa': ['General'], 
                'Perfil': ['Estudiante Kuepa'], 
                'Competencias': ['Habilidades Transversales']
            })

        return df_empresas, df_programas

    except Exception as e:
        st.error(f"❌ Error crítico al conectar con los datos: {e}")
        return None, None

# Ejecutar carga de datos
df, df_prog = load_data()

# --- 4. VERIFICACIÓN DE SEGURIDAD ---
if df is None or df_prog is None:
    st.warning("No se pudieron cargar los datos. Verifica que el Google Sheet sea público y los archivos estén en GitHub.")
    st.stop()

# --- 5. INTERFAZ DE USUARIO ---
st.title("🎓 Kuepa Insight Engine")
st.markdown("### 🚀 Sistema de Inteligencia para Formación Dual")

tab1, tab2, tab3 = st.tabs(["👨‍🏫 DOCENTES", "🎓 ESTUDIANTES", "💼 GESTORES"])

# ==========================================
# PESTAÑA 1: DOCENTES
# ==========================================
with tab1:
    st.header("🛠️ Diseñador de Retos Prácticos")
    
    col1, col2 = st.columns(2)
    with col1:
        # Selector de Programa
        prog_list = df_prog['Programa'].unique() if 'Programa' in df_prog.columns else ['General']
        prog_sel = st.selectbox("Programa Técnico:", prog_list)
    with col2:
        # Selector de Empresa
        emp_list = df['Empresa'].unique()
        empresa_profe = st.selectbox("Empresa Destino:", emp_list, key="profe_emp")
    
    tema_clase = st.text_input("Habilidad Técnica / Tema de hoy:", placeholder="Ej: Excel, SQL, Servicio al cliente...")

    if st.button("🚀 Diseñar Actividad Disruptiva"):
        if not tema_clase:
            st.warning("Escribe un tema para la clase.")
        else:
            with st.spinner("Consultando cerebros..."):
                # Datos empresa y programa
                data_emp = df[df['Empresa'] == empresa_profe].iloc[0]
                data_prog = df_prog[df_prog['Programa'] == prog_sel].iloc[0] if prog_sel in df_prog['Programa'].values else {}
                
                # MODO ESPONJA: Leer todas las columnas de la empresa
                info_empresa = "\n".join([f"- {k}: {v}" for k, v in data_emp.items()])

                prompt = f"""
                Actúa como un Lead Instructor de Kuepa.
                Contexto: Clases virtuales, metodología 'Aprender Haciendo'.
                
                TEMA: {tema_clase}
                PROGRAMA: {prog_sel}
                PERFIL DEL EGRESADO: {data_prog.get('Perfil', 'General')}

                INFORMACIÓN DE LA EMPRESA (Bitácora):
                {info_empresa}

                MISIÓN: Diseña un reto de 15 min para Breakrooms basado en las funciones reales de esta empresa.
                Responde con: 1. El Reto, 2. Herramientas, 3. KPI de éxito.
                """
                response = model.generate_content(prompt)
                st.success("🎯 Propuesta de Actividad:")
                st.write(response.text)

# ==========================================
# PESTAÑA 2: ESTUDIANTES
# ==========================================
with tab2:
    st.header("🛡️ Guía de Supervivencia Laboral")
    empresa_est = st.selectbox("¿A qué empresa vas?", df['Empresa'].unique(), key="est_emp")
    
    data_est = df[df['Empresa'] == empresa_est].iloc[0]
    
    col_a, col_b = st.columns(2)
    col_a.metric("👔 Vestuario", data_est.get('Código de vestimenta', 'No especifica'))
    col_b.metric("🏢 Sector", data_est.get('Sector', 'General'))

    if st.button("🛡️ Ver Consejos de Éxito"):
        info_est = "\n".join([f"- {k}: {v}" for k, v in data_est.items()])
        prompt = f"""
        Eres un Mentor de Kuepa. Un estudiante va a {empresa_est}.
        Analiza estos datos de la bitácora empresarial:
        {info_est}
        
        Dame 3 consejos clave para que no lo despidan y tenga éxito, basándote en la cultura y motivos de fracaso reportados.
        """
        response = model.generate_content(prompt)
        st.info("Estrategia recomendada:")
        st.write(response.text)

# ==========================================
# PESTAÑA 3: GESTORES
# ==========================================
with tab3:
    st.header("🤝 Preparación de Reunión")
    empresa_gest = st.selectbox("Empresa a visitar:", df['Empresa'].unique(), key="gest_emp")
    data_gest = df[df['Empresa'] == empresa_gest].iloc[0]

    st.write(f"**Estado actual:** {data_gest.get('ESTADO', 'Pendiente')}")
    
    if st.button("🤝 Generar Guion de Visita"):
        info_gest = "\n".join([f"- {k}: {v}" for k, v in data_gest.items()])
        prompt = f"""
        Eres un Consultor Senior de Kuepa. Vas a visitar a {empresa_gest}.
        Datos actuales: {info_gest}
        
        Genera un guion de 3 puntos para la reunión:
        1. Rompehielos (basado en su visión/historia).
        2. Seguimiento de compromisos pendientes.
        3. Propuesta de valor para recibir más aprendices.
        """
        response = model.generate_content(prompt)
        st.write(response.text)
