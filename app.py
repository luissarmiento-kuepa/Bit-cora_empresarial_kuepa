import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine", page_icon="🎓", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (SECRETOS Y MODELO) ---
# Usamos un bloque try-except para asegurar que el modelo se cree correctamente
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ No se encontró la clave 'GEMINI_API_KEY' en los Secrets de Streamlit.")
        st.stop()
    
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Usamos el nombre de modelo más compatible
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"⚠️ Error al configurar la IA: {e}")
    st.stop()

# --- 3. FUNCIÓN DE CARGA DE DATOS (GOOGLE SHEETS + CSV) ---
@st.cache_data
def load_data():
    try:
        # --- CARGAR BITÁCORA DESDE GOOGLE SHEETS ---
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        # dtype=str evita el error de float64/números
        df_empresas = pd.read_csv(SHEET_URL, dtype=str)
        df_empresas.columns = df_empresas.columns.str.strip()
        
        # Estandarizar nombre de la columna 'Empresa'
        posibles_nombres = ['Empresas asociadas', 'EMPRESA', 'Nombre de la Empresa']
        for nombre in posibles_nombres:
            if nombre in df_empresas.columns:
                df_empresas.rename(columns={nombre: 'Empresa'}, inplace=True)
                break
        
        df_empresas.fillna("Información no disponible", inplace=True)

        # --- CARGAR PROGRAMAS DESDE CSV LOCAL (GITHUB) ---
        try:
            df_programas = pd.read_csv("programas.csv", dtype=str, encoding='utf-8-sig')
            df_programas.columns = df_programas.columns.str.strip()
            if 'Perfil_Del_Egresado' in df_programas.columns:
                df_programas.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
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

# Validar que los datos existan
if df is None or df_prog is None:
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---
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
        prog_list = sorted(df_prog['Programa'].unique()) if 'Programa' in df_prog.columns else ['General']
        prog_sel = st.selectbox("Selecciona Programa Técnico:", prog_list)
    with col2:
        emp_list = sorted(df['Empresa'].unique())
        empresa_profe = st.selectbox("Selecciona Empresa Destino:", emp_list, key="profe_emp")
    
    tema_clase = st.text_input("Habilidad Técnica / Tema de hoy:", placeholder="Ej: Excel, SQL, Servicio al cliente...")

    if st.button("🚀 Diseñar Actividad Disruptiva"):
        if not tema_clase:
            st.warning("Por favor, escribe un tema para generar la actividad.")
        else:
            with st.spinner("Generando reto pedagógico..."):
                try:
                    # Datos empresa y programa
                    data_emp = df[df['Empresa'] == empresa_profe].iloc[0]
                    data_prog = df_prog[df_prog['Programa'] == prog_sel].iloc[0] if prog_sel in df_prog['Programa'].values else {}
                    
                    info_empresa = "\n".join([f"- {k}: {v}" for k, v in data_emp.items()])

                    prompt = f"""
                    Actúa como un Lead Instructor de Kuepa experto en metodología 'Learning by doing'.
                    TEMA: {tema_clase}
                    PROGRAMA: {prog_sel}
                    PERFIL: {data_prog.get('Perfil', 'Estudiante técnico')}

                    INFORMACIÓN DE LA EMPRESA:
                    {info_empresa}

                    MISIÓN: Diseña un reto de 15 min para Breakrooms basado en la realidad de esta empresa.
                    Responde con: 1. El Reto, 2. Herramientas, 3. KPI de éxito.
                    """
                    
                    response = model.generate_content(prompt)
                    st.success("🎯 Propuesta de Actividad:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error al generar contenido: {e}")

# ==========================================
# PESTAÑA 2: ESTUDIANTES
# ==========================================
with tab2:
    st.header("🛡️ Guía de Supervivencia Laboral")
    empresa_est = st.selectbox("¿A qué empresa vas?", sorted(df['Empresa'].unique()), key="est_emp")
    
    data_est = df[df['Empresa'] == empresa_est].iloc[0]
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("👔 Vestuario", data_est.get('Código de vestimenta', 'No especifica'))
    with col_b:
        st.metric("🏢 Sector", data_est.get('Sector', 'General'))

    if st.button("🛡️ Ver Consejos de Éxito"):
        with st.spinner("Preparando tus tips..."):
            info_est = "\n".join([f"- {k}: {v}" for k, v in data_est.items()])
            prompt = f"Dame 3 consejos clave para tener éxito en mi práctica en la empresa {empresa_est} basándote en esta info: {info_est}. Sé motivador."
            
            try:
                response = model.generate_content(prompt)
                st.info("Estrategia recomendada:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# PESTAÑA 3: GESTORES
# ==========================================
with tab3:
    st.header("🤝 Preparación de Reunión")
    empresa_gest = st.selectbox("Empresa a visitar:", sorted(df['Empresa'].unique()), key="gest_emp")
    data_gest = df[df['Empresa'] == empresa_gest].iloc[0]

    st.write(f"**Estado actual:** {data_gest.get('ESTADO', 'Activo')}")
    
    if st.button("🤝 Generar Guion de Visita"):
        with st.spinner("Creando guion estratégico..."):
            info_gest = "\n".join([f"- {k}: {v}" for k, v in data_gest.items()])
            prompt = f"Genera un guion de 3 puntos para una reunión con la empresa {empresa_gest} usando estos datos: {info_gest}. Enfócate en mejorar la relación."
            
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
