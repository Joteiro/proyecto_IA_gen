"""Configuración central del asistente de reglamentos de tenis.

Todas las constantes y la carga de la API key de Gemini viven aquí para que
el notebook y la app de Streamlit compartan la misma fuente de verdad.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# --- Rutas del proyecto -------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = ROOT_DIR / "chroma_db"

# Documentos de la base de conocimiento. El orden importa: el reglamento del
# torneo es la fuente PRINCIPAL y el reglamento ITF es la fuente de RESPALDO.
DOC_TORNEO = DATA_DIR / "Normas Ranking Federado Distrito de Moncloa-Aravaca 2025-2026.pdf"
DOC_ITF = DATA_DIR / "itf-reglas-del-tenis-2026.pdf"

# Nombres de las colecciones en ChromaDB (una por reglamento).
COLLECTION_TORNEO = "reglamento_torneo_moncloa"
COLLECTION_ITF = "reglamento_itf"

# --- Modelos de Gemini --------------------------------------------------------
# gemini-2.5-flash-lite: modelo usado en clase y mejor opción del free tier de esta
# API key (los modelos 2.0 no tienen cuota gratuita y los 2.5 permiten ~20 req/día).
# Hace tool-calling de forma fiable, ideal para el agente ReAct.
CHAT_MODEL = "gemini-2.5-flash-lite"
EMBEDDING_MODEL = "models/gemini-embedding-001"

# --- Parámetros de troceado (chunking) y recuperación -------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 4


def load_api_key() -> str:
    """Carga la API key de Gemini desde el entorno o desde un archivo .env.

    `langchain-google-genai` espera la variable ``GOOGLE_API_KEY``. En el máster
    la guardamos como ``GEMINI_API_KEY``, así que aceptamos ambas y normalizamos.
    Nunca se escribe la clave en el código (buena práctica de la consigna).
    """
    # Busca un .env en la raíz del proyecto y en la carpeta de clase.
    for candidate in (ROOT_DIR / ".env", ROOT_DIR / ".env" / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            break
    else:
        load_dotenv()  # comportamiento por defecto (variables de entorno / .env local)

    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError(
            "No se encontró la API key de Gemini. Definí GOOGLE_API_KEY o "
            "GEMINI_API_KEY en un archivo .env o como variable de entorno."
        )
    # Normalizamos para que las librerías de Google la encuentren.
    os.environ["GOOGLE_API_KEY"] = key
    return key
