import os
import json
import ollama

# Nombre del archivo donde guardaremos la conversación de forma permanente
ARCHIVO_MEMORIA = "historial_chat.json"

def cargar_historial():
    """Función para LEER el archivo guardado en el disco"""
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                print("📂 ¡Memoria persistente encontrada! Cargando conversación anterior...\n")
                return json.load(f)
        except Exception as e:
            print(f"⚠️ No se pudo leer el historial ({e}). Empezando chat nuevo.")
    
    # Si el archivo no existe o falla, empezamos con el contexto base en blanco
    return [
        {'role': 'system', 'content': 'Eres un asistente de programación conciso y servicial. Responde en español y sé muy breve.'}
    ]

def guardar_historial(historial):
    """Función para ESCRIBIR el archivo en el disco"""
    try:
        with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
        print("\n💾 Conversación guardada exitosamente en 'historial_chat.json'.")
    except Exception as e:
        print(f"\n❌ Error al guardar el archivo: {e}")

def chat_persistente():
    modelo = 'qwen2.5-coder:3b'
    
    # 1. LEER: Cargamos el historial del disco duro
    historial_mensajes = cargar_historial()
    
    print(f"🤖 Conectado a {modelo}. Escribe 'salir' para terminar y guardar.\n")
    
    while True:
        prompt = input("👤 Tú: ")
        if prompt.lower() == 'salir':
            # 2. ESCRIBIR: Antes de cerrar, guardamos todo en el archivo
            guardar_historial(historial_mensajes)
            print("¡Nos vemos!")
            break
        
        if not prompt.strip():
            continue
            
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
    chat_persistente()
