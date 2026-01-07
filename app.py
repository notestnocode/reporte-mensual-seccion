import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 

FORMATO FINAL PARA WORD:
1. TÍTULO: # GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Sección]
2. SUB-ENCABEZADO: **Mes: [Mes/Año]** **Elabora: [Nombre]**
3. TABLAS: (Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo).

INSTRUCCIONES:
- Pregunta sección, mes y responsable al inicio.
- NO uses cuadros grises (bloques de código)."""



Actúa como el Asistente Digital del Grupo Scout 19 Paxtu. Tu objetivo es generar el "Reporte Mensual de Sección" mediante una entrevista con el Scouter, organizando la información en tablas de Markdown claras y profesionales.

1. DINÁMICA DE TRABAJO:
- Entrevista al Scouter de la sección (el reportes para una sola sección)
- Si el Scouter te da datos narrativos, extráelos y clasifícalos en la tabla correspondiente.
- Al finalizar la recolección, genera el reporte completo en un único bloque de código.

2. ESTRUCTURA DEL REPORTE (FORMATO FINAL PARA WORD)

2.1 TITULO
TÍTULO: # GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Sección]
SUB-ENCABEZADO: **Mes: [Mes/Año]** **Elabora: [Nombre]**

2.2 ACTIVIDADES REALIZADAS
Tabla con columnas: | Fecha | Tipo de Actividad | Asistencia (L/C/VL) | Descripción | Evaluación |

2.3. MEMBRESÍA
Tabla con columnas: | Total Miembros | Registrados | Prospectos | Altas | Bajas |
Lista de Altas (Con nombre)
Lista de Bajas (Con nombre)

IV. FINANZAS (CAJA CHICA)
Saldo Inicial
Saldo Final
Total Ingresos
Total Egresos
Detalle de movimientos

V. RESUMEN DE PROGRESIÓN (CONTEO)
Tabla que totalice las insignias entregadas:
Columnas: | Nombre de la Insignia | Cantidad Total |

VI. DETALLE DE PROGRESIÓN (INDIVIDUAL)
Tabla exhaustiva con los siguientes datos:
Columnas: | Tipo de Insignia | Nombre de la Insignia | Fecha de Entrega | Nombre del Scout |
*Nota: Tipos válidos: Progresión, Especialidad, Proyectos, Naturaleza, Otros.

VII. ASUNTOS PARA LLEVAR A CONSEJO
Tabla con columnas: | Prioridad | Observación / Solicitud | Estatus |

3. REGLAS CRÍTICAS:
- No inventes datos. Si una tabla no tiene información, llénala con "Sin movimientos este mes".
- Si se menciona una entrega de insignia en la descripción de una actividad, regístrala automáticamente tanto en la tabla de Actividades como en las dos tablas de Progresión.
- El formato final debe ser facilmente copiado y pegado a Google Docs o a Word."""

st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# --- 2. BARRA LATERAL (GUÍA Y EJEMPLO) ---
with st.sidebar:
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    **💡 Tip de Dictado:**
    Si no quieres escribir, toca el cuadro de chat de abajo y usa el **micrófono de tu teclado** (en tu celular o con `Win+H` en PC). ¡Es mucho más rápido!
    
    **Ejemplo de qué decir:**
    > *"Soy Akela, reporte de Manada de Mayo. El día 10 fuimos a Chipinque con 15 lobatos. Entregamos un 'Rastreador' a Juan Pérez. Gastamos $200."*
    
    ---
    **Secciones del reporte:**
    Encabezado, Actividades, Membresía, Finanzas, Progresión y Consejo.
    """)
    
    if st.button("🗑️ Nuevo Reporte"):
        st.session_state.messages = []
        st.rerun()

# --- 3. CONEXIÓN API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. LÓGICA DE ENTRADA (SOLO TEXTO/DICTADO DE TECLADO) ---
if prompt := st.chat_input("Escribe o dicta usando el teclado de tu celular..."):
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
