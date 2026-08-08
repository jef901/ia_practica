import streamlit as pd
import ollama
from main_rag import buscar_contexto

# Configuración visual de la página web
pd.set_page_config(page_title="Mi RAG Local Inteligente", page_icon="🧠", layout="centered")
pd.title("🧠 Asistente de Documentación Inteligente")
pd.subheader("Consultando tu base de datos vectorial ChromaDB local")

# Crear una barra lateral interactiva
with pd.sidebar:
    pd.header("⚙️ Configuración")
    modelo = pd.selectbox("Modelo de IA:", ["qwen2.5-coder:3b"])
    pd.markdown("---")
    pd.info("📚 Los documentos de la carpeta `mis_documentos` ya están cargados en tu base vectorial local.")

# 🧠 Inicializar el historial de conversación en la memoria de la página web
if "mensajes" not in pd.session_state:
    pd.session_state.mensajes = []

# Dibujar los mensajes anteriores en la pantalla con burbujas estéticas
for msj in pd.session_state.mensajes:
    with pd.chat_message(msj["role"]):
        pd.markdown(msj["content"])

# 📥 Caja de entrada de texto inferior para tus preguntas
if pregunta := pd.chat_input("Escribe tu pregunta sobre el Instructivo aquí..."):
    # 1. Mostrar tu pregunta en la pantalla de inmediato
    with pd.chat_message("user"):
        pd.markdown(pregunta)
    pd.session_state.mensajes.append({"role": "user", "content": pregunta})
    
    # 2. Buscar en ChromaDB los fragmentos semánticos relevantes
    with pd.spinner("🔍 Buscando en la base de datos vectorial..."):
        contexto_privado = buscar_contexto(pregunta, max_resultados=3)
    
    # 3. Enviar el prompt enriquecido a Ollama y mostrar la respuesta en Streaming
    with pd.chat_message("assistant"):
        prompt_enriquecido = (
            f"Con base ÚNICAMENTE en este contexto privado recabado de la base de datos:\n"
            f"'{contexto_privado}'\n\n"
            f"Responde de forma concisa a la siguiente pregunta: {pregunta}"
        )
        
        # Streamlit maneja el streaming de Ollama de forma nativa y elegante
        contenedor_respuesta = pd.empty()
        respuesta_completa_ia = ""
        
        try:
            stream = ollama.chat(
                model=modelo,
                messages=[{'role': 'user', 'content': prompt_enriquecido}],
                stream=True
            )
            for chunk in stream:
                respuesta_completa_ia += chunk['message']['content']
                # Actualiza la interfaz en tiempo real letra por letra
                contenedor_respuesta.markdown(respuesta_completa_ia + "▌")
            contenedor_respuesta.markdown(respuesta_completa_ia)
            
            # Guardar la respuesta en el historial de sesión
            pd.session_state.mensajes.append({"role": "assistant", "content": respuesta_completa_ia})
            
        except Exception as e:
            pd.error(f"❌ Error al conectar con Ollama: {e}")
