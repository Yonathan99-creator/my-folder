import mysql.connector
from faker import Faker
import random
from datetime import datetime, timedelta

# Configuración de la conexión a MySQL
config = {
    'user': 'root',
    'password': '12345678',
    'host': 'localhost',
    'database': 'suplementos_db'
}

# Conectar a la base de datos
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

fake = Faker()

# Insertar datos en la tabla 'usuarios'
print("Insertando datos en la tabla usuarios...")
for _ in range(500):
    nombre = fake.first_name()
    apellido = fake.last_name()
    email = fake.email()
    telefono = fake.phone_number()
    direccion = fake.address()
    password = fake.password()
    cursor.execute("INSERT INTO usuarios (nombre, apellido, email, telefono, direccion, password) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (nombre, apellido, email, telefono, direccion, password))

# Obtener IDs de usuarios generados
conn.commit()
cursor.execute("SELECT id FROM usuarios")
usuarios_ids = [row[0] for row in cursor.fetchall()]

# Insertar datos en la tabla 'productos'
print("Insertando datos en la tabla productos...")
categorias = ['proteina', 'mass', 'amino', 'creatina']
estados = ['activo', 'inactivo']
for _ in range(500):
    nombre = fake.word().capitalize()
    marca = fake.company()
    contenido = f"{random.randint(500, 3000)}g"
    ingredientes = fake.sentence()
    precio = round(random.uniform(10, 100), 2)
    stock = random.randint(1, 100)
    categoria = random.choice(categorias)
    estado = random.choice(estados)
    cursor.execute("""
        INSERT INTO productos (nombre, marca, contenido, ingredientes, precio, stock, categoria, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nombre, marca, contenido, ingredientes, precio, stock, categoria, estado))

# Obtener IDs de productos generados
conn.commit()
cursor.execute("SELECT id FROM productos")
productos_ids = [row[0] for row in cursor.fetchall()]

# Insertar datos en la tabla 'pedidos'
print("Insertando datos en la tabla pedidos...")
estados_pedido = ['pendiente', 'enviado', 'entregado', 'cancelado']
pedidos_ids = []
for _ in range(500):
    usuario_id = random.choice(usuarios_ids)
    total = round(random.uniform(100, 5000), 2)
    estado = random.choice(estados_pedido)
    cursor.execute("INSERT INTO pedidos (usuario_id, total, estado) VALUES (%s, %s, %s)", (usuario_id, total, estado))
    pedidos_ids.append(cursor.lastrowid)

# Insertar datos en la tabla 'pedido_productos'
print("Insertando datos en la tabla pedido_productos...")
for _ in range(1000):
    pedido_id = random.choice(pedidos_ids)
    producto_id = random.choice(productos_ids)
    cantidad = random.randint(1, 5)
    precio_total = cantidad * round(random.uniform(10, 100), 2)
    cursor.execute("INSERT INTO pedido_productos (pedido_id, producto_id, cantidad, precio_total) VALUES (%s, %s, %s, %s)",
                   (pedido_id, producto_id, cantidad, precio_total))

# Insertar datos en la tabla 'reseñas'
print("Insertando datos en la tabla reseñas...")
for _ in range(500):
    usuario_id = random.choice(usuarios_ids)
    producto_id = random.choice(productos_ids)
    calificacion = random.randint(1, 5)
    comentario = fake.sentence()
    fecha_resena = fake.date_between(start_date='-2y', end_date='today')
    cursor.execute("INSERT INTO resenas (usuario_id, producto_id, calificacion, comentario, fecha_resena) VALUES (%s, %s, %s, %s, %s)",
                   (usuario_id, producto_id, calificacion, comentario, fecha_resena))

# Insertar datos en la tabla 'tarjetas'
print("Insertando datos en la tabla tarjetas...")
tipos_tarjeta = ['credito', 'debito']
estados_tarjeta = ['activo', 'inactivo']

for _ in range(500):
    id_usuario = random.choice(usuarios_ids)
    numero_tarjeta = fake.credit_card_number()
    tipo_tarjeta = random.choice(tipos_tarjeta)
    titular = fake.name()
    vencimiento = fake.future_date(end_date='+5y').strftime('%m/%Y')
    cvv = str(random.randint(100, 999))
    estado = random.choice(estados_tarjeta)
    
    cursor.execute("""
        INSERT INTO tarjetas (numero_tarjeta, tipo_tarjeta, titular, vencimiento, cvv, id_usuario, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (numero_tarjeta, tipo_tarjeta, titular, vencimiento, cvv, id_usuario, estado))

# Confirmar cambios y cerrar conexión
conn.commit()
cursor.close()
conn.close()

print("Inserción completada.")
