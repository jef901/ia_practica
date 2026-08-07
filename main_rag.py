import chromadb
import ollama
from incrustador import generar_vector

def buscar_contexto(pregunta, max_resultados=1):
    """Busca en ChromaDB los fragmentos semánticamente más cercanos"""
    cliente = chromadb.PersistentClient(path="./db_vectorial")
    
    # 🛠️ CAMBIO AQUÍ: get_or_create_collection evita el error si no la encuentra
    coleccion = cliente.get_or_create_collection(name="mis_documentos")
    
    vector_pregunta = generar_vector(pregunta)
    
    resultado = coleccion.query(
        query_embeddings=[vector_pregunta],
        n_results=max_resultados
    )
    
    # Validamos que existan documentos en la lista para evitar errores de índice
    if resultado and resultado['documents'] and len(resultado['documents'][0]) > 0:
        return resultado['documents'][0]
    return "No se encontró contexto relevante."


def chat_rag():
    modelo = 'qwen2.5-coder:3b'
    print(f"🤖 Chat RAG Vectorial Activo ({modelo}).")
    print("👋 Escribe 'salir' para terminar.\n")
    
    while True:
        pregunta = input("👤 Tú: ")
        if pregunta.lower() == 'salir':
            break
            
        print("🔍 [RAG] Buscando en la base de datos vectorial...")
        contexto_privado = buscar_contexto(pregunta)
        print(f"📌 [Contexto Encontrado]: {contexto_privado}\n")
        
        # Inyectamos el conocimiento recuperado al prompt del modelo
        prompt_enriquecido = (
            f"Con base ÚNICAMENTE en este contexto privado recabado de la base de datos:\n"
            f"'{contexto_privado}'\n\n"
            f"Responde de forma concisa a la siguiente pregunta: {pregunta}"
        )
        
        print("🤖 IA: ", end="", flush=True)
        try:
            stream = ollama.chat(
                model=modelo,
                messages=[{'role': 'user', 'content': prompt_enriquecido}],
                stream=True
            )
            for chunk in stream:
                print(chunk['message']['content'], end='', flush=True)
            print("\n" + "-"*30)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    chat_rag()
