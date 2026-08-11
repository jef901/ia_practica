import os
import streamlit as st
import ollama
from main_rag import buscar_contexto
from incrustador import escanear_e_indexar_carpeta

# Configuración visual de la página web
st.set_page_config(page_title="Mi RAG Local Inteligente", page_icon="🧠", layout="centered")
st.title("🧠 Asistente de Documentación Inteligente")
st.subheader("Consultando tu base de datos vectorial ChromaDB local")

# Directorio donde se guardan los documentos
CARPETA_DOCS = "mis_documentos"
os.makedirs(CARPETA_DOCS, exist_ok=True)

# Crear una barra lateral interactiva
with st.sidebar:
    st.header("⚙️ Configuración")
    modelo = st.selectbox("Modelo de IA:", ["qwen2.5-coder:3b"])
    
    st.markdown("---")
    st.header("📥 Subir Documentos")
    
    # 🗂️ Componente para arrastrar y soltar archivos (.txt y .docx)
    archivo_subido = st.file_uploader(
        "Selecciona un archivo para añadir al conocimiento:", 
        type=["txt", "docx", "pdf"]  # 👈 Añadido "pdf" aquí
    )
    
    if archivo_subido is not None:
        ruta_guardado = os.path.join(CARPETA_DOCS, archivo_subido.name)
        
        # Verificar si el archivo ya existe para evitar trabajo doble
        if not os.path.exists(ruta_guardado):
            with st.spinner("💾 Guardando archivo en el disco..."):
                # Escribir los bytes del archivo subido en nuestra carpeta de WSL 2
                with open(ruta_guardado, "wb") as f:
                    f.write(archivo_subido.getbuffer())
            
            st.success(f"✅ Archivo '{archivo_subido.name}' guardado.")
            
            # 🔥 Disparar automáticamente el proceso de Chunking e Indexación Vectorial
            with st.spinner("✂️ Fragmentando e indexando en ChromaDB..."):
                escanear_e_indexar_carpeta(CARPETA_DOCS)
            st.success("🧠 ¡Base de datos vectorial actualizada!")
        else:
            st.warning(f"ℹ️ El archivo '{archivo_subido.name}' ya estaba indexado.")

    st.markdown("---")
    st.info("📚 Los documentos subidos se fragmentan de forma segura y se almacenan localmente en tu base vectorial.")

# 🧠 Inicializar el historial de conversación en la memoria de la sesión web
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Dibujar los mensajes anteriores en la pantalla con burbujas estéticas
for msj in st.session_state.mensajes:
    with st.chat_message(msj["role"]):
        st.markdown(msj["content"])

# 📥 Caja de entrada de texto inferior para tus preguntas
if pregunta := st.chat_input("Escribe tu pregunta sobre tus documentos aquí..."):
    # Mostrar tu pregunta en la pantalla de inmediato
    with st.chat_message("user"):
        st.markdown(pregunta)
    st.session_state.mensajes.append({"role": "user", "content": pregunta})
    
    # Buscar en ChromaDB los fragmentos semánticos relevantes
    with st.spinner("🔍 Buscando en la base de datos vectorial..."):
        contexto_privado = buscar_contexto(pregunta, max_resultados=3)
    
    # Enviar el prompt enriquecido a Ollama y mostrar la respuesta en Streaming
    with st.chat_message("assistant"):
        prompt_enriquecido = (
            f"Con base ÚNICAMENTE en este contexto privado recabado de la base de datos:\n"
            f"'{contexto_privado}'\n\n"
            f"Responde de forma concisa a la siguiente pregunta: {pregunta}"
        )
        
        contenedor_respuesta = st.empty()
        respuesta_completa_ia = ""
        
        try:
            stream = ollama.chat(
                model=modelo,
                messages=[{'role': 'user', 'content': prompt_enriquecido}],
                stream=True
            )
            for chunk in stream:
                respuesta_completa_ia += chunk['message']['content']
                contenedor_respuesta.markdown(respuesta_completa_ia + "▌")
            contenedor_respuesta.markdown(respuesta_completa_ia)
            
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_completa_ia})
            
        except Exception as e:
            st.error(f"❌ Error al conectar con Ollama: {e}")
