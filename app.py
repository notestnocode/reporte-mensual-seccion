import streamlit as st
import google.generativeai as genai
import google.ai.generativelanguage as gapic

# 1. Configuración del Sistema
SYSTEM_PROMPT = "Actúa como el Asistente del Grupo 19 Paxtu. Ayuda a generar reportes en tablas de Markdown."

st.set_page_config(page_title="Asistente Paxtu", page_icon="⚜️")
st.title("🤖 Reporte de Sección - Grupo 19 Paxtu v0.0.2")

# 2. Configuración de API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta GOOGLE_API_KEY en Secrets.")
    st.stop()

# Forzamos la configuración de la librería
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Usamos el nombre corto, que es el más aceptado por la versión estable
model = genai.GenerativeModel('gemini-1.5-flash')

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
        # Generar contenido de forma directa sin historial complejo para evitar el 404
        response = model.generate_content(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Tip: Verifica que tu API Key sea de un proyecto con Gemini API habilitado.")
