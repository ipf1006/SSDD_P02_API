import pymysql  # Para conectarse a una base de datos MySQL desde Python
import requests  # Para hacer peticiones HTTP a APIs externas (como PokéAPI)
from flask import Flask, jsonify  # Flask para crear el microservicio, jsonify para devolver respuestas en formato JSON

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)


# ---------------------------
# Ruta para acceder a la base de datos MySQL y obtener usuarios
# ---------------------------
@app.route('/api/db/listado-usuarios')
def obtener_usuarios():
    try:
        # Intentamos conectarnos a la base de datos
        conn = pymysql.connect(
            host='mysql',
            user='root',
            password='root',
            database='ssdd_p02_bd',
            cursorclass=pymysql.cursors.DictCursor
        )

        with conn:
            with conn.cursor() as cursor:
                # Ejecutamos la consulta SQL para obtener todos los usuarios
                cursor.execute("SELECT * FROM usuarios")
                usuarios = cursor.fetchall()  # Obtenemos los resultados

                return jsonify(usuarios), 200  # Los devolvemos en formato JSON

    except pymysql.MySQLError as e:
        # Excepciones relacionadas con MySQL
        return jsonify(error="Error al acceder a la base de datos", detalle=str(e)), 500

    except Exception as e:
        # Cualquier otra excepción
        return jsonify(error="Error inesperado en el servidor", detalle=str(e)), 500


@app.route('/api/db/conexion-fallida')
def conexion_fallida():
    try:
        # Intentamos conectarnos a la base de datos con parámetros erróneos
        conn = pymysql.connect(
            host='noExiste',  # Host incorrecto para simular fallo
            user='root',
            password='root',
            database='ssdd_p02_bd'
        )
    except pymysql.MySQLError as e:
        return jsonify(error="Error al conectar con la base de datos", detalle=str(e)), 504

    return jsonify(message="Conexión establecida correctamente.")


@app.route('/api/db/tabla-inexistente')
def tabla_inexistente():
    try:
        # Intentamos consultar una tabla que no existe
        conn = pymysql.connect(
            host='mysql',
            user='root',
            password='root',
            database='ssdd_p02_bd'
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tabla_no_existente")  # Esta tabla no existe
            result = cursor.fetchall()
            return jsonify(result), 200
    except pymysql.MySQLError as e:
        return jsonify(error="Tabla no encontrada en la base de datos", detalle=str(e)), 404


@app.route('/api/db/valores-duplicados')
def valores_duplicados():
    try:
        # Intentamos insertar un valor duplicado en la base de datos
        conn = pymysql.connect(
            host='mysql',
            user='root',
            password='root',
            database='ssdd_p02_bd'
        )
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO usuarios (nombre, email) VALUES ('Ignacio', 'ipf1006@alu.ubu.es')")  # Duplicado
            conn.commit()
            return jsonify(message="Usuarios insertados correctamente."), 201
    except pymysql.MySQLError as e:
        return jsonify(error="Error de inserción, valores duplicados", detalle=str(e)), 409


@app.route('/api/db/valores-nulos')
def valores_nulos():
    try:
        # Intentamos insertar valores nulos en una columna que no permite nulos
        conn = pymysql.connect(
            host='mysql',
            user='root',
            password='root',
            database='ssdd_p02_bd'
        )
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO usuarios (nombre, email) VALUES (null, null)")
            conn.commit()
            return jsonify(message="Usuario insertado correctamente."), 201
    except pymysql.MySQLError as e:
        return jsonify(error="Error de inserción, valores nulos", detalle=str(e)), 400


# ---------------------------
# Ruta para consultar un país en la API externa (RestCountries)
# ---------------------------
@app.route('/api/externa/recurso-existente')
def api_externa_recurso_existente():
    try:
        # Realizamos la solicitud HTTP a la API de RestCountries
        r = requests.get("https://restcountries.com/v3.1/name/spain")
        r.raise_for_status()  # Si la solicitud falla, lanza un error HTTP

        # Parseamos el JSON de respuesta
        data = r.json()

        # Extraemos la información relevante del JSON
        nombre = data[0]["name"]["common"]
        capital = data[0]["capital"][0] if "capital" in data[0] else "No disponible"
        bandera = data[0]["flags"]["png"]

        # Devolvemos la información relevante
        return jsonify(nombre=nombre, capital=capital, bandera=bandera), 200

    except Exception as e:
        # Capturamos el error
        return jsonify(error="Fallo en API externa", detalle=str(e)), 504


# ---------------------------
# Simular errores en una API de terceros (REST Countries)
# ---------------------------
@app.route('/api/externa/recurso-inexistente')
def api_externa_recurso_inexistente():
    try:
        # Intentamos acceder a un país que no existe
        r = requests.get("https://restcountries.com/v3.1/name/paisInexistente")
        r.raise_for_status()
    except Exception as e:
        # Capturamos el error
        return jsonify(error="Fallo en API externa", detalle=str(e)), 404


@app.route('/api/externa/solicitud-erronea')
def api_externa_solicitud_erronea():
    try:
        # Realizamos una solicitud errónea
        r = requests.get("https://restcountries.com/v3.1/alpha?codes=")
        r.raise_for_status()
    except Exception as e:
        # Capturamos el error
        return jsonify(error="Fallo en API externa", detalle=str(e)), 400


# Manejar errores inesperados
@app.errorhandler(Exception)
def handle_generic_error(error):
    return jsonify(error="Ha ocurrido un error inesperado"), 500


# Solo se ejecuta si el archivo se ejecuta directamente con "python app.py"
if __name__ == '__main__':
    # Ejecutamos la app Flask en modo debug, escuchando en todas las interfaces (útil para Docker o red local)
    app.run(debug=True, host='0.0.0.0', port=5000)
