import os
import chromadb
import ollama
from docx import Document
from pypdf import PdfReader  # 📦 Importamos el lector de PDF

def inicializar_base_datos():
    cliente = chromadb.PersistentClient(path="./db_vectorial")
    return cliente.get_or_create_collection(name="mis_documentos")

def generar_vector(texto, modelo="all-minilm"):
    respuesta = ollama.embeddings(model=modelo, prompt=texto)
    return respuesta['embedding']

def leer_txt(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        return f.read()

def leer_docx(ruta_archivo):
    doc = Document(ruta_archivo)
    parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(parrafos)

def leer_pdf(ruta_archivo):
    """Extrae texto limpio de todas las páginas de un archivo PDF"""
    lector = PdfReader(ruta_archivo)
    texto_completo = []
    for pagina in lector.pages:
        texto_pagina = pagina.extract_text()
        if texto_pagina:
            texto_completo.append(texto_pagina.strip())
    return "\n".join(texto_completo)

def dividir_en_chunks_seguros(texto, tamano_caracteres=400, solapamiento=50):
    texto_limpio = " ".join(texto.split())
    chunks = []
    inicio = 0
    while inicio < len(texto_limpio):
        fin = inicio + tamano_caracteres
        chunk = texto_limpio[inicio:fin]
        chunks.append(chunk)
        inicio += (tamano_caracteres - solapamiento)
    return chunks

def escanear_e_indexar_carpeta(ruta_carpeta="mis_documentos"):
    coleccion = inicializar_base_datos()
    
    if not os.path.exists(ruta_carpeta):
        print(f"❌ La carpeta '{ruta_carpeta}' no existe.")
        return

    archivos = os.listdir(ruta_carpeta)
    print(f"📂 [Escáner] Buscando archivos en '{ruta_carpeta}'...")

    for nombre_archivo in archivos:
        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
        texto_contenido = ""
        
        # 🔍 Añadimos la detección de formatos extendida
        if nombre_archivo.endswith(".txt"):
            texto_contenido = leer_txt(ruta_completa)
        elif nombre_archivo.endswith(".docx"):
            texto_contenido = leer_docx(ruta_completa)
        elif nombre_archivo.endswith(".pdf"):
            texto_contenido = leer_pdf(ruta_completa)
        else:
            continue

        if texto_contenido.strip():
            fragmentos = dividir_en_chunks_seguros(texto_contenido)
            print(f"📖 Procesando '{nombre_archivo}' en {len(fragmentos)} fragmentos seguros...")
            
            for idx, fragmento in enumerate(fragmentos):
                id_chunk = f"{nombre_archivo}_chunk_{idx}"
                try:
                    vector = generar_vector(fragmento)
                    coleccion.add(
                        embeddings=[vector],
                        documents=[fragmento],
                        metadatas=[{"origen": nombre_archivo, "chunk": idx}],
                        ids=[id_chunk]
                    )
                except Exception as e:
                    print(f"⚠️ Error al indexar fragmento {idx}: {e}")
                    continue
            print(f"✨ [Vectorial] Archivo '{nombre_archivo}' indexado correctamente.")

if __name__ == "__main__":
    escanear_e_indexar_carpeta()
