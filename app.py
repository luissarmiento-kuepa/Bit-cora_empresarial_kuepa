import streamlit as st
import pandas as pd
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine", page_icon="🎓", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (MÁXIMA COMPATIBILIDAD) ---
try:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave 'GEMINI_API_KEY' en los Secrets de Streamlit.")
        st.stop()
    
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Intentamos con el nombre estándar. Si falla, el bloque try lo atrapará.
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
        
        # dtype=str para evitar errores con números/celdas vacías
        df_empresas = pd.read_csv(SHEET_URL, dtype=str)
        df_empresas.columns = df_empresas.columns.str.strip()
        
        # Buscador inteligente de columna 'Empresa'
        col_empresa = next((c for c in df_empresas.columns if c.lower() in ['empresa', 'empresas asociadas', 'nombre']), df_empresas.columns[0])
        df_empresas.rename(columns={col_empresa: 'Empresa'}, inplace=True)
        
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
    
    tema_clase = st.text_input("Tema de la clase:", placeholder="Ej: Excel, Servicio al Cliente...")

    if st.button("🚀 Generar Actividad"):
        if not tema_clase:
            st.warning("Escribe un tema.")
        else:
            with st.spinner("Generando contenido..."):
                try:
                    data_emp = df[df['Empresa'] == empresa_profe].iloc[0]
                    data_prog = df_prog[df_prog['Programa'] == prog_sel].iloc[0] if prog_sel in df_prog['Programa'].values else {}
                    
                    info_contexto = "\n".join([f"- {k}: {v}" for k, v in data_emp.items()])

                    prompt = f"""
                    Actúa como un Lead Instructor de Kuepa. 
                    Diseña un reto de 15 min para {prog_sel} sobre el tema {tema_clase}.
                    Usa esta info real de la empresa {empresa_profe}: {info_contexto}.
                    Responde: 1. Reto, 2. Herramientas, 3. KPI.
                    """
                    
                    # Llamada directa y limpia
                    response = model.generate_content(prompt)
                    st.success("🎯 Propuesta:")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"La IA no pudo responder. Detalles: {e}")

# ==========================================
# PESTAÑA 2: ESTUDIANTES
# ==========================================
with tab2:
    st.header("🛡️ Guía de Éxito")
    empresa_est = st.selectbox("Empresa:", sorted(df['Empresa'].unique()), key="est_emp")
    data_est = df[df['Empresa'] == empresa_est].iloc[0]
    
    st.info(f"Vestuario: {data_est.get('Código de vestimenta', 'No especifica')}")

    if st.button("🛡️ Obtener Consejos"):
        try:
            prompt = f"Dame 3 consejos para triunfar en {empresa_est}."
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# PESTAÑA 3: GESTORES
# ==========================================
with tab3:
    st.header("🤝 Visita Empresarial")
    empresa_gest = st.selectbox("Empresa:", sorted(df['Empresa'].unique()), key="gest_emp")
    
    if st.button("🤝 Generar Guion"):
        try:
            prompt = f"Dame un guion para visitar la empresa {empresa_gest}."
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
