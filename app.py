import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA (FORMATO PERSONALIZADO) ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

INSTRUCCIÓN DE FORMATO FINAL (ESTRICTA):
Cuando el usuario pida 'Generar reporte', entrega el contenido de la siguiente manera:

1. TÍTULO PRINCIPAL: 
# GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Nombre de la Sección]

2. SUB-ENCABEZADO:
**Mes: [Mes y Año]** **Elabora: [Nombre de la persona que elabora]**

3. TABLAS (Sin bloques de código, solo Markdown directo):
- ACTIVIDADES: (Fecha, Tipo, Asistencia, Descripción, Evaluación).
- MEMBRESÍA: (Total, Registrados, Sin Registro, Altas/Bajas, Prospectos).
- FINANZAS: (Concepto, Ingreso, Egreso, Saldo).
- RESUMEN PROGRESIÓN: (Nombre de Insignia, Cantidad Total).
- DETALLE PROGRESIÓN: (Tipo, Nombre Insignia, Fecha, Nombre/Tótem).
- ASUNTOS CONSEJO: (Prioridad, Observación, Estatus).

INSTRUCCIONES DE CONVERSACIÓN:
- Saluda de forma Scout.
- Pregunta primero por la Sección, el Mes/Año y quién elabora para completar el encabezado.
- Recolecta el resto de los datos de forma natural.
- NO uses cuadros grises (bloques de código). Entrega el texto limpio para copiar a Word."""

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Instrucciones para Word")
    st.markdown("""
    1. Cuéntale al bot los detalles del mes.
    2. Escribe **'Generar reporte'**.
    3. Copia el resultado y pégalo en Word.
    
    *Nota: El título aparecerá grande y los datos del responsable en negritas automáticamente.*
    """)
    st.divider()
    if st.button("🗑️ Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CONEXIÓN API ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta API Key en Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. LÓGICA DE CHAT ---
if prompt := st.chat_input("Cuéntame sobre el mes de la sección..."):
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
