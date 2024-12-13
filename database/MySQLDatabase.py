# MySQLDatabase.py
import mysql.connector

class MySQLDatabase:
    def __init__(self, host="localhost", user="root", password="qwerty", database="daw"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conexion = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conexion = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conexion.cursor()
            print("Conexión exitosa a la base de datos.")
        except mysql.connector.Error as e:
            print(f"Error al conectar con la base de datos: {e}")

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        print("Conexión cerrada.")

    def select(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            return resultados
        except mysql.connector.Error as e:
            print(f"Error al ejecutar SELECT: {e}")
            return None

    def insert(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.conexion.commit()
            print("Inserción exitosa.")
        except mysql.connector.Error as e:
            print(f"Error al ejecutar INSERT: {e}")
            self.conexion.rollback()

    def update(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.conexion.commit()
            print("Actualización exitosa.")
        except mysql.connector.Error as e:
            print(f"Error al ejecutar UPDATE: {e}")
            self.conexion.rollback()

    def delete(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.conexion.commit()
            print("Eliminación exitosa.")
        except mysql.connector.Error as e:
            print(f"Error al ejecutar DELETE: {e}")
            self.conexion.rollback()

    def crear_usuario(self, name, user, password, mail, role):
        query = "INSERT INTO usuarios (name, user, password, mail, role) VALUES (%s, %s, %s, %s, %s)"
        params = (name, user, password, mail, role)
        self.insert(query, params)

    def consultar_usuario(self, user):
        query = "SELECT * FROM usuarios WHERE user = %s"
        return self.select(query, (user,))

    def actualizar_rol(self, user, new_role):
        query = "UPDATE usuarios SET role = %s WHERE user = %s"
        self.update(query, (new_role, user))

    def eliminar_usuario(self, user):
        query = "DELETE FROM usuarios WHERE user = %s"
        self.delete(query, (user,))
        
    def listar_usuarios(self):
        query = "SELECT * FROM usuarios"
        return self.select(query)

