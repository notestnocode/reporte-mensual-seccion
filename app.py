import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA (PROMPT MAESTRO) ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 
Tu función es redactar el Reporte Mensual de Sección mediante una charla fluida con el Scouter.

REGLA CRÍTICA: 
Este reporte es EXCLUSIVAMENTE para UNA SOLA SECCIÓN. NO preguntes por otras ramas. 
Todo el contenido pertenece a la misma sección que el usuario indique al inicio.

ESTRUCTURA DEL REPORTE FINAL (Tablas Markdown):
Debes organizar la información en estas tablas independientes:
1. ENCABEZADO: (Grupo 19 Paxtu, Sección, Mes, Emisión, Responsable).
2. ACTIVIDADES: (Fecha, Tipo, Asistencia [L/S/C/R/VL], Descripción, Evaluación).
3. MEMBRESÍA: (Total, Registrados, Sin Registro, Altas/Bajas, Prospectos).
4. FINANZAS: (Concepto, Ingreso, Egreso, Saldo Caja Chica).
5. RESUMEN PROGRESIÓN: (Nombre de Insignia | Cantidad Total).
6. DETALLE PROGRESIÓN: (Tipo [Progresión, Especialidad, Proyectos, Naturaleza, Otros], Nombre Insignia, Fecha, Nombre/Tótem).
7. ASUNTOS CONSEJO: (Prioridad, Observación, Estatus).

INSTRUCCIONES DE CONVERSACIÓN:
- Saluda y pregunta: "¿Para qué sección es el reporte?" y "¿Quién lo elabora?".
- Si el usuario narra una entrega de insignia durante las actividades, regístrala automáticamente en las dos tablas de progresión.
- Si notas que faltan datos en secciones clave (Finanzas, Membresía o Consejo), pregunta amablemente antes de cerrar.
- Solo entrega el reporte completo en un bloque de código Markdown cuando el usuario diga 'Generar reporte', 'Listo' o 'Terminamos'."""

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Sección - Paxtu 19", page_icon="⚜️", layout="centered")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")
st.markdown("---")

# --- 3. BARRA LATERAL (GUÍA Y SECCIONES) ---
with st.sidebar:
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **¿Cómo hablar con el bot?**
    Cuéntale lo que pasó en el mes de forma natural. Él extraerá los datos.
    
    **Ejemplo:**
    > *"Soy Akela, reporte de Manada de Mayo. El día 10 fuimos a Chipinque con 15 lobatos. Entregamos un 'Rastreador' a Juan Pérez (KOTICK). Compramos material por $200."*
    
    ---
    **Secciones del reporte:**
    1. **Encabezado** (Datos básicos)
    2. **Actividades** (Fechas y asistencia)
    3. **Membresía** (Altas y registrados)
    4. **Finanzas** (Caja chica)
    5. **Resumen Progresión** (Conteos)
    6. **Detalle Progresión** (Nombres y fechas)
    7. **Asuntos de Consejo** (Peticiones)
    
    ---
    **Comandos:**
    * Escribe **'Generar reporte'** para finalizar.
    """)
    
    st.divider()
    if st.button("🗑️ Limpiar y Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CONEXIÓN CON API (SECRETS) ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# NOTA: Cambia 'gemini-1.5-flash' por el nombre que te funcionó si el 404 regresa.
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash', 
    system_instruction=SYSTEM_PROMPT
)

# --- 5. GESTIÓN DEL HISTORIAL ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Dibujar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. INTERACCIÓN ---
if prompt := st.chat_input("Escribe aquí los detalles del mes..."):
    # Mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Preparar historial para la API (ESTA PARTE TENÍA EL ERROR DE SANGRÍA)
        history_google = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history_google.append({"role": role, "parts": [m["content"]]})

        # Iniciar chat con memoria de contexto
        chat = model.start_chat(history=history_google)
        response = chat.send_message(prompt)
        
        # Mostrar respuesta del asistente
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Hubo un problema: {str(e)}")
