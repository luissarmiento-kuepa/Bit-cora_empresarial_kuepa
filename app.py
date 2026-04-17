@st.cache_data
def load_data():
    try:
        # --- 1. CARGAR BITÁCORA (Desde Google Sheets) ---
        SHEET_ID = "11S3HLgveTiMJqMWp6Ejrj2MwELbjO_wu_yWtok8F3c8"
        SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
        
        df_empresas = pd.read_csv(SHEET_URL)
        df_empresas.columns = df_empresas.columns.str.strip()
        
        # Ajustar nombre de columna de empresas
        if 'Empresas asociadas' in df_empresas.columns:
            df_empresas.rename(columns={'Empresas asociadas': 'Empresa'}, inplace=True)
        
        df_empresas.fillna("Información no disponible", inplace=True)

        # --- 2. CARGAR PROGRAMAS (Desde el archivo en GitHub) ---
        # Nota: Asegúrate de que el archivo 'programas.csv' esté en tu repositorio de GitHub
        try:
            df_programas = pd.read_csv("programas.csv", encoding='utf-8-sig')
            df_programas.columns = df_programas.columns.str.strip()
            
            # Ajustar nombre de columna de perfil si es necesario
            if 'Perfil_Del_Egresado' in df_programas.columns:
                df_programas.rename(columns={'Perfil_Del_Egresado': 'Perfil'}, inplace=True)
        except Exception as e:
            # Si falla la carga del CSV, creamos un DataFrame de emergencia para que la app no muera
            df_programas = pd.DataFrame({
                'Programa': ['General'], 
                'Perfil': ['Información no disponible'], 
                'Competencias': ['General']
            })

        # --- 3. ¡EL PASO VITAL! Retornar ambos DataFrames ---
        return df_empresas, df_programas

    except Exception as e:
        # Si algo falla a nivel general, mostramos el error en la app
        st.error(f"Error crítico cargando datos: {e}")
        return None, None
