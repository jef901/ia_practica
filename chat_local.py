import os
import re
import json
import ollama

ARCHIVO_MEMORIA = "historial_chat.json"

def cargar_historial():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                print("📂 ¡Memoria de chat cargada!\n")
                return json.load(f)
        except Exception as e:
            print(f"⚠️ No se pudo leer el historial ({e}).")
    
    return [
        {'role': 'system', 'content': 'Eres un asistente experto en Python. Responde en español. Al dar código corregido, ponlo SIEMPRE dentro de un bloque de código markdown con ```python'}
    ]

def guardar_historial(historial):
    try:
        with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Error al guardar historial: {e}")

def extraer_codigo(texto_ia):
    """Busca el bloque de código limpio generado por la IA"""
    patron = r"```python(.*?)```"
    resultado = re.search(patron, texto_ia, re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return None

def chat_con_escritura():
    modelo = 'qwen2.5-coder:3b'
    historial_mensajes = cargar_historial()
    
    print(f"🤖 Conectado a {modelo}.")
    print("💡 Comando: '/analizar nombre_archivo.py' (Creará un archivo '_corregido.py')")
    print("👋 Escribe 'salir' para terminar.\n")
    
    while True:
        prompt = input("👤 Tú: ")
        if prompt.lower() == 'salir':
            guardar_historial(historial_mensajes)
            print("¡Nos vemos!")
            break
        
        if not prompt.strip():
            continue
            
        es_comando_analizar = False
        nombre_original = ""
        
        if prompt.startswith("/analizar "):
            nombre_original = prompt.split(" ", 1)[1].strip()
            if os.path.exists(nombre_original):
                try:
                    with open(nombre_original, "r", encoding="utf-8") as f:
                        codigo_contenido = f.read()
                    prompt = f"Analiza este código del archivo '{nombre_original}'. Busca errores, corrígelos y devuélveme el script completo y corregido dentro de un bloque ```python:\n\n{codigo_contenido}"
                    print(f"📖 Leyendo '{nombre_original}'...")
                    es_comando_analizar = True
                except Exception as e:
                    print(f"❌ Error al leer: {e}")
                    continue
            else:
                print(f"❌ El archivo '{nombre_original}' no existe.")
                continue

        historial_mensajes.append({'role': 'user', 'content': prompt})
        print("🤖 IA: ", end="", flush=True)
        
        try:
            stream = ollama.chat(model=modelo, messages=historial_mensajes, stream=True)
            respuesta_completa_ia = ""
            for chunk in stream:
                texto_chunk = chunk['message']['content']
                print(texto_chunk, end='', flush=True)
                respuesta_completa_ia += texto_chunk
            print("\n")
            
            historial_mensajes.append({'role': 'assistant', 'content': respuesta_completa_ia})
            
            # ✍️ SI FUE UN COMANDO /ANALIZAR, ESCRIBIMOS EL ARCHIVO NUEVO
            if es_comando_analizar:
                codigo_limpio = extraer_codigo(respuesta_completa_ia)
                if codigo_limpio:
                    # Creamos el nuevo nombre (ej: codigo_roto_corregido.py)
                    nombre_base, extension = os.path.splitext(nombre_original)
                    nuevo_nombre_archivo = f"{nombre_base}_corregido{extension}"
                    
                    with open(nuevo_nombre_archivo, "w", encoding="utf-8") as f:
                        f.write(codigo_limpio)
                    print(f"✨ ¡Agente actuó! Código limpio guardado automáticamente en: '{nuevo_nombre_archivo}'\n")
                else:
                    print("⚠️ La IA no devolvió un bloque de código válido para extraer.")
                    
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    chat_con_escritura()
