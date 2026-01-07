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
- Si mencionan insignias en actividades, regístrala automáticamente.
- NO uses bloques de código (cuadros grises)."""

st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# --- 2. BARRA LATERAL (GUÍA, EJEMPLO Y DICTADO) ---
with st.sidebar:
    st.header("🎙️ Dictado por Voz")
    st.write("Pulsa para hablar:")
    # Capturamos el audio de forma segura
    audio_data = mic_recorder(start_prompt="🔴 Iniciar Dictado", stop_prompt="⏹️ Enviar", key='recorder')
    
    st.divider()
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **¿Cómo reportar?**
    Escribe abajo o dicta aquí a la izquierda. No importa el orden.
    
    **Ejemplo de conversación:**
    * *"Hola, reporte de Tropa de octubre, por Akela."*
    * *"El día 12 acampamos en Potrero Chico. Fuimos 15 scouts."*
    * *"Entregamos la insignia de 'Rastreador' a Daniel Garza."*
    * *"Generar reporte."*

    ---
    **Secciones:** Encabezado, Actividades, Membresía, Finanzas, Progresión y Consejo.
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

# --- 4. LÓGICA DE ENTRADA (CORREGIDA) ---
user_text = st.chat_input("Escribe los detalles aquí...")
prompt = None

# Verificamos si hubo entrada por voz (validando que no sea None)
if audio_data and audio_data.get('text'):
    prompt = audio_data['text']
# Si no hay voz, revisamos si hubo entrada por texto
elif user_text:
    prompt = user_text

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        history_google = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history_google.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history_google)
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
            if "# GRUPO 19 PAXTU" in response.text:
                st.info("⬆️ Reporte detectado. Usa el cuadro de abajo para copiar:")
                st.text_area("Copiado rápido (Ctrl+A, Ctrl+C):", value=response.text, height=300)
                
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Error: {str(e)}")
