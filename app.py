import streamlit as st
import google.generativeai as genai

# Configuración del Agente
SYSTEM_PROMPT = """Actúa como el Asistente Digital del Grupo Scout 19 Paxtu. 
Tu objetivo es generar el Reporte Mensual de Sección mediante una charla con el Scouter.

ESTRUCTURA DEL REPORTE (Tablas Markdown):
1. Encabezado (Grupo, Sección, Mes, Emisión, Responsable).
2. Actividades (Fecha, Tipo, Asistencia L/C/VL, Descripción, Evaluación).
3. Membresía (Totales, Reg, Sin Reg, Altas/Bajas, Prospectos).
4. Finanzas (Concepto, Ingreso, Egreso, Saldo).
5. Resumen Progresión (Conteo de insignias).
6. Detalle Progresión (Tipo: Progresión/Especialidad/Proyectos/Naturaleza/Otros, Nombre Insignia, Fecha, Nombre/Tótem).
7. Asuntos de Consejo.

REGLA: Solo genera el reporte completo al final en un bloque de código cuando el usuario lo solicite."""

st.set_page_config(page_title="Asistente Grupo 19 Paxtu", page_icon="⚜️")
st.title("🤖 Reporte de Sección - Grupo 19 Paxtu")

# Configuración de API Key
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Por favor, configura la clave 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Configuración del modelo - Probamos con el nombre directo
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=SYSTEM_PROMPT
)

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Hola, ¿listo para el reporte del mes?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Convertir historial para Gemini (User -> user, Assistant -> model)
        history_for_gemini = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history_for_gemini.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history_for_gemini)
        response = chat.send_message(prompt)
        
        # Mostrar respuesta
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Guardar respuesta
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error al generar respuesta: {str(e)}")
