import os
import json
import ollama

ARCHIVO_MEMORIA = "historial_chat.json"

def cargar_historial():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                print("📂 ¡Memoria persistente encontrada! Cargando conversación anterior...\n")
                return json.load(f)
        except Exception as e:
            print(f"⚠️ No se pudo leer el historial ({e}). Empezando chat nuevo.")
    
    return [
        {'role': 'system', 'content': 'Eres un asistente experto en programación en Python. Responde en español, sé conciso y explica tus correcciones de forma clara.'}
    ]

def guardar_historial(historial):
    try:
        with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
        print("\n💾 Conversación guardada exitosamente.")
    except Exception as e:
        print(f"\n❌ Error al guardar el archivo: {e}")

def chat_con_analisis():
    modelo = 'qwen2.5-coder:3b'
    historial_mensajes = cargar_historial()
    
    print(f"🤖 Conectado a {modelo}.")
    print("💡 Comando especial: Escribe '/analizar nombre_archivo.py' para revisar código local.")
    print("👋 Escribe 'salir' para terminar y guardar.\n")
    
    while True:
        prompt = input("👤 Tú: ")
        if prompt.lower() == 'salir':
            guardar_historial(historial_mensajes)
            print("¡Nos vemos!")
            break
        
        if not prompt.strip():
            continue
            
        # 🔍 DETECTAR COMANDO ESPECIAL DE AGENTE (/analizar)
        if prompt.startswith("/analizar "):
            nombre_archivo = prompt.split(" ", 1)[1].strip()
            
            # Comprobamos si el archivo realmente existe en la carpeta
            if os.path.exists(nombre_archivo):
                try:
                    with open(nombre_archivo, "r", encoding="utf-8") as f:
                        codigo_contenido = f.read()
                    
                    # Transformamos tu prompt en una instrucción técnica inyectando el código leído
                    prompt = f"Por favor, analiza el siguiente archivo llamado '{nombre_archivo}', busca errores, bugs o malas prácticas, y explícame cómo mejorarlo:\n\n```python\n{codigo_contenido}\n```"
                    print(f"📖 Leyendo y enviando '{nombre_archivo}' a la IA...")
                except Exception as e:
                    print(f"❌ Error al leer el archivo {nombre_archivo}: {e}")
                    continue
            else:
                print(f"❌ El archivo '{nombre_archivo}' no existe en esta carpeta. Verifica el nombre.")
                continue

        # Envío normal a la IA (con el historial acumulado)
        historial_mensajes.append({'role': 'user', 'content': prompt})
        print("🤖 IA: ", end="", flush=True)
        
        try:
            stream = ollama.chat(
                model=modelo,
                messages=historial_mensajes,
                stream=True,
            )
            
            respuesta_completa_ia = ""
            for chunk in stream:
                texto_chunk = chunk['message']['content']
                print(texto_chunk, end='', flush=True)
                respuesta_completa_ia += texto_chunk
            print("\n")
            
            historial_mensajes.append({'role': 'assistant', 'content': respuesta_completa_ia})
            
        except Exception as e:
            print(f"\n❌ Error de conexión: {e}")
            break

if __name__ == "__main__":
    chat_con_analisis()
