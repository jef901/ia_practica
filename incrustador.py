import chromadb
import ollama

def inicializar_base_datos():
    # Crea o conecta a la base de datos guardada en la carpeta local
    cliente = chromadb.PersistentClient(path="./db_vectorial")
    # Creamos o recuperamos la colección de documentos
    coleccion = cliente.get_or_create_collection(name="mis_documentos")
    return coleccion

def generar_vector(texto, modelo="all-minilm"):
    """Genera el embedding numérico usando Ollama"""
    respuesta = ollama.embeddings(model=modelo, prompt=texto)
    return respuesta['embedding']

def guardar_documento(id_doc, texto_contenido, metadatos=None):
    """Guarda un fragmento de texto y su vector en ChromaDB"""
    coleccion = inicializar_base_datos()
    vector = generar_vector(texto_contenido)
    
    coleccion.add(
        embeddings=[vector],
        documents=[texto_contenido],
        metadatas=[metadatos or {}],
        ids=[id_doc]
    )
    print(f"✨ [Vectorial] Documento '{id_doc}' indexado con éxito.")

if __name__ == "__main__":
    # Prueba rápida: Vamos a indexar dos datos de conocimiento privado
    print("🧠 Indexando conocimiento de prueba...")
    guardar_documento(
        id_doc="doc_1", 
        texto_contenido="El proyecto secreto de Jef se llama Alfa y utiliza Python avanzado con WSL 2.",
        metadatos={"origen": "manual"}
    )
    guardar_documento(
        id_doc="doc_2", 
        texto_contenido="La contraseña del servidor de desarrollo local es 'DesarrolloLocal2026!'.",
        metadatos={"origen": "manual"}
    )
