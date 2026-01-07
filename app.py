import streamlit as st
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# Configuración del Sistema
SYSTEM_PROMPT = """Actúa como el Asistente del Grupo 19 Paxtu. 
Tu objetivo es generar el Reporte Mensual mediante una charla. 
Estructura el reporte en tablas de Markdown: Encabezado, Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo."""

st.set_page_config(page_title="Asistente Paxtu", page_icon="⚜️")
st.title("🤖 Reporte de Sección - Grupo 19 Paxtu")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura GOOGLE_API_KEY en Secrets.")
    st.stop()

# Configuración forzada
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos una configuración de modelo más robusta
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Listo para el reporte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Forzamos a la API a usar la versión estable v1 para evitar el error 404
        response = model.generate_content(
            prompt,
            request_options=RequestOptions(api_version='v1')
        )
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error detectado: {str(e)}")
        st.info("Si el error persiste, genera una nueva API Key en Google AI Studio.")
