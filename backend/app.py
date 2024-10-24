from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configuración del log
logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)

# Conexión con la base de datos SQLite usando la ruta absoluta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/hmelendezr1/mi_tienda_en_linea/database/tienda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de la tabla loguin
class Loguin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)  # Contraseña ya cifrada
    correo = db.Column(db.String(100), unique=True, nullable=False)
    rol = db.Column(db.String(20))  # Rol del usuario

# Log para cuando se inicie una solicitud
@app.before_request
def before_request():
    logging.info('Nueva solicitud recibida')

# Ruta para el login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    contrasena_plana = data.get('contrasena')

    # Buscar el usuario en la base de datos
    usuario = Loguin.query.filter_by(nombre_usuario=nombre_usuario).first()

    if usuario and check_password_hash(usuario.contrasena, contrasena_plana):
        logging.info(f"Usuario {nombre_usuario} ha iniciado sesión exitosamente con rol {usuario.rol}")
        return jsonify({"mensaje": "Login exitoso", "usuario": nombre_usuario, "rol": usuario.rol})
    else:
        logging.warning(f"Intento fallido de inicio de sesión para usuario {nombre_usuario}")
        return jsonify({"mensaje": "Credenciales incorrectas"}), 401

# Ruta para crear un nuevo usuario (con contraseña cifrada)
@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    nombre_usuario = data.get('nombre_usuario')
    contrasena_plana = data.get('contrasena')
    correo = data.get('correo')
    rol = data.get('rol', 'usuario')  # Por defecto, rol 'usuario'

    # Verificar si el usuario ya existe
    usuario_existente = Loguin.query.filter_by(nombre_usuario=nombre_usuario).first()
    if usuario_existente:
        logging.warning(f"Intento de crear un usuario ya existente: {nombre_usuario}")
        return jsonify({"mensaje": "El usuario ya existe"}), 400

    # Cifrar la contraseña
    contrasena_cifrada = generate_password_hash(contrasena_plana)

    nuevo_usuario = Loguin(
        nombre_usuario=nombre_usuario,
        contrasena=contrasena_cifrada,
        correo=correo,
        rol=rol
    )

    try:
        db.session.add(nuevo_usuario)
        db.session.commit()
        logging.info(f"Nuevo usuario creado: {nombre_usuario}")
        return jsonify({"mensaje": "Usuario creado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()  # Revertir cambios si hay un error
        logging.error(f"Error creando usuario {nombre_usuario}: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
