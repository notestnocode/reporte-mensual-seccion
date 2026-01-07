import streamlit as st
import google.generativeai as genai

# Configuración del Agente (Aquí va tu prompt mejorado)
SYSTEM_PROMPT = """Actúa como el Asistente del Grupo 19 Paxtu. 
Tu objetivo es generar el Reporte Mensual mediante una charla. 
Sigue este orden: Encabezado, Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo.
Al final, genera tablas en Markdown dentro de un bloque de código y permite que el usuario lo descargue."""

st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# Configura tu API Key (La que sacaste de Google)
os_api_key = st.sidebar.text_input("Introduce la API Key de Google", type="password")

if os_api_key:
    genai.configure(api_key=os_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Cuéntame sobre las actividades del mes..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = model.generate_content(prompt)
        full_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
else:
    st.warning("Por favor, introduce tu API Key en la barra lateral para comenzar.")
