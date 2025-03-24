from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from usuario import Usuario
from usuario_dao import UsuarioDAO
from producto import Producto
from producto_dao import ProductoDAO
from reseña import Reseña
from reseña_dao import ReseñaDAO
from imagen import Imagen
from imagen_dao import ImagenDAO
from carrito_dao import CarritoDAO
from carrito_producto_dao import CarritoProductoDAO
from tarjeta_dao import TarjetaDAO
from pedido_dao import PedidoDAO
from pedido_producto_dao import PedidoProductoDAO

app = Flask(__name__)

titulo_app = 'Optimum Nutrition'

app.config['SECRET_KEY'] = 'llave_secreta'

# Ruta pagina principal

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# Rutas para el login, registro y logout

@app.route('/index')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = UsuarioDAO.seleccionar_login(email, password)
        
        if usuario:
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombre
            session['tipo_usuario'] = usuario.tipo_usuario
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html', titulo=titulo_app)

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    email = request.form.get('email')
    password = request.form.get('password')
    telefono = request.form.get('telefono')
    direccion = request.form.get('direccion')
    
    if nombre and apellido and email and password and telefono and direccion:
        usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=password,
            telefono=telefono,
            direccion=direccion
        )
        UsuarioDAO.insertar(usuario)
        flash('Usuario registrado con éxito', 'success')
        return redirect(url_for('login'))
    
    flash('Error al registrar usuario, revisa los datos ingresados', 'danger')
    return redirect(url_for('registro'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('nombre', None)
    session.pop('tipo_usuario', None)
    flash('Sesion cerrada', 'success')
    return redirect(url_for('dashboard'))

# Rutas del submenu de productos

@app.route('/proteina')
def proteina():
    productos = ProductoDAO.seleccionar(tipo='proteina')
    return render_template('proteina.html', productos=productos)

@app.route('/ganador')
def ganador():
    productos = ProductoDAO.seleccionar(tipo='mass')
    return render_template('ganador.html', productos=productos)

@app.route('/amino')
def amino():
    productos = ProductoDAO.seleccionar(tipo='amino')
    return render_template('amino.html', productos=productos)

@app.route('/creatina')
def creatina():
    productos = ProductoDAO.seleccionar(tipo='creatina')
    return render_template('creatina.html', productos=productos)

# Rutas de producto (principal y reseñas)

@app.route('/producto/<int:producto_id>')
def producto(producto_id):
    producto_seleccionado = ProductoDAO.seleccionar_por_id(producto_id)
    
    if not producto_seleccionado:
        flash('Producto no encontrado', 'danger')
        return redirect(url_for('dashboard'))

    # Reseñas del producto
    resenas = ReseñaDAO.seleccionar_reseñas(producto_id)

    # Imágenes del producto
    imagenes = ImagenDAO.seleccionar_imagenes(producto_id)
    
    return render_template('producto.html', producto=producto_seleccionado, resenas=resenas, imagenes=imagenes)

@app.route('/producto/<int:producto_id>/reseña', methods=['POST'])
def agregar_resena(producto_id):
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para dejar una reseña.', 'danger')
        return redirect(url_for('producto', producto_id=producto_id))
    
    usuario_id = session['usuario_id']
    calificacion = request.form.get('calificacion')
    comentario = request.form.get('comentario')
    
    if comentario and calificacion:
        calificacion = int(calificacion)
        reseña = Reseña(usuario_id=usuario_id, producto_id=producto_id, calificacion=calificacion, comentario=comentario)
        ReseñaDAO.insertar_reseña(reseña)
        flash('Reseña agregada con éxito', 'success')
    else:
        flash('Por favor, proporciona tanto una calificación como un comentario.', 'danger')
    
    return redirect(url_for('producto', producto_id=producto_id))

# Ruta para agregar al carrito
@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para agregar productos al carrito.', 'danger')
        return redirect(url_for('producto', producto_id=producto_id))

    cantidad = int(request.form.get('cantidad', 1))
    producto = ProductoDAO.seleccionar_por_id(producto_id)

    if producto is None:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('dashboard'))

    if producto.stock < cantidad:
        if producto.stock == 0:
            flash('No hay productos en stock.', 'danger')
        else:
            flash(f'Sólo hay {producto.stock} productos disponibles.', 'danger')
        return redirect(url_for('producto', producto_id=producto_id))

    usuario_id = session['usuario_id']
    carrito_id = CarritoDAO.obtener_o_crear_carrito(usuario_id)
    CarritoProductoDAO.agregar_producto(carrito_id, producto_id, cantidad)
    ProductoDAO.disminuir_stock(producto_id, cantidad)
    flash('Producto agregado al carrito con éxito.', 'success')

    return redirect(url_for('producto', producto_id=producto_id))

# Ruta para carrito
@app.route('/carrito')
def carrito():
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para ver tu carrito.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    productos = CarritoProductoDAO.obtener_productos_carrito(usuario_id)
    
    return render_template('carrito.html', productos=productos)

# Ruta para eliminar producto del carrito
@app.route('/carrito/eliminar/<int:producto_id>', methods=['POST'])
def eliminar_producto_carrito(producto_id):
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para modificar tu carrito.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    
    CarritoProductoDAO.eliminar_producto_por_usuario(usuario_id, producto_id)
    
    flash('Producto eliminado del carrito.', 'success')
    return redirect(url_for('carrito'))

# Rutas para pago, guardar tarjeta y eliminar tarjeta
@app.route('/pago')
def pago():
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para continuar al pago.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    productos = CarritoProductoDAO.obtener_productos_carrito(usuario_id)
    total = sum(p['total_por_producto'] for p in productos)
    tarjetas = TarjetaDAO.obtener_tarjetas_por_usuario(usuario_id)

    return render_template('pago.html', productos=productos, total=total, tarjetas=tarjetas)

@app.route('/guardar_tarjeta', methods=['POST'])
def guardar_tarjeta():
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para guardar una tarjeta.', 'danger')
        return redirect(url_for('login'))

    numero_tarjeta = request.form['numero_tarjeta']
    tipo_tarjeta = request.form['tipo_tarjeta']
    titular = request.form['titular']
    vencimiento = request.form['fecha_expiracion']
    cvv = request.form['cvv']
    id_usuario = session['usuario_id']

    try:
        TarjetaDAO.insertar_tarjeta(numero_tarjeta, tipo_tarjeta, titular, vencimiento, cvv, id_usuario)
        flash('Tarjeta guardada correctamente.', 'success')
    except Exception as e:
        print(f'Ocurrió un error: {e}')
        flash('Error al guardar la tarjeta.', 'danger')
    
    return redirect(url_for('pago'))

@app.route('/eliminar_tarjeta/<int:tarjeta_id>', methods=['POST'])
def eliminar_tarjeta(tarjeta_id):
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para modificar tus tarjetas.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    try:
        TarjetaDAO.marcar_tarjeta_inactiva(tarjeta_id, usuario_id)
        flash('Tarjeta eliminada correctamente.', 'success')
    except Exception as e:
        flash('Error al eliminar la tarjeta.', 'danger')
        print(f'Ocurrió un error: {e}')

    return redirect(url_for('pago'))

# Ruta para confirmar el pedido
@app.route('/confirmar_pedido', methods=['POST'])
def confirmar_pedido():
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para confirmar tu pedido.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    productos = CarritoProductoDAO.obtener_productos_carrito(usuario_id)
    
    if not productos:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('carrito'))

    total = sum(p['total_por_producto'] for p in productos)
    try:
        pedido_id = PedidoDAO.insertar_pedido(usuario_id, total)

        for producto in productos:
            PedidoProductoDAO.insertar_pedido_producto(
                pedido_id,
                producto['id'],
                producto['cantidad'],
                producto['total_por_producto']
            )

        for producto in productos:
            CarritoProductoDAO.eliminar_producto_por_usuario(usuario_id, producto['id'])

        flash('Pedido confirmado exitosamente.', 'success')
    except Exception as e:
        flash('Ocurrió un problema al confirmar el pedido.', 'danger')

    return redirect(url_for('carrito'))

# Ruta para compra
@app.route('/compra')
def compra():
    if 'usuario_id' not in session:
        flash('Necesitas estar autenticado para ver tus compras.', 'danger')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    pedidos = PedidoDAO.obtener_pedidos_por_usuario(usuario_id)
    
    return render_template('compra.html', pedidos=pedidos)

# Ruta para detalle_compra
@app.route('/detalle_compra/<int:pedido_id>')
def detalle_compra(pedido_id):
    
    pedido = PedidoDAO.obtener_pedido_por_id(pedido_id)
    productos = PedidoProductoDAO.obtener_productos_por_pedido(pedido_id)

    return render_template('detalle_compra.html', pedido=pedido, productos=productos)

if __name__ == '__main__':
    app.run(debug=True)