from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.utils import secure_filename
import os
from flask_mysqldb import MySQL
from datetime import datetime
from flask import jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from flask import send_file, make_response
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


UPLOAD_FOLDER_IMAGES = 'static/imagenes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'Taller'
mysql = MySQL(app)

app.config['UPLOAD_FOLDER_PDF'] = 'static/PDF'

app.secret_key = 'mysecretkey'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para registrar la sesión del usuario
def registrar_sesion(user_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO sesion (ID_Logeado) VALUES (%s)", (user_id,))
    mysql.connection.commit()
    cur.close()

# Rutas permitidas sin comprobación de tipo
allowed_routes = ['index', 'login', 'dashboard', 'logout', 'static']

def verificar_permisos():
    if not session.get('user_id'):
        # No está autenticado
        abort(401)
    elif session['user_type'] == 2:
        # Si es un usuario de tipo 2, bloquear ciertas rutas
        blocked_routes = ['Usuarios', 'add_usuario', 'get_usuario', 'update_usuario', 'delete_usuario',
                          'Proveedores', 'add_proveedor', 'get_proveedor', 'update_proveedor', 'delete_proveedor',
                          'Inventario', 'add_inventario', 'get_inventario', 'update_inventario', 'delete_inventario',
                          'compra', 'obtener_productos', 'add_compra', 'delete_desc', 'add_producto', 
                          'bitacora', 'reimpresion_v', 'reimpresion_c',
                          'registrosventa', 
                          'registroscompra']
        if request.endpoint in blocked_routes:
            abort(403)

@app.before_request
def before_request():
    if request.endpoint and request.endpoint not in allowed_routes:
        verificar_permisos()

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('error.html', error_code=401, error_message='No estás autenticado. Inicia sesión para acceder.'), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_code=403, error_message='Acceso prohibido. No tienes permisos para esta página.'), 403

