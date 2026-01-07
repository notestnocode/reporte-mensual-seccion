import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import mic_recorder

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

FORMATO FINAL (ESTRICTO PARA WORD):
1. TÍTULO: # GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Sección]
2. SUB-ENCABEZADO: **Mes: [Mes/Año]** **Elabora: [Nombre]**
3. TABLAS: (Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo).

INSTRUCCIONES:
- Pregunta sección, mes y responsable al inicio.
- Si mencionan insignias en actividades, regístralas en las tablas de progresión automáticamente.
- NO uses bloques de código (cuadros grises)."""

st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# --- 2. BARRA LATERAL (GUÍA, EJEMPLO Y DICTADO) ---
with st.sidebar:
    st.header("🎙️ Dictado por Voz")
    st.write("Pulsa para hablar:")
    audio = mic_recorder(start_prompt="🔴 Iniciar Dictado", stop_prompt="⏹️ Enviar", key='recorder')
    
    st.divider()
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **¿Cómo reportar?**
    Puedes escribir o dictar los detalles del mes. No importa el orden, el bot organizará todo.
    
    **Ejemplo de conversación:**
    * *"Hola, es el reporte de la Manada de octubre, lo hace Akela."*
    * *"El día 12 tuvimos una acampada en Potrero Chico. Fuimos 15 scouts y 3 jefes. Estuvo excelente."*
    * *"Ese mismo día le entregamos la insignia de 'Rastreador' a Daniel Garza."*
    * *"Tuvimos un ingreso de $500 por cuotas y compramos piola por $150."*
    * *"Por favor, genera el reporte."*

    ---
    **Secciones incluidas:**
    Encabezado, Actividades, Membresía, Finanzas, Progresión y Consejo.
    """)
    
    if st.button("🗑️ Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- 3. CONEXIÓN API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. LÓGICA DE ENTRADA ---
user_input = st.chat_input("Escribe los detalles aquí...")
prompt = audio['text'] if audio else user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Preparar historial
        history_google = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history_google.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history_google)
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
            # Herramienta de copiado si es el reporte final
            if "# GRUPO 19 PAXTU" in response.text:
                st.info("⬆️ Reporte detectado. Usa el cuadro de abajo para copiarlo todo:")
                st.text_area("Copiado rápido (Ctrl+A, Ctrl+C):", value=response.text, height=300)
                
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error: {str(e)}")
