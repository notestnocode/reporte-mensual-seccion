import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DEL SISTEMA (PROMPT OPTIMIZADO) ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

REGLA CRÍTICA: 
Este reporte es EXCLUSIVAMENTE para UNA SOLA SECCIÓN. 
NO preguntes por otras ramas (Tropa, Comunidad, Clan) ni mezcles datos. Todo el contenido pertenece a la misma sección que el usuario indique.

ESTRUCTURA DEL REPORTE FINAL (Tablas Markdown):
Debes organizar la información en estas tablas independientes:
1. ENCABEZADO: (Grupo 19 Paxtu, Sección, Mes, Emisión, Responsable).
2. ACTIVIDADES: (Fecha, Tipo, Asistencia [L/S/C/R/VL según corresponda], Descripción, Evaluación).
3. MEMBRESÍA: (Total, Registrados, Sin Registro, Altas/Bajas, Prospectos).
4. FINANZAS: (Concepto, Ingreso, Egreso, Saldo Caja Chica).
5. RESUMEN PROGRESIÓN: (Nombre de Insignia | Cantidad Total).
6. DETALLE PROGRESIÓN: (Tipo [Progresión, Especialidad, Proyectos, Naturaleza, Otros], Nombre Insignia, Fecha, Nombre/Tótem).
7. ASUNTOS CONSEJO: (Prioridad, Observación, Estatus).

INSTRUCCIONES DE CONVERSACIÓN:
- Saluda de forma Scout y pregunta: "¿Para qué sección realizaremos el reporte hoy?" y "¿Quién es el responsable?".
- Una vez definida la sección, no preguntes por otras ramas.
- Si el usuario menciona una entrega de insignia en la narrativa de actividades, regístrala automáticamente en las dos tablas de progresión.
- Sé proactivo: si faltan datos de Finanzas o Membresía, recuérdalo amablemente antes de terminar.
- Solo entrega el reporte completo en un bloque de código Markdown cuando el usuario diga 'Generar reporte', 'Listo' o 'Terminamos'."""

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Sección - Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")
st.markdown("---")

# --- CONEXIÓN CON API (SECRETS) ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: No se encontró la clave GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# NOTA: Cambia 'gemini-1.5-flash' por el nombre que te funcionó si el 404 regresa.
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT
)

# --- GESTIÓN DEL HISTORIAL DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes previos en la interfaz de Streamlit
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INTERACCIÓN CON EL USUARIO ---
if prompt := st.chat_input("Escribe aquí los detalles del mes..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Preparar historial para la API de Google
        history_google = []
        for m in st.session_state.messages[:-1]:
            # Traducir roles de Streamlit a Google Gemini
            role = "user" if m["role"] == "user" else "model"
            history_google.append({"role": role, "parts": [m["content"]]})

        # Iniciar chat con memoria de contexto
        chat = model.start_chat(history=history_google)
        response = chat.send_message(prompt)
        
        # Mostrar y guardar respuesta del asistente
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Hubo un problema al procesar el reporte: {str(e)}")
        st.info("Tip: Si el error es 404, intenta cambiar el nombre del modelo en el código.")

# --- BOTÓN DE LIMPIEZA (Opcional) ---
if st.sidebar.button("Limpiar Chat / Nuevo Reporte"):
    st.session_state.messages = []
    st.rerun()
