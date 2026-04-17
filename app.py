import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine", page_icon="🎓", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (SECRETOS) ---
try:
    # Intenta leer la API KEY desde los Secrets de Streamlit
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
        
        # EL PARCHE: Forzamos a que todo sea texto (dtype=str) para evitar el error de float64
        df_empresas = pd.read_csv(SHEET_URL, dtype=str)
        df_empresas.columns = df_empresas.columns.str.strip()
        
        # Estandarizar nombre de la columna principal de empresas
        if 'Empresas asociadas' in df_empresas.columns:
            df_empresas.rename(columns={'Empresas asociadas': 'Empresa'}, inplace=True)
        elif 'EMPRESA' in df_empresas.columns:
            df_empresas.rename(columns={'EMPRESA': 'Empresa'}, inplace=True)
        
        df_empresas.fillna("Información no disponible", inplace=True)

        # --- CARGAR PROGRAMAS DESDE CSV LOCAL (GITHUB) ---
        try:
            # También forzamos texto aquí por seguridad
            df_programas = pd.read_csv("programas.csv", dtype=str, encoding='utf-8-sig')
            df_programas.columns = df_programas.columns.str.strip()
            
            # Ajustar nombre de columna de perfil si es necesario
            if 'Perfil_Del_Egresado' in df_programas.columns:
                df_programas.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
            # Respaldo si no encuentra el archivo programas.csv en GitHub
            df_programas = pd.DataFrame({
                'Programa': ['General'], 
                'Perfil': ['Estudiante Kuepa'], 
                'Competencias': ['Habilidades Transversales']
            })

        # RETORNO VITAL: Entregamos los dos paquetes de datos
        return df_empresas, df_programas

    except Exception as e:
        st.error(f"❌ Error crítico al conectar con los datos: {e}")
        return None, None

# --- 4. EJECUCIÓN Y VALIDACIÓN ---
df, df_prog = load_data()

if df is None or df_prog is None:
    st.warning("No se pudieron cargar los datos. Revisa el link de Google Sheets o los archivos en GitHub.")
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
        prog_list = df_prog['Programa'].unique() if 'Programa' in df_prog.columns else ['General']
        prog_sel = st.selectbox("Selecciona Programa Técnico:", prog_list)
    with col2:
        emp_list = df['Empresa'].unique()
        empresa_profe = st.selectbox("Selecciona Empresa Destino:", emp_list, key="profe_emp")
    
    tema_clase = st.text_input("Habilidad Técnica / Tema de hoy:", placeholder="Ej: Excel, SQL, Servicio al cliente...")

    if st.button("🚀 Diseñar Actividad Disruptiva"):
        if not tema_clase:
            st.warning("Escribe un tema para la clase.")
        else:
            with st.spinner("La IA está analizando la bitácora..."):
                # Extraer datos específicos
                data_emp = df[df['Empresa'] == empresa_profe].iloc[0]
                data_prog = df_prog[df_prog['Programa'] == prog_sel].iloc[0] if prog_sel in df_prog['Programa'].values else {}
                
                # Resumen de toda la información de la empresa para el prompt
                info_empresa = "\n".join([f"- {k}: {v}" for k, v in data_emp.items()])

                prompt = f"""
                Actúa como un Lead Instructor de Kuepa experto en metodología 'Learning by doing'.
                
                TEMA DE CLASE: {tema_clase}
                PROGRAMA TÉCNICO: {prog_sel}
                PERFIL DEL ESTUDIANTE: {data_prog.get('Perfil', 'General')}

                CONTEXTO REAL DE LA EMPRESA (Bitácora):
                {info_empresa}

                TU MISIÓN:
                Diseña un micro-reto de 15 minutos para Breakrooms donde el estudiante aplique {tema_clase} 
                resolviendo un problema real basado en la información de la empresa {empresa_profe}.
                
                Responde con:
                1. **El Reto:** (Contexto y problema).
                2. **Herramientas:** (Qué deben usar).
                3. **KPI de Éxito:** (Cómo sabemos que lo hicieron bien).
                """
                
                response = model.generate_content(prompt)
                st.success("🎯 Propuesta de Actividad:")
                st.markdown(response.text)

# ==========================================
# PESTAÑA 2: ESTUDIANTES
# ==========================================
with tab2:
    st.header("🛡️ Guía de Supervivencia Laboral")
    empresa_est = st.selectbox("¿A qué empresa vas a entrar?", df['Empresa'].unique(), key="est_emp")
    
    data_est = df[df['Empresa'] == empresa_est].iloc[0]
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("👔 Código de Vestimenta", data_est.get('Código de vestimenta', 'No especifica'))
    with col_b:
        st.metric("🏢 Sector Económico", data_est.get('Sector', 'General'))

    if st.button("🛡️ Ver Tips de Éxito"):
        info_est = "\n".join([f"- {k}: {v}" for k, v in data_est.items()])
        prompt = f"""
        Eres un Mentor de Prácticas en Kuepa. Un estudiante está nervioso porque empieza en {empresa_est}.
        Basándote en esta información:
        {info_est}
        
        Dame 3 consejos de 'oro' específicos para esta empresa que le aseguren el éxito y eviten que lo despidan.
        Se breve y motivador.
        """
        response = model.generate_content(prompt)
        st.info("Estrategia para el primer día:")
        st.write(response.text)

# ==========================================
# PESTAÑA 3: GESTORES
# ==========================================
with tab3:
    st.header("🤝 Preparación de Visita Empresarial")
    empresa_gest = st.selectbox("Selecciona empresa para la visita:", df['Empresa'].unique(), key="gest_emp")
    data_gest = df[df['Empresa'] == empresa_gest].iloc[0]

    st.write(f"**Estado de la relación:** {data_gest.get('ESTADO', 'Activo')}")
    
    if st.button("🤝 Generar Guion de Reunión"):
        info_gest = "\n".join([f"- {k}: {v}" for k, v in data_gest.items()])
        prompt = f"""
        Eres un Gestor de Relaciones Corporativas Senior. Vas a reunirte con {empresa_gest}.
        Datos de la bitácora: {info_gest}
        
        Genera un guion estratégico:
        1. Un dato curioso/positivo para romper el hielo.
        2. Un punto crítico que debemos solucionar según la bitácora.
        3. Una propuesta para aumentar el número de aprendices.
        """
        response = model.generate_content(prompt)
        st.markdown(response.text)