# Rutas para Login

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT usuario.ID_Usuario, persona.Nom_persona, usuario.ID_Tipo
            FROM usuario
            INNER JOIN Persona ON usuario.ID_Persona = persona.IDPersona
            WHERE Email = %s AND Contraseña = %s
        """, (email, password))
        user = cur.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_type'] = user[2]
            
            # Insertar registro en la tabla sesion
            user_id = session['user_id']
            cur.execute("""INSERT INTO sesion (ID_Logeado) VALUES (%s)""", (user_id,))
            mysql.connection.commit()
            
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas. Intenta de nuevo.', 'danger')

    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return redirect(url_for('principal'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sesion")
    mysql.connection.commit()
    cur.close()
    flash('Sesion cerrada', 'success')
    return redirect(url_for('index'))

# Ruta con relación a la pagina principal

@app.route('/Principal')
def principal():
    return render_template('Principal.html')


# Rutas con relación a usuarios

@app.route('/usuario')
def Usuarios():
    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarUsuario')
    data = cur.fetchall()

    return render_template('usuarios.html', usuarios=data)

@app.route('/add_usuario', methods=['POST', 'GET'])
def add_usuario():
    cur = mysql.connection.cursor()
    cur.execute('SELECT ID_Tipo, Tipo FROM tipos_Usu')
    tipos_usuarios = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        Nom_persona = request.form['Nom_persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Numero = request.form['Numero']
        Contraseña = request.form['Contraseña']
        ID_Tipo = request.form['ID_Tipo']

        if 'Imagen' in request.files:
            imagen = request.files['Imagen']
            if imagen.filename != '' and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))

                cur = mysql.connection.cursor()
                cur.callproc('InsertarUsuario', (Nom_persona, ApellidoP, ApellidoM, Email, Contraseña, ID_Tipo, Numero, filename))
                mysql.connection.commit()
                cur.close()

                flash('Usuario agregado correctamente', 'success')
                return redirect(url_for('Usuarios'))
            else:
                flash('Imagen no válida. Sube una imagen en formato PNG, JPG, JPEG o GIF.', 'danger')

    return render_template('formusuarios.html', tipos_usuario=tipos_usuarios)

@app.route('/edit_usuario/<id>')
def get_usuario(id):
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerUsuarioPorID', (id,))
    data = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute('SELECT ID_Tipo, Tipo FROM Tipos_Usu')
    tipos_usuarios = cur.fetchall()
    
    return render_template('edit_usuario.html', usuario=data[0], tipos_usuario=tipos_usuarios)

@app.route('/update_usuario/<int:id>', methods=['POST'])
def update_usuario(id):
    if request.method == 'POST':
        Nom_persona = request.form['Nom_persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Numero = request.form['Numero']
        Contraseña = request.form['Contraseña']
        ID_Tipo = request.form['ID_Tipo']
        nueva_imagen = request.files['Imagen']

        cur = mysql.connection.cursor()
        cur.execute('SELECT Imagen FROM Usuario WHERE ID_Persona = %s;', (id,))
        resultado = cur.fetchone()
        cur.close()

        if resultado:
            vieja_imagen = resultado[0]
        
        # Verificar si se proporcionó una nueva imagen
            if nueva_imagen.filename != '' and allowed_file(nueva_imagen.filename):
                # Borrar la vieja imagen
                if vieja_imagen:
                    vieja_imagen_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], vieja_imagen)
                    if os.path.exists(vieja_imagen_path):
                        os.remove(vieja_imagen_path)

                # Guardar la nueva imagen
                filename = secure_filename(nueva_imagen.filename)
                nueva_imagen.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))

                # Llamar al procedimiento para cambiar la imagen
                cur = mysql.connection.cursor()
                cur.callproc('EditarUsuarioConImagen', (id, Nom_persona, ApellidoP, ApellidoM, Email, Contraseña, ID_Tipo, Numero, filename))
                mysql.connection.commit()
                cur.close()

                flash('Usuario editado correctamente')
                return redirect(url_for('Usuarios'))
            else:
                # Llamar al procedimiento para cambiar la informacion sin imagen
                cur = mysql.connection.cursor()
                cur.callproc('EditarUsuarioSinImagen', (id, Nom_persona, ApellidoP, ApellidoM, Email, Contraseña, ID_Tipo, Numero))
                mysql.connection.commit()
                cur.close()

                flash('Usuario editado correctamente', 'success')
                return redirect(url_for('Usuarios'))
            
@app.route('/delete_usuario/<id>')
def delete_usuario(id):
    cur = mysql.connection.cursor()
    cur.callproc('InactivarPersona', (id,))
    mysql.connection.commit()
    cur.close()
    flash('Usuario marcado como inactivo', 'success')
    return redirect(url_for('Usuarios'))


# Rutas con relación a clientes

@app.route('/cliente')
def Clientes():
    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarCliente')
    data = cur.fetchall()

    return render_template('clientes.html', clientes=data)

@app.route('/add_cliente', methods=['POST', 'GET'])
def add_cliente():
    if request.method == 'POST':
        Nom_persona = request.form['Nom_persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Numero = request.form['Numero']

        cur = mysql.connection.cursor()
        cur.callproc('InsertarCliente', (Nom_persona, ApellidoP, ApellidoM, Email, Numero))
        mysql.connection.commit()
        flash('Cliente agregado correctamente', 'success')
        return redirect(url_for('Clientes'))

    return render_template('formclientes.html')

@app.route('/edit_cliente/<id>')
def get_cliente(id):
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerClientePorID', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('edit_cliente.html', cliente=data[0])

@app.route('/update_cliente/<int:id>', methods=['POST'])
def update_cliente(id):
    if request.method == 'POST':
        Nom_persona = request.form['Nom_persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Numero = request.form['Numero']

        cur = mysql.connection.cursor()
        cur.callproc('EditarPersona', (id, Nom_persona, ApellidoP, ApellidoM, Email, Numero))
        mysql.connection.commit()
        cur.close()
        flash('Cliente editado correctamente', 'success')
        return redirect(url_for('Clientes'))
            
@app.route('/delete_cliente/<id>')
def delete_cliente(id):
    cur = mysql.connection.cursor()
    cur.callproc('InactivarPersona', (id,))
    mysql.connection.commit()
    cur.close()
    flash('Cliente marcado como inactivo', 'success')
    return redirect(url_for('Clientes'))

# Rutas con relación a proveedores

@app.route('/proveedor')
def Proveedores():
    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarProveedores')
    data = cur.fetchall()

    return render_template('proveedores.html', proveedores=data)

@app.route('/add_proveedor', methods=['POST', 'GET'])
def add_proveedor():
    if request.method == 'POST':
        Nom_persona = request.form['Nom_persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Numero = request.form['Numero']

        cur = mysql.connection.cursor()
        cur.callproc('InsertarProveedor', (Nom_persona, ApellidoP, ApellidoM, Email, Numero))
        mysql.connection.commit()
        flash('Proveedor agregado correctamente', 'success')
        return redirect(url_for('Proveedores'))

    return render_template('formproveedores.html')

@app.route('/edit_proveedor/<id>')
def get_proveedor(id):
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerProveedorPorID', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('edit_proveedor.html', proveedor=data[0])

@app.route('/update_proveedor/<int:id>', methods=['POST'])
def update_proveedor(id):
    if request.method == 'POST':
        Nom_persona = request.form['Nom_persona']
        ApellidoP = request.form['ApellidoP']
        ApellidoM = request.form['ApellidoM']
        Email = request.form['Email']
        Numero = request.form['Numero']

        cur = mysql.connection.cursor()
        cur.callproc('EditarPersona', (id, Nom_persona, ApellidoP, ApellidoM, Email, Numero))
        mysql.connection.commit()
        cur.close()
        flash('Proveedor editado correctamente', 'success')
        return redirect(url_for('Proveedores'))
            
@app.route('/delete_proveedor/<id>')
def delete_proveedor(id):
    cur = mysql.connection.cursor()
    cur.callproc('InactivarPersona', (id,))
    mysql.connection.commit()
    cur.close()
    flash('Proveedor marcado como inactivo', 'success')
    return redirect(url_for('Proveedores'))

# Rutas con relación a inventario

@app.route('/inventario')
def Inventario():
    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarInventarioPorProveedor')
    data = cur.fetchall()

    return render_template('inventario.html', productos=data)

@app.route('/add_inventario', methods=['POST', 'GET'])
def add_inventario():
    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarProveedores')
    proveedores = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        Nom_producto = request.form['Nom_producto']
        Precio_C = request.form['Precio_C']
        ID_Proveedor = request.form['ID_Proveedor']

        if 'Imagen' in request.files:
            imagen = request.files['Imagen']
            if imagen.filename != '' and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))

                cur = mysql.connection.cursor()
                cur.callproc('InsertarInventario', (Nom_producto, Precio_C, filename, ID_Proveedor))
                mysql.connection.commit()
                cur.close()

                flash('Producto agregado correctamente', 'success')
                return redirect(url_for('Inventario'))
            else:
                flash('Imagen no válida. Sube una imagen en formato PNG, JPG, JPEG o GIF.', 'danger')

    return render_template('forminventario.html', proveedor=proveedores)

@app.route('/edit_inventario/<id>')
def get_inventario(id):
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerProductoPorID', (id,))
    data = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarProveedores')
    proveedores = cur.fetchall()
    
    return render_template('edit_inventario.html', producto=data[0], proveedor=proveedores)

@app.route('/update_inventario/<int:id>', methods=['POST'])
def update_inventario(id):
    if request.method == 'POST':
        Nom_producto = request.form['Nom_producto']
        Precio_C = request.form['Precio_C']
        Existencias = request.form['Existencias']
        nueva_imagen = request.files['Imagen']
        ID_Proveedor = request.form['ID_Proveedor']

        cur = mysql.connection.cursor()
        cur.execute('SELECT Imagen FROM inventario WHERE ID_Producto = %s;', (id,))
        resultado = cur.fetchone()
        cur.close()

        if resultado:
            vieja_imagen = resultado[0]
        
        # Verificar si se proporcionó una nueva imagen
            if nueva_imagen.filename != '' and allowed_file(nueva_imagen.filename):
                # Borrar la vieja imagen
                if vieja_imagen:
                    vieja_imagen_path = os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], vieja_imagen)
                    if os.path.exists(vieja_imagen_path):
                        os.remove(vieja_imagen_path)

                # Guardar la nueva imagen
                filename = secure_filename(nueva_imagen.filename)
                nueva_imagen.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))

                # Llamar al procedimiento para cambiar la imagen
                cur = mysql.connection.cursor()
                cur.callproc('EditarProducto', (id, Nom_producto, Precio_C, Existencias, filename, ID_Proveedor))
                mysql.connection.commit()
                cur.close()

                flash('Inventario editado correctamente', 'success')
                return redirect(url_for('Inventario'))
            else:
                # Llamar al procedimiento para cambiar la informacion sin imagen
                cur = mysql.connection.cursor()
                cur.callproc('EditarProductoSinImagen', (id, Nom_producto, Precio_C, Existencias, ID_Proveedor))
                mysql.connection.commit()
                cur.close()

                flash('Inventario editado correctamente', 'success')
                return redirect(url_for('Inventario'))
            
@app.route('/delete_inventario/<id>')
def delete_inventario(id):
    cur = mysql.connection.cursor()
    cur.callproc('InactivarProducto', (id,))
    mysql.connection.commit()
    cur.close()
    flash('Producto marcado como inactivo', 'success')
    return redirect(url_for('Inventario'))

# Rutas con relacion a compra

@app.route('/compra', methods=['GET', 'POST'])
def compra():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'agregarProducto':
            ID_Producto = request.form['ID_Producto']
            Cantidad = request.form['Cantidad']
            Precio = request.form['Precio']

            cur = mysql.connection.cursor()
            cur.callproc('InsertarCompra', (ID_Producto, Cantidad, Precio))
            mysql.connection.commit()
            cur.close()

            return redirect(url_for('compra'))

        elif action == 'terminarCompra':
            ID_Proveedor = request.form['ID_Proveedor']
            
            cur = mysql.connection.cursor()
            cur.callproc('ActualizarCompra', (ID_Proveedor))
            mysql.connection.commit()
            cur.close()
            flash('Compra realizada correctamente', 'success')
            generar_ticket()
            return redirect(url_for('compra'))
        
        elif action == 'cancelarcompra':
            cur = mysql.connection.cursor()
            cur.callproc('EliminarComprasPorEstado')
            mysql.connection.commit()
            cur.close()
            flash('Compra cancelada correctamente', 'success')
            return redirect(url_for('compra'))

    # Si es un método GET o si no se envió un formulario, renderiza la página de compra
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_Compra FROM compra WHERE Estado = 3")
    result = cur.fetchone()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('ObtenerComprasEstado')
    data = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarProveedores')
    proveedores = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('ObtenerDetallesCompraEstado')
    compra = cur.fetchall()
    cur.close()

    user_name = session.get('user_name')

    if result:
        return render_template('compra.html', CompEstado=data[0], proveedor=proveedores, detalles=compra, user_name=user_name)
    else:
        return render_template('AddCompra.html')
    
@app.route('/productos/<proveedor_id>')
def obtener_productos(proveedor_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_Producto, Nom_Producto, Precio_C FROM inventario WHERE ID_Proveedor = %s", (proveedor_id,))
    productos = cur.fetchall()
    cur.close()

    # Devolver los productos como respuesta JSON
    return jsonify(productos)
    
@app.route('/add_compra', methods=['POST'])
def add_compra():
    if request.method == 'POST':
        try:
            # Obtener el ID de usuario de la sesión
            user_id = session.get('user_id')

            if user_id:
                # Si hay un usuario en sesión, registrar la compra con su ID
                cur = mysql.connection.cursor()
                cur.callproc('RegistrarCompra', (user_id,))
                mysql.connection.commit()
                cur.close()
                flash('Compra registrada correctamente', 'success')
            else:
                flash('Usuario no autenticado', 'danger')
        except Exception as e:
            flash('Error al registrar la compra: {}'.format(str(e)), 'danger')
            mysql.connection.rollback()
    else:
        flash('Método de solicitud no permitido', 'danger')
    return redirect(url_for('compra'))

@app.route('/delete_desc/<int:id>', methods=['GET'])
def delete_desc(id):
    try:
        cur = mysql.connection.cursor()
        cur.callproc('EliminarDescCompra', (id,))
        cur.execute('SELECT 1')

        mysql.connection.commit()
        cur.close()

        flash('Producto eliminado correctamente', 'success')
    except Exception as e:
        flash('Error al eliminar el producto: {}'.format(str(e)), 'danger')
        mysql.connection.rollback()

    return redirect(url_for('compra'))

@app.route('/add_producto', methods=['POST', 'GET'])
def add_producto():
    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarProveedores')
    proveedores = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        Nom_producto = request.form['Nom_producto']
        Precio_C = request.form['Precio_C']
        ID_Proveedor = request.form['ID_Proveedor']

        if 'Imagen' in request.files:
            imagen = request.files['Imagen']
            if imagen.filename != '' and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))

                cur = mysql.connection.cursor()
                cur.callproc('InsertarInventario', (Nom_producto, Precio_C, filename, ID_Proveedor))
                mysql.connection.commit()
                cur.close()

                flash('Producto agregado correctamente', 'success')
                return redirect(url_for('compra'))
            else:
                flash('Imagen no válida. Sube una imagen en formato PNG, JPG, JPEG o GIF.', 'danger')

    return render_template('productos.html', proveedor=proveedores)

# Rutas con relacion a venta

@app.route('/venta', methods=['GET', 'POST'])
def venta():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'agregarProducto':
            ID_Producto = int(request.form['ID_Producto'])
            Cantidad = int(request.form['Cantidad'])
            Precio = float(request.form['Precio'])

            # Consulta las existencias del producto en el inventario
            cur = mysql.connection.cursor()
            cur.execute("SELECT Existencias FROM inventario WHERE ID_Producto = %s", (ID_Producto,))
            producto = cur.fetchone()
            cur.close()

            if producto and producto[0] >= Cantidad:
                cur = mysql.connection.cursor()
                cur.callproc('InsertarVenta', (ID_Producto, Cantidad, Precio))
                mysql.connection.commit()
                cur.close()

                return redirect(url_for('venta'))
            else:
                flash('Cantidad en inventario insuficiente.', 'danger')
                return redirect(url_for('venta'))

        elif action == 'terminarCompra':
            Mano = request.form['Mano']

            cur = mysql.connection.cursor()
            cur.callproc('AgregarMano', (Mano,))
            mysql.connection.commit()
            cur.close()

            ID_Cliente = request.form['ID_Cliente']

            cur = mysql.connection.cursor()
            cur.callproc('ActualizarVenta', (ID_Cliente,))
            mysql.connection.commit()
            cur.close()
            flash('Venta realizada correctamente', 'success')
            generar_ticket_v()
            return redirect(url_for('venta'))
        
        elif action == 'cancelarcompra':
            cur = mysql.connection.cursor()
            cur.callproc('EliminarVentasPorEstado')
            mysql.connection.commit()
            cur.close()
            flash('Venta cancelada correctamente', 'success')
            return redirect(url_for('venta'))
    
    # Si es un método GET o si no se envió un formulario, renderiza la página de compra
    cur = mysql.connection.cursor()
    cur.execute("SELECT ID_Venta FROM venta WHERE Estado = 3")
    result = cur.fetchone()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('ObtenerVentasEstado')
    data = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('SeleccionarClientes')
    proveedores = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.callproc('ObtenerDetallesVentaEstado')
    compra = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM inventario WHERE Estado = 1")
    productos = cur.fetchall()
    cur.close()

    user_name = session.get('user_name')

    if result:
        return render_template('venta.html', CompEstado=data[0], proveedor=proveedores, detalles=compra, producto=productos, user_name=user_name)
    else:
        return render_template('AddVenta.html')

    
@app.route('/add_venta', methods=['POST'])
def add_venta():
    if request.method == 'POST':
        try:
            # Obtener el ID de usuario de la sesión
            user_id = session.get('user_id')

            if user_id:
                # Si hay un usuario en sesión, registrar la compra con su ID
                cur = mysql.connection.cursor()
                cur.callproc('RegistrarVenta', (user_id,))
                mysql.connection.commit()
                cur.close()
                flash('venta registrada correctamente', 'success')
            else:
                flash('Usuario no autenticado', 'danger')
        except Exception as e:
            flash('Error al registrar la venta: {}'.format(str(e)), 'danger')
            mysql.connection.rollback()
    else:
        flash('Método de solicitud no permitido', 'danger')
    return redirect(url_for('venta'))

@app.route('/delete_descvent/<int:id>', methods=['GET'])
def delete_descvent(id):
    try:
        cur = mysql.connection.cursor()
        cur.callproc('EliminarDescVenta', (id,))
        cur.execute('SELECT 1')

        mysql.connection.commit()
        cur.close()

        flash('Producto eliminado correctamente', 'success')
        return redirect(url_for('venta'))
    except Exception as e:
        flash('Error al eliminar el producto: {}'.format(str(e)), 'danger')
        mysql.connection.rollback()

        return redirect(url_for('venta'))

# Ruta con relación a bitacora

@app.route('/bitacora')
def bitacora():
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerBitacoraCompleta')
    data = cur.fetchall()

    return render_template('bitacora.html', bitacora=data)    

# Rutas con relación a Registros de venta

@app.route('/registrosventa')
def registrosventa():
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerVentaHecha')
    data = cur.fetchall()

    return render_template('RegistrosVenta.html', registros=data)

# Rutas con relación a Registros de compra

@app.route('/registroscompra')
def registroscompra():
    cur = mysql.connection.cursor()
    cur.callproc('ObtenerCompraHecha')
    data = cur.fetchall()

    return render_template('RegistrosCompra.html', registros=data) 

# Rutas con relacion al ticket de compra en PDF

@app.route('/generar_ticket')
def generar_ticket():
    try:
        cur = mysql.connection.cursor()

        # Obtener el ID de compra máximo de la tabla 'compra'
        cur.execute("SELECT MAX(ID_Compra) FROM compra")
        max_id_compra = cur.fetchone()[0]

        # Obtener datos de la última compra y sus detalles
        cur.callproc('SeleccionarDatosCompraPorID', (max_id_compra,))
        
        datos_ticket = cur.fetchall()

        # Generar el PDF
        pdf_bytes = generar_pdf(max_id_compra, datos_ticket)

        if pdf_bytes:
            # Determinar el nombre del archivo
            ticket_path = next_available_filename('static/PDF/ticket', 'pdf')

            # Guardar el archivo PDF
            with open(ticket_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)

            # Insertar en la tabla 'ticket_compra'
            nombre_archivo = os.path.basename(ticket_path)
            cur.execute("""
                INSERT INTO ticket_compra (Nombre, ID_Compra)
                VALUES (%s, %s)
            """, (nombre_archivo, max_id_compra))
            mysql.connection.commit()

            # Enviar el archivo como respuesta para descarga
            return send_file(ticket_path, as_attachment=True)

        else:
            return "Error: No se generó correctamente el PDF del ticket", 500

    except Exception as e:
        print("Error al generar el ticket:", e)
        return f"Error al generar el ticket: {str(e)}", 500

    finally:
        cur.close()

def next_available_filename(base_path, extension):
    # Esta función encuentra el próximo nombre disponible para el archivo
    version = 1
    while True:
        filename = f"{base_path}_{version}.{extension}"
        if not os.path.exists(filename):
            return filename
        version += 1

# Función para generar el PDF del ticket
def generar_pdf(id_compra, datos):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Establecer fuente y tamaño para el ticket
        c.setFont("Helvetica-Bold", 14)

        # Encabezado del ticket
        c.drawCentredString(letter[0] / 2, 750, 'Ticket de Compra')

        # Línea horizontal debajo del encabezado
        c.line(50, 740, 550, 740)

        # Mostrar datos generales (solo imprimir una vez)
        if datos:
            fecha, proveedor, email_proveedor, total_general, usuario, email_usuario, *_ = datos[0]

            # Datos generales en la parte superior
            c.setFont("Helvetica", 12)
            c.drawString(50, 720, f'Fecha: {fecha}')
            c.drawString(50, 700, f'Proveedor: {proveedor}')
            c.drawString(50, 680, f'Email Proveedor: {email_proveedor}')
            c.drawString(50, 660, f'Usuario: {usuario}')
            c.drawString(50, 640, f'Email Usuario: {email_usuario}')

            # Separación antes de mostrar la tabla de detalles
            y_position = 580

            # Encabezados de la tabla
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, 'Producto')
            c.drawString(250, y_position, 'Cantidad')
            c.drawString(350, y_position, 'Precio')
            c.drawString(450, y_position, 'Total')

            y_position -= 20  # Mover la posición hacia arriba para los datos de la tabla

            # Línea horizontal encima de la tabla
            c.line(50, y_position, 550, y_position)

            # Detalles de la compra (tabla)
            for detalle in datos:
                if len(detalle) == 10:
                    _, _, _, _, _, _, producto, cantidad, precio, total = detalle
                    c.setFont("Helvetica", 12)
                    c.drawString(50, y_position - 20, producto[:30])  # Limitar longitud del producto
                    c.drawRightString(320, y_position - 20, str(cantidad))
                    c.drawRightString(420, y_position - 20, f"${precio:.2f}")
                    c.drawRightString(520, y_position - 20, f"${total:.2f}")
                    y_position -= 40  # Mover hacia arriba para la siguiente fila

            # Línea horizontal debajo de la tabla
            c.line(50, y_position - 20, 550, y_position - 20)

            # Total general
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(420, y_position - 50, 'Total General:')
            c.drawRightString(520, y_position - 50, f"${total_general:.2f}")

        # Pie de página
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, '¡Gracias por su compra!')

        c.save()

        buffer.seek(0)  # Regresar al inicio del buffer
        return buffer.getvalue()

    except Exception as e:
        print("Error al generar el PDF del ticket:", e)
        raise e  # Relanzar la excepción para identificar el problema específico

    
@app.route('/ver_ticket')
def ver_ticket():
    # Obtener el último ticket generado
    cur = mysql.connection.cursor()
    cur.execute("SELECT Nombre FROM ticket_compra ORDER BY ID_Compra DESC LIMIT 1")
    ticket_filename = cur.fetchone()

    if ticket_filename:
        # Redirigir a la página que muestra el ticket
        return redirect(url_for('mostrar_ticket', filename=ticket_filename[0]))
    else:
        return "No se encontró ningún ticket.", 404

@app.route('/mostrar_ticket/<filename>')
def mostrar_ticket(filename):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER_PDF'], filename)
    return render_template('mostrar_ticket.html', pdf_filename=filename)

# Rutas con relacion al ticket de venta en PDF

@app.route('/generar_ticket_v')
def generar_ticket_v():
    try:
        cur = mysql.connection.cursor()

        # Obtener el ID de venta máximo de la tabla 'venta'
        cur.execute("SELECT MAX(ID_Venta) FROM venta")
        max_id_venta = cur.fetchone()[0]

        # Obtener datos de la última venta y sus detalles
        cur.callproc('SeleccionarDatosVentaPorID', (max_id_venta,))
        
        datos_ticket = cur.fetchall()

        # Generar el PDF
        pdf_bytes = generar_pdf_v(max_id_venta, datos_ticket)

        if pdf_bytes:
            # Determinar el nombre del archivo
            ticket_path = next_available_filename_v('static/PDF2/ticket', 'pdf')

            # Guardar el archivo PDF
            with open(ticket_path, 'wb') as pdf_file:
                pdf_file.write(pdf_bytes)

            # Insertar en la tabla 'ticket_venta'
            nombre_archivo = os.path.basename(ticket_path)
            cur.execute("""
                INSERT INTO ticket_venta (Nombre, ID_Venta)
                VALUES (%s, %s)
            """, (nombre_archivo, max_id_venta))
            mysql.connection.commit()

            # Enviar el archivo como respuesta para descarga
            return send_file(ticket_path, as_attachment=True)

        else:
            return "Error: No se generó correctamente el PDF del ticket", 500

    except Exception as e:
        print("Error al generar el ticket:", e)
        return f"Error al generar el ticket: {str(e)}", 500

    finally:
        cur.close()

def next_available_filename_v(base_path, extension):
    # Esta función encuentra el próximo nombre disponible para el archivo
    version = 1
    while True:
        filename = f"{base_path}_{version}.{extension}"
        if not os.path.exists(filename):
            return filename
        version += 1

# Función para generar el PDF del ticket
def generar_pdf_v(id_venta, datos):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Establecer fuente y tamaño para el ticket
        c.setFont("Helvetica-Bold", 14)

        # Encabezado del ticket
        c.drawCentredString(letter[0] / 2, 750, 'Ticket de Venta')

        # Línea horizontal debajo del encabezado
        c.line(50, 740, 550, 740)

        # Mostrar datos generales (solo imprimir una vez)
        if datos:
            fecha, cliente, email_cliente, total_general, usuario, email_usuario, *_ = datos[0]

            # Datos generales en la parte superior
            c.setFont("Helvetica", 12)
            c.drawString(50, 720, f'Fecha: {fecha}')
            c.drawString(50, 700, f'Cliente: {cliente}')
            c.drawString(50, 680, f'Email Cliente: {email_cliente}')
            c.drawString(50, 660, f'Usuario: {usuario}')
            c.drawString(50, 640, f'Email Usuario: {email_usuario}')

            # Separación antes de mostrar la tabla de detalles
            y_position = 580

            # Encabezados de la tabla
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, 'Producto')
            c.drawString(250, y_position, 'Cantidad')
            c.drawString(350, y_position, 'Precio')
            c.drawString(450, y_position, 'Total')

            y_position -= 20  # Mover la posición hacia arriba para los datos de la tabla

            # Línea horizontal encima de la tabla
            c.line(50, y_position, 550, y_position)

            # Detalles de la venta (tabla)
            for detalle in datos:
                if len(detalle) == 10:
                    _, _, _, _, _, _, producto, cantidad, precio, total = detalle
                    c.setFont("Helvetica", 12)
                    c.drawString(50, y_position - 20, producto[:30])  # Limitar longitud del producto
                    c.drawRightString(320, y_position - 20, str(cantidad))
                    c.drawRightString(420, y_position - 20, f"${precio:.2f}")
                    c.drawRightString(520, y_position - 20, f"${total:.2f}")
                    y_position -= 40  # Mover hacia arriba para la siguiente fila

            # Línea horizontal debajo de la tabla
            c.line(50, y_position - 20, 550, y_position - 20)

            # Total general
            c.setFont("Helvetica-Bold", 12)
            c.drawRightString(420, y_position - 50, 'Total General:')
            c.drawRightString(520, y_position - 50, f"${total_general:.2f}")

        # Pie de página
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, '¡Gracias por su compra!')

        c.save()

        buffer.seek(0)  # Regresar al inicio del buffer
        return buffer.getvalue()

    except Exception as e:
        print("Error al generar el PDF del ticket:", e)
        raise e  # Relanzar la excepción para identificar el problema específico

    
@app.route('/ver_ticket_v')
def ver_ticket_v():
    # Obtener el último ticket generado
    cur = mysql.connection.cursor()
    cur.execute("SELECT Nombre FROM ticket_venta ORDER BY ID_Venta DESC LIMIT 1")
    ticket_filename = cur.fetchone()

    if ticket_filename:
        # Redirigir a la página que muestra el ticket
        return redirect(url_for('mostrar_ticket_v', filename=ticket_filename[0]))
    else:
        return "No se encontró ningún ticket.", 404

@app.route('/mostrar_ticket_v/<filename>')
def mostrar_ticket_v(filename):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER_PDF'], filename)
    return render_template('mostrar_ticket_v.html', pdf_filename=filename)

# Rutas con relacion de reimpresion

@app.route('/reimpresion_v/<id>')
def reimpresion_v(id):
    cur = mysql.connection.cursor()
    cur.callproc('Reimpresion_v', (id,))
    ticket_filename = cur.fetchone()

    if ticket_filename:
        # Obtener el nombre de archivo del ticket
        filename = ticket_filename[0]

        # Redirigir a la página que muestra el ticket con el filename obtenido
        return redirect(url_for('mostrar_ticket_v', filename=filename))
    else:
        return "No se encontró ningún ticket.", 404
    
@app.route('/reimpresion_c/<id>')
def reimpresion_c(id):
    cur = mysql.connection.cursor()
    cur.callproc('Reimpresion_c', (id,))
    ticket_filename = cur.fetchone()

    if ticket_filename:
        # Obtener el nombre de archivo del ticket
        filename = ticket_filename[0]

        # Redirigir a la página que muestra el ticket con el filename obtenido
        return redirect(url_for('mostrar_ticket', filename=filename))
    else:
        return "No se encontró ningún ticket.", 404



if __name__ == '__main__':
 app.run(port=3000, debug = True)