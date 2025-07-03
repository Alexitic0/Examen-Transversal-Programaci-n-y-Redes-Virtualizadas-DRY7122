from flask import Flask, request, render_template_string
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Configuración
DATABASE = 'usuarios.db'
INTEGRANTES = ['Diego', 'Brian', 'Joaquin', 'Alexis']  # Lista de integrantes del grupo

# Crear base de datos y tabla si no existen
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Agregar usuarios con contraseña hasheada
def agregar_usuario(nombre, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    hash_pw = generate_password_hash(password)
    try:
        c.execute('INSERT INTO usuarios (nombre, password_hash) VALUES (?, ?)', (nombre, hash_pw))
        conn.commit()
        print(f"Usuario agregado: {nombre}")
    except sqlite3.IntegrityError:
        print(f"Usuario ya existe: {nombre}")
    conn.close()

# Validar usuario y contraseña
def validar_usuario(nombre, password):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT password_hash FROM usuarios WHERE nombre=?', (nombre,))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], password):
        return True
    return False

# Validar usuario por comando
def validar_usuario_por_comando():
    nombre = input("Ingrese el nombre de usuario: ")
    password = input("Ingrese la contraseña: ")
    if validar_usuario(nombre, password):
        print(f"¡Bienvenido, {nombre}!")
    else:
        print("Usuario o contraseña incorrectos.")

# Inicializar base de datos y agregar integrantes
init_db()
for integrante in INTEGRANTES:
    agregar_usuario(integrante, 'Mon0nOT3chn0l@gy')  # Acá se cambia la password

# Crear app Flask
app = Flask(__name__)

# Página de login
@app.route('/', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        nombre = request.form['nombre']
        password = request.form['password']
        if validar_usuario(nombre, password):
            return f'Bienvenido, {nombre}!'
        else:
            mensaje = 'Usuario o contraseña incorrectos'
    return render_template_string('''
        <h2>Login</h2>
        <form method="post">
            Nombre: <input name="nombre"><br>
            Contraseña: <input name="password" type="password"><br>
            <input type="submit" value="Ingresar">
        </form>
        <p style="color:red;">{{mensaje}}</p>
    ''', mensaje=mensaje)

if __name__ == '__main__':
    modo = input("¿Desea iniciar el servidor web (w) o validar usuario por comando (c)? [w/c]: ")
    if modo.lower() == 'c':
        validar_usuario_por_comando()
    else:
        app.run(port=5800)
