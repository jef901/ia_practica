from ddgs import DDGS

def buscar_en_internet(consulta, max_resultados=3):
    """Busca en la web y devuelve un texto resumido con los hallazgos"""
    print(f"🔍 [Buscador] Navegando en internet para: '{consulta}'...")
    try:
        with DDGS() as ddgs:
            resultados = ddgs.text(consulta, max_results=max_resultados)
            if not resultados:
                return "No se encontraron resultados en internet."
            
            # Formateamos los resultados en un texto limpio para la IA
            texto_resultados = "Resultados encontrados en internet:\n"
            for i, r in enumerate(resultados):
                texto_resultados += f"\n--- Resultado {i+1} ---\n"
                texto_resultados += f"Título: {r['title']}\n"
                texto_resultados += f"Resumen: {r['body']}\n"
                texto_resultados += f"Enlace: {r['href']}\n"
            return texto_resultados
    except Exception as e:
        return f"⚠️ Error al buscar en internet: {e}"
