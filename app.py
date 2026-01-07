import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DEL SISTEMA ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

INSTRUCCIÓN DE FORMATO FINAL:
Cuando el usuario pida 'Generar reporte', entrega las tablas en formato Markdown limpio.
NO uses bloques de código (fondo gris), entrega el texto directamente en el chat.
Asegúrate de que cada tabla tenga sus encabezados claros y esté separada de la siguiente por un título en negrita.

ESTRUCTURA:
1. ENCABEZADO (Tabla 2 columnas)
2. ACTIVIDADES (Tabla: Fecha, Tipo, Asistencia, Descripción, Evaluación)
3. MEMBRESÍA (Tabla: Total, Registrados, Sin Registro, Altas/Bajas, Prospectos)
4. FINANZAS (Tabla: Concepto, Ingreso, Egreso, Saldo)
5. RESUMEN PROGRESIÓN (Tabla: Nombre Insignia, Cantidad)
6. DETALLE PROGRESIÓN (Tabla: Tipo, Nombre Insignia, Fecha, Nombre/Tótem)
7. ASUNTOS CONSEJO (Tabla: Prioridad, Observación, Estatus)"""

st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

with st.sidebar:
    st.header("📋 Instrucciones")
    st.write("1. Cuéntale al bot lo que pasó en el mes.")
    st.write("2. Escribe **'Generar reporte'** al final.")
    st.write("3. Selecciona y copia las tablas resultantes.")
    st.write("4. Pega directamente en **Word**.")
    if st.button("🗑️ Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- CONEXIÓN API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Cuéntame del mes..."):
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
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {str(e)}")
