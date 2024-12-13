from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_mysqldb import MySQL
import hashlib
import logging
import os
from functools import wraps
from modules.scans import perform_arp_scan, perform_nmap_scan, perform_fuzzing
from modules.attacks import bruteforce, sqlmap_attack, sqlmap_execute_database, hydra_attack
from modules.sniff import start_sniff, stop_sniff
from modules.docs import docs_page, download_resultados,  send_email_with_attachment

# Configuración inicial de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'password123'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'qwerty'
app.config['MYSQL_DB'] = 'daw'


# Configuración del servidor de correo electrónico
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Cambiar por tu servidor SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'correo@gmail.com'  # Introducir tu correo
app.config['MAIL_PASSWORD'] = 'contraseña'  # Introducir tu contraseña

# Inicialización de la conexión a MySQL
mysql = MySQL(app)

# Configuración del logging
if not os.path.exists('logs'):
    os.makedirs('logs')
if not os.path.exists('logs/userlog.txt'):
    open('logs/userlog.txt', 'w').close()

logging.basicConfig(
    filename='logs/userlog.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

UPLOAD_FOLDER = 'uploads'

# Decorador para verificar roles antes de acceder a ciertas rutas
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session or session.get('role') != role:
                return redirect(url_for('login_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Función para limpiar y recrear la carpeta uploads
def clean_uploads_folder():
    if os.path.exists(UPLOAD_FOLDER):
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)  # Eliminar archivo
    else:
        os.makedirs(UPLOAD_FOLDER)  # Crear la carpeta si no existe

# Función para crear el archivo resultados.txt
def create_resultados_file(username):
    resultados_path = os.path.join(UPLOAD_FOLDER, 'resultados.txt')
    with open(resultados_path, 'w') as file:
        file.write(f"Usuario '{username}' inició sesión.\n")

@app.route('/save-results', methods=['POST'])
def save_results():
    if 'user' not in session:
        return jsonify({"error": "Acceso no autorizado."}), 403

    try:
        data = request.get_json()
        content = data.get('content', '')

        if not content.strip():
            return jsonify({"error": "Contenido vacío."}), 400

        # Asegurarse de que el directorio exista
        os.makedirs('uploads', exist_ok=True)

        # Guardar contenido en resultados.txt
        with open('uploads/resultados.txt', 'a') as f:
            f.write(content + '\n')

        logging.info(f"Usuario '{session['user']}' guardó datos en resultados.txt.")
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Error al guardar resultados: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/docs')
def docs():
    if 'user' not in session:
        return jsonify({"error": "Acceso no autorizado."}), 403

    logging.info(f"Usuario '{session['user']}' accedió a la página de documentación.")

    return docs_page(email=session.get('mail'))

@app.route('/download/resultados', methods=['GET'])
def download():
    if 'user' not in session:
        return jsonify({"error": "Acceso no autorizado."}), 403
    logging.info(f"Usuario '{session['user']}' descargó resultados.txt.")

    return download_resultados()
    
@app.route('/send-email', methods=['POST'])
def send_email():
    if 'user' not in session:
        return jsonify({"error": "Acceso no autorizado."}), 403

    email = request.form.get('email')  # Obtener el correo del formulario
    if not email:
        return jsonify({"error": "Correo no proporcionado."}), 400

    logging.info(f"Usuario '{session['user']}' envió resultados.txt a {email}.")
    return send_email_with_attachment(to_email=email)
    
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']

        # Hasheamos la contraseña ingresada
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        # Verificamos usuario y contraseña en la base de datos
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user, mail, role FROM usuarios WHERE user = %s AND password = %s", (user, hashed_password))
        result = cursor.fetchone()
        cursor.close()

        if result:
            # Guardamos datos en la sesión
            session['user'] = result[0]
            session['mail'] = result[1]
            session['role'] = result[2]
            
            # Limpiar carpeta uploads y crear el archivo resultados.txt
            clean_uploads_folder()
            create_resultados_file(user)
            
            logging.info(f"Usuario '{user}' inició sesión.")
            return redirect(url_for('home'))
        else:
            logging.warning(f"Intento fallido de inicio de sesión para usuario '{user}'.")
            return "Usuario o contraseña incorrectos", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user' in session:
        logging.info(f"Usuario '{session['user']}' cerró sesión.")
        # Limpiar la carpeta uploads
        clean_uploads_folder()
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    logging.info(f"Usuario '{session['user']}' accedió a la página principal.")
    return render_template('index.html', role=session.get('role'))

@app.route('/scans', methods=['GET', 'POST'])
def scans_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        logging.info(f"Usuario '{session['user']}' realizó un escaneo ARP.")
        return jsonify(perform_arp_scan())
    logging.info(f"Usuario '{session['user']}' accedió a la página de escaneos.")
    return render_template('scans.html')

@app.route('/scans/nmap', methods=['POST'])
def nmap_scan():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    data = request.get_json()
    ip = data.get("ip")
    if not ip:
        return jsonify({"error": "No IP provided"}), 400
    
    logging.info(f"Usuario '{session['user']}' realizó un escaneo Nmap al IP: {ip}.")
    return jsonify(perform_nmap_scan(ip))

@app.route('/scans/fuzzing', methods=['POST'])
def fuzzing():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    logging.info(f"Usuario '{session['user']}' realizó un escaneo de fuzzing.")
    return perform_fuzzing()

@app.route('/attacks')
@role_required('attack')
def attacks_page():
    logging.info(f"Usuario '{session['user']}' accedió a la página de ataques.")
    return render_template('attacks.html')

@app.route('/attacks/bruteforce', methods=['POST'])
@role_required('attack')
def attack_bruteforce():
    logging.info(f"Usuario '{session['user']}' ejecutó un ataque de fuerza bruta.")
    return bruteforce()

@app.route('/attacks/sqlmap', methods=['POST'])
@role_required('attack')
def attack_sqlmap():
    logging.info(f"Usuario '{session['user']}' ejecutó un ataque SQLMap.")
    return sqlmap_attack()

@app.route('/attacks/sqlmap/database', methods=['POST'])
@role_required('attack')
def attack_sqlmap_database():
    logging.info(f"Usuario '{session['user']}' ejecutó una base de datos SQLMap.")
    return sqlmap_execute_database()

@app.route('/attacks/hydra', methods=['POST'])
@role_required('attack')
def attack_hydra():
    logging.info(f"Usuario '{session['user']}' ejecutó un ataque Hydra.")
    return hydra_attack()

@app.route('/sniff')
def sniff_page():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    logging.info(f"Usuario '{session['user']}' accedió a la página de captura de tráfico.")
    return render_template('sniff.html')

@app.route('/sniff/start', methods=['POST'])
def sniff_start():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    logging.info(f"Usuario '{session['user']}' inició la captura de tráfico.")
    return start_sniff()

@app.route('/sniff/stop', methods=['POST'])
def sniff_stop():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    logging.info(f"Usuario '{session['user']}' detuvo la captura de tráfico.")
    return stop_sniff()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

