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
6. Detalle Progresión (Tipo, Nombre Insignia, Fecha, Nombre/Tótem).
7. Asuntos de Consejo.

Al final, entrega el reporte en un bloque de código Markdown cuando el usuario diga 'Listo' o 'Generar'."""

st.set_page_config(page_title="Asistente Grupo 19 Paxtu", page_icon="⚜️")
st.title("🤖 Reporte de Sección - Grupo 19 Paxtu v0.0.14")

# Configuración de API Key
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura la clave 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# INSTRUCCIÓN CLAVE: Usamos 'gemini-1.5-flash-latest' para forzar la versión más compatible
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash-latest',
    system_instruction=SYSTEM_PROMPT
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Hola, ¿listo para el reporte del mes?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Simplificamos el envío del mensaje sin usar start_chat para evitar el error 404 de historial
        # Pasamos el contexto del historial manualmente
        contexto_chat = ""
        for m in st.session_state.messages:
            contexto_chat += f"{m['role']}: {m['content']}\n"

        response = model.generate_content(contexto_chat)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error técnico: {str(e)}")
