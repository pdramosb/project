from flask import request, jsonify
from scapy.all import sniff, wrpcap
import threading

# Variables globales para gestionar la captura
capture_thread = None
captured_packets = []
capture_running = False

def start_capture(filter_enabled, filter_ip):
    """Inicia la captura de paquetes"""
    global capture_running, captured_packets
    capture_running = True
    captured_packets = []

    def packet_handler(packet):
        print(packet.summary()) 
        if filter_enabled and filter_ip:
            # Filtrar por IP de origen o destino
            if filter_ip not in (packet.src, packet.dst):
                return
        captured_packets.append(packet)

    def stop_filter(packet):
        return not capture_running

    #sniff(prn=packet_handler, store=False, stop_filter=stop_filter)
    sniff(prn=packet_handler, store=False, iface="ens33", promisc=True, stop_filter=stop_filter)


def stop_capture():
    """Detiene la captura de paquetes."""
    global capture_running
    capture_running = False

# Endpoint para iniciar la captura
def start_sniff():
    global capture_thread
    if capture_thread and capture_thread.is_alive():
        return jsonify({"success": False, "error": "La captura ya está en ejecución."}), 400

    data = request.get_json()
    filter_enabled = data.get("filterEnabled", False)
    filter_ip = data.get("filterIp", "")

    capture_thread = threading.Thread(target=start_capture, args=(filter_enabled, filter_ip))
    capture_thread.start()
    return jsonify({"success": True}), 200

# Endpoint para detener la captura
def stop_sniff():
    global capture_running, capture_thread
    capture_running = False

    if capture_thread:
        capture_thread.join()  # Esperar a que el hilo termine

    # Serializar los paquetes capturados
    packets_summary = "\n".join(packet.summary() for packet in captured_packets)
    return jsonify({"success": True, "packets": packets_summary}), 200

