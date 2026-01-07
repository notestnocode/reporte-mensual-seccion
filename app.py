import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA (PROMPT MAESTRO) ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

INSTRUCCIÓN DE FORMATO FINAL (ESTRICTA PARA WORD):
Cuando el usuario pida 'Generar reporte', entrega el contenido así:

1. TÍTULO PRINCIPAL (Formato Encabezado):
# GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Nombre de la Sección]

2. SUB-ENCABEZADO (En Negritas):
**Mes: [Mes y Año]** **Elabora: [Nombre de la persona que elabora]**

3. TABLAS (Markdown limpio, sin bloques de código/cuadros grises):
- ACTIVIDADES: (Fecha, Tipo, Asistencia, Descripción, Evaluación).
- MEMBRESÍA: (Total, Registrados, Sin Registro, Altas/Bajas, Prospectos).
- FINANZAS: (Concepto, Ingreso, Egreso, Saldo).
- RESUMEN PROGRESIÓN: (Nombre de Insignia, Cantidad Total).
- DETALLE PROGRESIÓN: (Tipo, Nombre Insignia, Fecha, Nombre/Tótem).
- ASUNTOS CONSEJO: (Prioridad, Observación, Estatus).

INSTRUCCIONES DE CONVERSACIÓN:
- Pregunta primero: sección, mes/año y responsable.
- Recolecta los datos de forma natural. Si mencionan una insignia en actividades, regístrala en las tablas de progresión.
- NO uses cuadros grises. Entrega el texto limpio para facilitar el copiado a Word."""

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Sección - Paxtu 19", page_icon="⚜️", layout="centered")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")
st.markdown("---")

# --- 3. BARRA LATERAL (RECUPERANDO LA GUÍA COMPLETA) ---
with st.sidebar:
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **¿Cómo hablar con el bot?**
    Cuéntale lo que pasó en el mes de forma natural, como una plática.
    
    **Ejemplo:**
    > *"Soy Akela, reporte de Manada de Enero. El día 15 fuimos a Chipinque con 12 lobatos. Entregamos un 'Rastreador' a Juan Pérez. Gastamos $200 en material."*
    
    ---
    **Secciones que incluye tu reporte:**
    1. **Encabezado:** Título oficial y responsable.
    2. **Actividades:** Fechas, asistencia y evaluación.
    3. **Membresía:** Altas, bajas y registros.
    4. **Finanzas:** Movimientos de caja chica.
    5. **Resumen Progresión:** Conteo de insignias.
    6. **Detalle Progresión:** Quién recibió qué y cuándo.
    7. **Asuntos de Consejo:** Avisos para el Grupo.
    
    ---
    **Pasos para Word:**
    1. Al terminar escribe: **'Generar reporte'**.
    2. Selecciona y copia el texto.
    3. Pega en Word (las tablas se crearán automáticamente).
    """)
    
    st.divider()
    if st.button("🗑️ Limpiar y Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CONEXIÓN API (SECRETS) ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

# --- 5. GESTIÓN DEL HISTORIAL ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. INTERACCIÓN ---
if prompt := st.chat_input("Escribe los detalles del mes aquí..."):
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
        st.error(f"Hubo un problema: {str(e)}")
