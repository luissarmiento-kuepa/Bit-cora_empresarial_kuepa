import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine", page_icon="🎓", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (CONEXIÓN ESTABLE) ---
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave 'GEMINI_API_KEY' en los Secrets de Streamlit.")
        st.stop()
    
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    
    # Usamos el nombre de modelo más estándar y compatible actualmente
    model = genai.GenerativeModel('gemini-1.5-flash')
    
except Exception as e:
    st.error(f"⚠️ Error al configurar la IA: {e}")
    st.stop()

# --- 3. FUNCIÓN DE CARGA DE DATOS (BLINDADA) ---
@st.cache_data
def load_data():
    try:
        # --- CARGAR BITÁCORA DESDE GOOGLE SHEETS ---
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        # Leemos todo como texto (str) para evitar errores de celdas vacías o números
        df_empresas = pd.read_csv(SHEET_URL, dtype=str)
        df_empresas.columns = df_empresas.columns.str.strip()
        
        # Buscador de columna de Empresa (por si cambia el nombre en el Excel)
        col_empresa = None
        for col in df_empresas.columns:
            if col.lower() in ['empresa', 'empresas asociadas', 'nombre de la empresa']:
                col_empresa = col
                break
        
        if col_empresa:
            df_empresas.rename(columns={col_empresa: 'Empresa'}, inplace=True)
        else:
            # Si no la encuentra, asumimos la primera columna como la empresa
            df_empresas.rename(columns={df_empresas.columns[0]: 'Empresa'}, inplace=True)
        
        df_empresas.fillna("Información no disponible", inplace=True)

        # --- CARGAR PROGRAMAS DESDE CSV LOCAL (GITHUB) ---
        try:
            df_programas = pd.read_csv("programas.csv", dtype=str, encoding='utf-8-sig')
            df_programas.columns = df_programas.columns.str.strip()
            if 'Perfil_Del_Egresado' in df_programas.columns:
                df_programas.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except:
            # Respaldo si falla la carga del CSV en GitHub
            df_programas = pd.DataFrame({
                'Programa': ['General'], 
                'Perfil': ['Estudiante Técnico'], 
                'Competencias': ['Habilidades Transversales']
            })

        return df_empresas, df_programas

    except Exception as e:
        st.error(f"❌ Error crítico al conectar con los datos: {e}")
        return None, None

# Ejecutar carga
df, df_prog = load_data()

if df is None or df_prog is None:
    st.stop()

# --- 4. INTERFAZ DE USUARIO ---
st.title("🎓 Kuepa Insight Engine")
st.markdown("### 🚀 Herramienta de Inteligencia para Formación Dual")

tab1, tab2, tab3 = st.tabs(["👨‍🏫 DOCENTES", "🎓 ESTUDIANTES", "💼 GESTORES"])

# ==========================================
# PESTAÑA 1: DOCENTES
# ==========================================
with tab1:
    st.header("🛠️ Diseñador de Retos Prácticos")
    
    col1, col2 = st.columns(2)
    with col1:
        prog_list = sorted(df_prog['Programa'].unique())
        prog_sel = st.selectbox("Programa Técnico:", prog_list)
    with col2:
        emp_list = sorted(df['Empresa'].unique())
        empresa_profe = st.selectbox("Empresa Destino:", emp_list, key="profe_emp")
    
    tema_clase = st.text_input("Tema de la clase (Habilidad técnica):", placeholder="Ej: Tablas Dinámicas, SQL, Protocolos...")

    if st.button("🚀 Generar Actividad"):
        if not tema_clase:
            st.warning("Escribe un tema para la clase.")
        else:
            with st.spinner("La IA está analizando la bitácora empresarial..."):
                try:
                    data_emp = df[df['Empresa'] == empresa_profe].iloc[0]
                    data_prog = df_prog[df_prog['Programa'] == prog_sel].iloc[0] if prog_sel in df_prog['Programa'].values else {}
                    
                    info_contexto = "\n".join([f"- {k}: {v}" for k, v in data_emp.items()])

                    prompt = f"""
                    Actúa como un Lead Instructor de Kuepa.
                    TEMA: {tema_clase}
                    PROGRAMA: {prog_sel}
                    PERFIL: {data_prog.get('Perfil', 'Estudiante técnico')}

                    INFO EMPRESA:
                    {info_contexto}

                    MISIÓN: Crea un reto práctico de 15 min para Breakrooms basado en esta empresa.
                    Responde: 1. El Reto, 2. Herramientas, 3. KPI de éxito.
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
    st.header("🛡️ Guía de Éxito en la Práctica")
    empresa_est = st.selectbox("Selecciona tu empresa:", sorted(df['Empresa'].unique()), key="est_emp")
    
    data_est = df[df['Empresa'] == empresa_est].iloc[0]
    
    c1, c2 = st.columns(2)
    c1.metric("👔 Vestuario", data_est.get('Código de vestimenta', 'No especifica'))
    c2.metric("🏢 Sector", data_est.get('Sector', 'General'))

    if st.button("🛡️ Obtener Consejos"):
        with st.spinner("Preparando tus tips..."):
            info_est = "\n".join([f"- {k}: {v}" for k, v in data_est.items()])
            prompt = f"Dame 3 consejos clave para tener éxito en mi práctica en la empresa {empresa_est} basándote en esta info: {info_est}."
            
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
    st.header("🤝 Preparación de Visita")
    empresa_gest = st.selectbox("Empresa a visitar:", sorted(df['Empresa'].unique()), key="gest_emp")
    data_gest = df[df['Empresa'] == empresa_gest].iloc[0]

    st.write(f"**Estado:** {data_gest.get('ESTADO', 'Activo')}")
    
    if st.button("🤝 Generar Guion"):
        with st.spinner("Creando guion..."):
            info_gest = "\n".join([f"- {k}: {v}" for k, v in data_gest.items()])
            prompt = f"Genera un guion corto de reunión para visitar {empresa_gest} usando estos datos: {info_gest}."
            
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {e}")
