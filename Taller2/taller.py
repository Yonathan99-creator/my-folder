from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'Taller'

mysql = MySQL(app)

app.secret_key = 'mysecretkey'

def check_connection():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM Usuarios') 
            cur.close()
            print("Conexión a la base de datos MariaDB establecida correctamente.")
        except Exception as e:
            print(f"Error al conectar con la base de datos: {e}")

if __name__ == '__main__':
    check_connection()
