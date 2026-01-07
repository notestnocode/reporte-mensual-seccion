import streamlit as st
import google.generativeai as genai

# Configuración del Agente (Tu prompt del Grupo 19 Paxtu)
SYSTEM_PROMPT = """Actúa como el Asistente Digital del Grupo Scout 19 Paxtu. 
Tu objetivo es generar el Reporte Mensual de Sección mediante una charla.
Estructura el reporte en tablas de Markdown: Encabezado, Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo.
Al final, entrega el reporte en un bloque de código."""

st.set_page_config(page_title="Asistente Grupo 19 Paxtu", page_icon="⚜️")
st.title("🤖 Reporte de Sección - Grupo 19 Paxtu")

# --- MODIFICACIÓN PARA EL SECRET ---
# Intentamos leer la API Key desde los secretos de Streamlit
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # CAMBIO AQUÍ: Usamos el nombre técnico completo 'models/gemini-1.5-flash'
    model = genai.GenerativeModel(
        model_name='models/gemini-1.5-flash', 
        system_instruction=SYSTEM_PROMPT
    )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Dibujar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Hola, ¿listo para el reporte del mes?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # CAMBIO AQUÍ: Mejoramos el manejo del historial
        history_google = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model" # Google usa 'model', no 'assistant'
            history_google.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history_google)
        
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

except Exception as e:
    st.error(f"Hubo un error de configuración: {e}")
