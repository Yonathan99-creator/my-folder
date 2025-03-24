from conexion import Conexion
from producto_dao import ProductoDAO

class CarritoProductoDAO:
    INSERTAR = """
        INSERT INTO carrito_productos(carrito_id, producto_id, cantidad) VALUES(%s, %s, %s)
    """
    ACTUALIZAR_CANTIDAD = """
        UPDATE carrito_productos SET cantidad = cantidad + %s
        WHERE carrito_id = %s AND producto_id = %s
    """
    OBTENER_PRODUCTOS_CARRITO = """
        SELECT productos.id, productos.nombre, productos.marca, productos.precio, carrito_productos.cantidad
        FROM carrito_productos
        INNER JOIN productos ON carrito_productos.producto_id = productos.id
        INNER JOIN carritos ON carrito_productos.carrito_id = carritos.id
        WHERE carritos.usuario_id = %s
    """
    EXISTE_PRODUCTO_EN_CARRITO = """
        SELECT 1 FROM carrito_productos WHERE carrito_id = %s AND producto_id = %s
    """
    OBTENER_CANTIDAD_DEL_PRODUCTO = """
        SELECT cantidad FROM carrito_productos
        WHERE carrito_id IN (SELECT id FROM carritos WHERE usuario_id = %s)
        AND producto_id = %s
    """
    ELIMINAR_POR_USUARIO_Y_PRODUCTO = """
        DELETE carrito_productos 
        FROM carrito_productos
        JOIN carritos ON carrito_productos.carrito_id = carritos.id
        WHERE carrito_productos.producto_id = %s 
        AND carritos.usuario_id = %s
    """
    
    @classmethod
    def agregar_producto(cls, carrito_id, producto_id, cantidad):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()

            # Comprobar si el producto ya está en el carrito
            cursor.execute(cls.EXISTE_PRODUCTO_EN_CARRITO, (carrito_id, producto_id))
            existe = cursor.fetchone()

            if existe:
                # Si el producto ya está en el carrito, actualizamos la cantidad
                cursor.execute(cls.ACTUALIZAR_CANTIDAD, (cantidad, carrito_id, producto_id))
            else:
                # Si el producto no está en el carrito, lo insertamos
                cursor.execute(cls.INSERTAR, (carrito_id, producto_id, cantidad))
            
            conexion.commit()
            
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def obtener_productos_carrito(cls, usuario_id):
        productos_carrito = []
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(cls.OBTENER_PRODUCTOS_CARRITO, (usuario_id,))
            productos_carrito = cursor.fetchall()
        except Exception as e:
            print(f'Ocurrió un error al obtener los productos del carrito: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

        # Se procesan los productos para calcular total por producto
        for producto in productos_carrito:
            producto['total_por_producto'] = producto['precio'] * producto['cantidad']
        
        return productos_carrito
    
    @classmethod
    def eliminar_producto_por_usuario(cls, usuario_id, producto_id):
        cantidad = 0
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.OBTENER_CANTIDAD_DEL_PRODUCTO, (usuario_id, producto_id))
            resultado = cursor.fetchone()
            if resultado:
                cantidad = resultado[0]
                
            cursor.execute(cls.ELIMINAR_POR_USUARIO_Y_PRODUCTO, (producto_id, usuario_id))
            conexion.commit()

            # Incrementar el stock del producto eliminado
            if cantidad > 0:
                ProductoDAO.incrementar_stock(producto_id, cantidad)

        except Exception as e:
            print(f'Ocurrió un error al eliminar el producto del carrito: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)