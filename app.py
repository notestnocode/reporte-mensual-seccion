import streamlit as st
import google.generativeai as genai

# Configuración del Sistema
SYSTEM_PROMPT = """Actúa como el Asistente Digital del Grupo Scout 19 Paxtu. 
Tu objetivo es generar el Reporte Mensual mediante una charla. 
Estructura el reporte en tablas de Markdown: Encabezado, Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo."""

st.set_page_config(page_title="Asistente Paxtu", page_icon="⚜️")
st.title("🤖 Reporte de Sección - Grupo 19 Paxtu")

# Verificación de la API Key en Secrets
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Configuración básica
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Inicializar el modelo
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar el historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto
if prompt := st.chat_input("¿Listo para empezar el reporte?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Enviamos el mensaje con el System Prompt incluido en cada llamado 
        # para asegurar que no pierda su identidad
        full_prompt = f"{SYSTEM_PROMPT}\n\nHistorial previo:\n"
        for m in st.session_state.messages[-3:]: # Enviamos solo los últimos 3 mensajes para ahorrar espacio
            full_prompt += f"{m['role']}: {m['content']}\n"
        
        response = model.generate_content(full_prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {str(e)}")
