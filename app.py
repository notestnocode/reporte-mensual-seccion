import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA (TU NUEVO PROMPT ACTUALIZADO) ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital del Grupo Scout 19 Paxtu. Tu objetivo es generar el "Reporte Mensual de Sección" mediante una entrevista con el Scouter.

1. DINÁMICA DE TRABAJO:
- Entrevista al Scouter de la sección (el reporte es para una sola sección).
- Si el Scouter te da datos narrativos, extráelos y clasifícalos en la tabla correspondiente.
- Al finalizar la recolección, genera el reporte completo.

2. ESTRUCTURA DEL REPORTE (FORMATO PARA COPIAR A WORD/GOOGLE DOCS):

2.1 TITULO
# GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Sección]
**Mes: [Mes/Año]** **Elabora: [Nombre]**

2.2 ACTIVIDADES REALIZADAS
| Fecha | Tipo de Actividad | Asistencia (L/C/VL) | Descripción | Evaluación |
| :--- | :--- | :--- | :--- | :--- |

2.3. MEMBRESÍA
| Total Miembros | Registrados | Prospectos | Altas | Bajas |
| :--- | :--- | :--- | :--- | :--- |
- **Lista de Altas:** [Nombres]
- **Lista de Bajas:** [Nombres]

IV. FINANZAS (CAJA CHICA)
- **Saldo Inicial:** [Monto]
- **Saldo Final:** [Monto]
- **Total Ingresos:** [Monto]
- **Total Egresos:** [Monto]
- **Detalle de movimientos:** [Lista]

V. RESUMEN DE PROGRESIÓN (CONTEO)
| Nombre de la Insignia | Cantidad Total |
| :--- | :--- |

VI. DETALLE DE PROGRESIÓN (INDIVIDUAL)
| Tipo de Insignia | Nombre de la Insignia | Fecha de Entrega | Nombre del Scout |
| :--- | :--- | :--- | :--- |

VII. ASUNTOS PARA LLEVAR A CONSEJO
| Prioridad | Observación / Solicitud | Estatus |
| :--- | :--- | :--- |

3. REGLAS CRÍTICAS:
- NO uses bloques de código (fondo gris/backticks). Entrega el texto y las tablas directamente en el chat para que mantengan el formato al copiar.
- No inventes datos. Si una tabla no tiene información, llénala con "Sin movimientos este mes".
- Si se menciona una entrega de insignia en la narrativa, regístrala automáticamente en Actividades y en las dos tablas de Progresión.
- Usa fuentes en negrita y títulos claros para que Word los reconozca al pegar."""

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# --- 3. BARRA LATERAL (GUÍA Y EJEMPLO) ---
with st.sidebar:
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **💡 Tip de Dictado:**
    Usa el **micrófono de tu teclado** en el celular para dictar los detalles más rápido.

    **Ejemplo de qué decir:**
    > *"Soy Juan Perez, Jefe de la Tropa Centauros. El día 10 fuimos a Chipinque con 15 scouts. Entregamos un 'Rastreador' a Lucía Gomez. Gastamos $200."*
    
    **Secciones del reporte:**
    Encabezado, Actividades, Membresía, Finanzas, Progresión y Consejo.

    **Para finalizar:**
    Escribe **'Generar reporte'**. Luego selecciona el texto, cópialo y pégalo en Word o Google Docs.
    """)
    
    st.divider()
    if st.button("🗑️ Nuevo Reporte / Limpiar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 4. CONEXIÓN API ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clave GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. LÓGICA DE INTERACCIÓN ---
if prompt := st.chat_input("Cuéntame sobre el mes de la sección..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Preparar historial para el modelo
        history_google = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history_google.append({"role": role, "parts": [m["content"]]})

        chat = model.start_chat(history=history_google)
        response = chat.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
            
            # Si detectamos que es el reporte final, mostramos el cuadro de copiado rápido
            if "GRUPO 19 PAXTU" in response.text:
                st.info("⬆️ Reporte listo para copiar.")
                st.text_area("Copiado rápido (Selecciona todo y copia):", value=response.text, height=300)
                
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Hubo un problema: {str(e)}")
