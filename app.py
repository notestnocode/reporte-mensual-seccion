import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DEL SISTEMA ---
SYSTEM_PROMPT = """Actúa como el Asistente Digital de Sección del Grupo Scout 19 Paxtu. 
INSTRUCCIÓN DE FORMATO FINAL:
Cuando el usuario pida 'Generar reporte', entrega el contenido así:
# GRUPO 19 PAXTU - REPORTE DE SECCIÓN [Nombre de la Sección]
**Mes: [Mes y Año]** **Elabora: [Nombre de la persona que elabora]**

Tablas: Actividades, Membresía, Finanzas, Resumen Progresión, Detalle Progresión y Asuntos de Consejo.
NO uses bloques de código (fondo gris), entrega el texto directo."""

st.set_page_config(page_title="Reporte Paxtu 19", page_icon="⚜️")
st.title("🤖 Asistente de Reportes - Grupo 19 Paxtu")

# --- 2. BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Guía para el Scouter")
    st.markdown("""
    1. Cuéntale al bot los detalles del mes.
    2. Escribe **'Generar reporte'**.
    3. Usa el icono de copiado que aparecerá en el reporte o selecciona el texto.
    4. Pega en Word.
    """)
    st.divider()
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

# --- 4. INTERACCIÓN ---
if prompt := st.chat_input("Escribe los detalles aquí..."):
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
            # Si la respuesta parece ser el reporte final, añadimos una utilidad de copiado
            if "# GRUPO 19 PAXTU" in response.text:
                st.markdown(response.text)
                st.caption("👇 Copia el texto de arriba para pegarlo en Word")
                # Esta es una zona de texto que facilita el copiado masivo
                st.text_area("Copiado rápido del reporte:", value=response.text, height=200)
            else:
                st.markdown(response.text)
                
        st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error: {str(e)}")
