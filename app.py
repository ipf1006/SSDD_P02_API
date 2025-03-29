from flask import Flask, jsonify # Flask para crear el microservicio, jsonify para devolver respuestas en formato JSON
import requests # Para hacer peticiones HTTP a APIs externas (como PokéAPI)
import pymysql # Para conectarse a una base de datos MySQL desde Python

# Creamos una instancia de la aplicación Flask
app = Flask(__name__)

# ---------------------------
# Ruta para simular un error en una API de terceros (PokéAPI)
# ---------------------------
@app.route('/api/pokemon')
def error_api():
    try:
        # Intentamos acceder a un Pokémon que no existe
        r = requests.get("https://pokeapi.co/api/v2/pokemon/noExiste")
        r.raise_for_status()
    except Exception as e:
        # Capturamos el error
        return jsonify(error="Fallo en API externa", detalle=str(e)), 502

# ---------------------------
# Ruta para acceder a la base de datos MySQL y obtener usuarios
# ---------------------------
@app.route('/api/usuarios')
def obtener_usuarios():
    try:
        # Conexión a la base de datos ssdd_p02_bd
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='ssdd_p02_bd',
            cursorclass=pymysql.cursors.DictCursor # Para obtener resultados como diccionarios: {'id': 1, 'nombre': 'Ignacio', 'email': 'ipf1006@alu.ubu.es'}
        )

        with conn:
            with conn.cursor() as cursor:
                # Ejecutamos una consulta SQL para obtener todos los usuarios
                cursor.execute("SELECT * FROM usuarios")
                usuarios = cursor.fetchall() # Obtenemos los resultados
                return jsonify(usuarios), 200 # Los devolvemos en formato JSON

    except Exception as e:
        # Si ocurre un error, lo devolvemos como JSON con código 500
        return jsonify(error="Error al acceder a la base de datos", detalle=str(e)), 500

# Solo se ejecuta si el archivo se ejecuta directamente con "python app.py"
if __name__ == '__main__':
    # Ejecutamos la app Flask en modo debug, escuchando en todas las interfaces (útil para Docker o red local)
    app.run(debug=True, host='0.0.0.0', port=5000)