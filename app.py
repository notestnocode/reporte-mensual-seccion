import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA (PROMPT MAESTRO) ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

INSTRUCCIÓN DE FORMATO FINAL (ESTRICTA PARA WORD):
Cuando el usuario pida 'Generar reporte', entrega el contenido así:

1. TÍTULO PRINCIPAL:
# GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Nombre de la Sección]

2. SUB-ENCABEZADO:
**Mes: [Mes y Año]** **Elabora: [Nombre de la persona que elabora]**

3. TABLAS (Markdown limpio, SIN cuadros grises/bloques de código):
- ACTIVIDADES: (Fecha, Tipo, Asistencia, Descripción, Evaluación).
- MEMBRESÍA: (Total, Registrados, Sin Registro, Altas/Bajas, Prospectos).
- FINANZAS: (Concepto, Ingreso, Egreso, Saldo).
- RESUMEN PROGRESIÓN: (Nombre de Insignia, Cantidad Total).
- DETALLE PROGRESIÓN: (Tipo, Nombre Insignia, Fecha, Nombre/Tótem).
- ASUNTOS CONSEJO: (Prioridad, Observación, Estatus).

INSTRUCCIONES DE CONVERSACIÓN:
- Pregunta primero: sección, mes/año y responsable.
- Recolecta datos de forma natural.
- NO uses bloques de código. Entrega el texto limpio para facilitar el copiado a Word."""

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Sección - Paxtu 19", page_icon="⚜️", layout="centered")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")
st.markdown("---")

# --- 3. BARRA LATERAL (GUÍA COMPLETA RESTAURADA) ---
with st.sidebar:
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **¿Cómo hablar con el bot?**
    Cuéntale los detalles del mes como una plática. No importa el orden.
    
    **Ejemplo:**
    > *"Soy Akela, reporte de Manada de Mayo. El día 10 fuimos a Chipinque con 15 lobatos. Entregamos un 'Rastreador' a Juan Pérez. Gastamos $200."*
    
    ---
    **Secciones del reporte:**
    1. **Encabezado** (Título y responsable)
    2. **Actividades** (Fechas y evaluación)
    3. **Membresía** (Altas y registros)
    4. **Finanzas** (Caja chica)
    5. **Resumen Progresión** (Conteos)
    6. **Detalle Progresión** (Nombres/Etapas)
    7. **Asuntos de Consejo** (Peticiones)
    
    ---
    **Instrucciones de Copiado:**
    1. Al terminar escribe: **'Generar reporte'**.
    2. Aparecerá un cuadro de **'Copiado Rápido'** al final.
    3. Copia ese texto y pégalo directamente en **Word**.
    """)
    
    st.divider()
    if st.button("🗑️ Limpiar y Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CONEXIÓN API ---
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

# --- 6. INTERACCIÓN Y LÓGICA DE COPIADO ---
if prompt := st.chat_input("Cuéntame sobre el mes de la sección..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with
