import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template, jsonify, send_file, request, current_app
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'

def docs_page(email):
    """
    Genera y renderiza la página de documentación.

    Argumentos:
    email -- Dirección de correo que se mostrará en la página.

    Retorna:
    Una página HTML renderizada con el correo proporcionado.
    """
    return render_template('docs.html', email=email)


def download_resultados():
    """
    Descarga el archivo 'resultados.txt' si existe.

    Retorna:
    - El archivo como descarga adjunta si está disponible.
    - Un mensaje de error en formato JSON si el archivo no existe.
    """
    
    file_path = os.path.join(UPLOAD_FOLDER, 'resultados.txt')
    if not os.path.exists(file_path):
        return jsonify({"error": "El archivo resultados.txt no existe."}), 404
    return send_file(file_path, as_attachment=True)

def send_email_with_attachment(to_email):
    """
    Envía el archivo 'resultados.txt' como adjunto a una dirección de correo electrónico.

    Argumentos:
    to_email -- Dirección de correo electrónico a la cual se enviará el archivo.

    Retorna:
    - Un mensaje de éxito en formato JSON si el correo se envió correctamente.
    - Un mensaje de error en formato JSON si ocurrió un problema.
    """
    
    file_path = os.path.join(UPLOAD_FOLDER, 'resultados.txt')
    if not os.path.exists(file_path):
        return jsonify({"error": "El archivo resultados.txt no existe."}), 404
    
    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = current_app.config['MAIL_USERNAME']
    msg['To'] = to_email
    msg['Subject'] = 'Archivo resultados.txt'
    
    body = "Adjunto el archivo resultados.txt solicitado."
    msg.attach(MIMEText(body, 'plain'))
    
    # Adjuntar el archivo
    with open(file_path, "rb") as f:
        part = MIMEText(f.read(), 'base64', 'utf-8')
        part.add_header('Content-Disposition', 'attachment', filename='resultados.txt')
        msg.attach(part)
    
    # Conexión SMTP y envío
    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls() # Inicia conexión segura TLS.
            server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.sendmail(msg['From'], to_email, msg.as_string())# Envía el correo.
        return jsonify({"success": True, "message": "Correo enviado correctamente."})
    except Exception as e:
        # Captura cualquier error durante el envío y lo retorna en formato JSON.
        return jsonify({"error": str(e)}), 500

