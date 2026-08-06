import os
import re
import ollama
from memoria import cargar_historial, guardar_historial
from ejecutor import ejecutar_codigo
# 📦 Importamos nuestro nuevo superpoder web
from buscador import buscar_en_internet

def extraer_codigo(texto_ia):
    patron = r"```python(.*?)```"
    resultado = re.search(patron, texto_ia, re.DOTALL)
    return resultado.group(1).strip() if resultado else None

def iniciar_agente():
    modelo = 'qwen2.5-coder:3b'
    historial_mensajes = cargar_historial()
    
    print(f"🤖 Agente Listo ({modelo}).")
    print("💡 Comandos: '/analizar nombre.py' o '/buscar lo que quieras saber'")
    print("👋 Escribe 'salir' para terminar.\n")
    
    while True:
        prompt = input("👤 Tú: ")
        if prompt.lower() == 'salir':
            guardar_historial(historial_mensajes)
            break
        if not prompt.strip():
            continue
            
        es_comando_analizar = False
        
        # 🔍 COMANDO EXTRA: BUSQUEDA EN INTERNET
        if prompt.startswith("/buscar "):
            consulta = prompt.split(" ", 1)[1].strip()
            # 1. El script navega por internet
            datos_web = buscar_en_internet(consulta)
            # 2. Le inyectamos los datos frescos de internet al prompt de la IA
            prompt = f"El usuario quiere saber sobre '{consulta}'. Utiliza esta información obtenida de internet en tiempo real para responderle:\n\n{datos_web}"
            
        elif prompt.startswith("/analizar "):
            nombre_original = prompt.split(" ", 1)[1].strip()
            if os.path.exists(nombre_original):
                try:
                    with open(nombre_original, "r", encoding="utf-8") as f:
                        codigo_contenido = f.read()
                    prompt = f"Analiza y corrige este código. Devuelve SOLO la solución completa dentro de un bloque ```python:\n\n{codigo_contenido}"
                    print(f"📖 Leyendo '{nombre_original}'...")
                    es_comando_analizar = True
                except Exception as e:
                    print(f"❌ Error al leer: {e}")
                    continue
            else:
                print(f"❌ El archivo '{nombre_original}' no existe.")
                continue

        historial_mensajes.append({'role': 'user', 'content': prompt})
        
        intento = 0
        while intento < 3:
            print(f"🤖 IA: ", end="", flush=True)
            try:
                stream = ollama.chat(model=modelo, messages=historial_mensajes, stream=True)
                respuesta_completa_ia = ""
                for chunk in stream:
                    texto_chunk = chunk['message']['content']
                    print(texto_chunk, end='', flush=True)
                    respuesta_completa_ia += texto_chunk
                print("\n")
                
                historial_mensajes.append({'role': 'assistant', 'content': respuesta_completa_ia})
                
                if es_comando_analizar:
                    codigo_limpio = extraer_codigo(respuesta_completa_ia)
                    if codigo_limpio:
                        nombre_base, extension = os.path.splitext(nombre_original)
                        nuevo_nombre_archivo = f"{nombre_base}_corregido{extension}"
                        
                        with open(nuevo_nombre_archivo, "w", encoding="utf-8") as f:
                            f.write(codigo_limpio)
                        
                        exito, resultado_terminal = ejecutar_codigo(nuevo_nombre_archivo)
                        
                        if exito:
                            print(f"✅ ¡Éxito! Salida:\n{resultado_terminal}")
                            break
                        else:
                            print(f"⚠️ Falló en terminal. Corrigiendo...")
                            prompt_error = f"El código dio este error al ejecutarlo:\n{resultado_terminal}\nArréglalo."
                            historial_mensajes.append({'role': 'user', 'content': prompt_error})
                            intento += 1
                    else:
                        break
                else:
                    break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                break

if __name__ == "__main__":
    iniciar_agente()
