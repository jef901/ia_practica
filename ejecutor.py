import subprocess

def ejecutar_codigo(nombre_archivo):
    """Ejecuta un archivo Python y devuelve (exito, salida_o_error)"""
    try:
        resultado = subprocess.run(
            ["python3", nombre_archivo],
            capture_output=True,
            text=True,
            timeout=5
        )
        if resultado.returncode == 0:
            return True, resultado.stdout
        else:
            return False, resultado.stderr
    except Exception as e:
        return False, str(e)
