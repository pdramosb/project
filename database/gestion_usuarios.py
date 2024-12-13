from MySQLDatabase import MySQLDatabase
import hashlib

def menu():
    db = MySQLDatabase(database="daw")  # Asegúrate de poner el nombre correcto de tu base de datos
    while True:
        print("\nGestión de Usuarios")
        print("1. Crear usuario")
        print("2. Consultar usuario")
        print("3. Cambiar rol")
        print("4. Eliminar usuario")
        print("5. Listar todos los usuarios")
        print("6. Salir")
        
        opcion = input("Elige una opción: ")
        
        if opcion == "1":
            name = input("Nombre: ")
            user = input("Usuario: ")
            password = input("Contraseña: ")
            # Convertir la contraseña a MD5
            password_md5 = hashlib.md5(password.encode()).hexdigest()
            mail = input("Correo: ")
            role = input("Rol (attack/scan): ")
            db.crear_usuario(name, user, password_md5, mail, role)
        
        elif opcion == "2":
            user = input("Introduce el usuario a consultar: ")
            resultado = db.consultar_usuario(user)
            if resultado:
                for row in resultado:
                    print(f"ID: {row[0]}, Nombre: {row[1]}, Usuario: {row[2]}, Contraseña: {row[3]}, Mail: {row[4]}, Rol: {row[5]}")
            else:
                print("Usuario no encontrado.")
        
        elif opcion == "3":
            user = input("Introduce el usuario a cambiar de rol: ")
            new_role = input("Nuevo rol (attack/scan): ")
            db.actualizar_rol(user, new_role)
        
        elif opcion == "4":
            user = input("Introduce el usuario a eliminar: ")
            db.eliminar_usuario(user)
        
        elif opcion == "5":
            # Llamar a la función listar_usuarios para obtener todos los usuarios
            usuarios = db.listar_usuarios()
            if usuarios:
                print("\nLista de todos los usuarios:")
                for usuario in usuarios:
                    print(f"ID: {usuario[0]}, Nombre: {usuario[1]}, Usuario: {usuario[2]}, Mail: {usuario[4]}, Rol: {usuario[5]}")
            else:
                print("No hay usuarios en la base de datos.")
        
        elif opcion == "6":
            db.close()
            print("Saliendo...")
            break

        else:
            print("Opción no válida, intenta nuevamente.")

if __name__ == "__main__":
    menu()

