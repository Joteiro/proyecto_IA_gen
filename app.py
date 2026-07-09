"""Interfaz web (Streamlit) para el asistente de reglamentos de tenis.

Ejecutar en local:      streamlit run app.py
Desplegar en la nube:   subir el repo a GitHub y conectarlo en share.streamlit.io
                        (definir GOOGLE_API_KEY en los Secrets de la app).
"""
from __future__ import annotations

import uuid

import streamlit as st

from src.agent import construir_agente, extraer_texto
from src.config import load_api_key

st.set_page_config(page_title="Asistente Reglamento de Tenis 🎾", page_icon="🎾")


@st.cache_resource(show_spinner="Indexando reglamentos y arrancando el agente…")
def get_agente():
    """Construye el agente una sola vez por sesión de servidor.

    En la nube no hay disco persistente para ChromaDB, así que indexamos en
    memoria (``persistir_chroma=False``). Los documentos son pequeños (~56 págs),
    con lo que el arranque tarda pocos segundos.
    """
    load_api_key()
    return construir_agente(persistir_chroma=False)


st.title("🎾 Asistente del Ranking Federado Moncloa-Aravaca")
st.caption(
    "Preguntá sobre el reglamento del torneo. Si algo no está en la normativa "
    "local, consulto las Reglas del Tenis de la ITF como respaldo."
)

# thread_id estable por sesión de navegador -> habilita la memoria de conversación.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Ejemplos")
    st.markdown(
        "- ¿Cómo se reparten los puntos del ranking?\n"
        "- ¿Qué pasa si no me presento a un partido?\n"
        "- ¿Cómo funciona el tie-break?\n"
        "- ¿Cuál es el plazo para disputar cada ronda?"
    )
    if st.button("🧹 Nueva conversación"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

agente = get_agente()

# Repinta el historial de la sesión.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if pregunta := st.chat_input("Escribí tu pregunta sobre el reglamento…"):
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando el reglamento…"):
            respuesta = extraer_texto(
                agente.invoke(
                    {"messages": [{"role": "user", "content": pregunta}]},
                    config={"configurable": {"thread_id": st.session_state.thread_id}},
                )["messages"][-1].content
            )
        st.markdown(respuesta)

    st.session_state.messages.append({"role": "assistant", "content": respuesta})
