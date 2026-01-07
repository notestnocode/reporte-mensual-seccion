import streamlit as st
import google.generativeai as genai

st.title("Diagnóstico de Modelos Gemini")

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura la clave 'GOOGLE_API_KEY' en los Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

try:
    st.write("Buscando modelos disponibles...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.code(f"Nombre: {m.name}\nVersión: {m.version}")
except Exception as e:
    st.error(f"Error al listar modelos: {e}")
