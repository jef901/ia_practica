import os
import json

ARCHIVO_MEMORIA = "historial_chat.json"

def cargar_historial():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                print("📂 [Memoria] Historial cargado desde el disco.")
                return json.load(f)
        except Exception as e:
            print(f"⚠️ [Memoria] No se pudo leer el archivo ({e}).")
    
    return [{
        'role': 'system', 
        'content': 'Eres un asistente experto en Python. Responde en español y pon el código dentro de ```python'
    }]

def guardar_historial(historial):
    try:
        # ✂️ HISTORIAL DESLIZABLE: Conservamos el System Prompt (posición 0)
        system_prompt = [historial[0]]
        
        # Tomamos solo los últimos 6 mensajes del intercambio real
        mensajes_recientes = historial[1:][-6:]
        
        # Fusionamos ambos bloques para crear el historial optimizado
        historial_recortado = system_prompt + mensajes_recientes
        
        with open(ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(historial_recortado, f, ensure_ascii=False, indent=2)
        print("💾 [Memoria] Conversación optimizada y guardada exitosamente.")
        
    except Exception as e:
        print(f"❌ [Memoria] Error al guardar: {e}")
