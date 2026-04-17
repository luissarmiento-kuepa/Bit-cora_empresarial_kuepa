import streamlit as st
import pandas as pd
from groq import Groq

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Kuepa Insight Engine", page_icon="🎓", layout="wide")

# --- 2. CONFIGURACIÓN DE IA (GROQ) ---
try:
    if "GROQ_API_KEY" not in st.secrets:
        st.error("❌ Falta la clave 'GROQ_API_KEY' en los Secrets de Streamlit.")
        st.stop()
    
    # Inicializamos el cliente de Groq
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    # Definimos el modelo a usar
    MODELO_GROQ = "llama3-8b-8192" 
    
except Exception as e:
    st.error(f"⚠️ Error de configuración con Groq: {e}")
    st.stop()

# --- 3. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        # BITÁCORA - GOOGLE SHEETS
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        df_ent = pd.read_csv(URL, dtype=str)
        df_ent.columns = df_ent.columns.str.strip()
        
        # Buscar columna de empresa
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

# --- 4. INTERFAZ ---
st.title("🎓 Kuepa Insight Engine")
st.markdown("---")

t1, t2, t3 = st.tabs(["👨‍🏫 DOCENTES", "🎓 ESTUDIANTES", "💼 GESTORES"])

# PESTAÑA DOCENTES
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
                    prompt = f"Como experto en Kuepa, crea un reto de 15 min sobre {tema} para el programa {p_sel} usando esta info de la empresa {e_sel}: {contexto}. Responde: Reto, Herramientas y KPI. Escribe en español."
                    
                    # Llamada a Groq
                    chat_completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=MODELO_GROQ,
                    )
                    st.markdown(chat_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error de la IA: {e}")

# PESTAÑA ESTUDIANTES
with t2:
    st.header("🛡️ Guía de Práctica")
    e_est = st.selectbox("Empresa:", sorted(df['Empresa'].unique()), key="est_e")
    if st.button("🛡️ Ver Consejos"):
        try:
            prompt = f"Dame 3 consejos clave para tener éxito en mi práctica profesional en la empresa {e_est}. Escribe en español."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODELO_GROQ,
            )
            st.write(chat_completion.choices[0].message.content)
        except Exception as e: st.error(f"Error: {e}")

# PESTAÑA GESTORES
with t3:
    st.header("🤝 Guion de Visita")
    e_gest = st.selectbox("Empresa:", sorted(df['Empresa'].unique()), key="ges_e")
    if st.button("🤝 Generar Guion"):
        try:
            prompt = f"Genera un guion corto para que un gestor de Kuepa visite la empresa {e_gest} y fortalezca la relación comercial. Escribe en español."
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODELO_GROQ,
            )
            st.markdown(chat_completion.choices[0].message.content)
        except Exception as e: st.error(f"Error: {e}")
