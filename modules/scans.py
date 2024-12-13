from flask import request, jsonify
import subprocess
import os
import re


# Función para realizar escaneo ARP
def perform_arp_scan():
    try:
        # Ejecuta el comando 'arp-scan' para listar dispositivos en la red local
        result = subprocess.run(['sudo', 'arp-scan', '--localnet'], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()
        devices = []
        # Filtrar las líneas que contienen IPs
        for line in output_lines:
            if re.match(r'\d+\.\d+\.\d+\.\d+', line):  # Filtra las líneas con IPs
                devices.append(line)  # Línea completa, incluyendo IP y MAC
        return {"ips": devices}
    except Exception as e:
        return {"error": str(e)}

# Función para realizar escaneo Nmap
def perform_nmap_scan(ip):
    try:
        # Ejecuta 'nmap' en modo avanzado (-A) y sin ping (-Pn)
        result = subprocess.run(['nmap', '-A', '-Pn', ip], capture_output=True, text=True)
        return {"results": result.stdout}
    except Exception as e:
        return {"error": str(e)}
        
# Función para realizar Fuzzing
def perform_fuzzing():
    try:
        # Obtener parámetros del request
        url = request.form.get("url")
        extensions = request.form.get("extensions", "")
        dictionary = request.files.get("dictionary")

        # Validar URL
        if not url:
            return jsonify({"error": "La URL es requerida."}), 400

        # Guardar diccionario temporal si se subió
        dictionary_path = "./dictionaries/common.txt"  # Por defecto
        if dictionary:
            temp_path = os.path.join("/tmp", dictionary.filename)
            dictionary.save(temp_path)
            dictionary_path = temp_path

        # Construir comando de gobuster
        command = [
            "gobuster", "dir",
            "-u", url,
            "-w", dictionary_path
        ]
        if extensions:
            command.extend(["-x", extensions])

        # Ejecutar gobuster
        result = subprocess.run(command, capture_output=True, text=True)
        if dictionary and os.path.exists(temp_path):
            os.remove(temp_path)  # Eliminar archivo temporal

        # Retornar resultados
        return jsonify({"results": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

