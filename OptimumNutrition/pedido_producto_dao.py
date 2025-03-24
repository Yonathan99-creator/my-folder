from conexion import Conexion

class PedidoProductoDAO:
    INSERTAR_PEDIDO_PRODUCTO = """
        INSERT INTO pedido_productos(pedido_id, producto_id, cantidad, precio_total) VALUES(%s, %s, %s, %s)
    """

    OBTENER_PRODUCTOS_POR_PEDIDO = """
        SELECT producto_id, cantidad, precio_total
        FROM pedido_productos
        WHERE pedido_id = %s
    """

    @classmethod
    def insertar_pedido_producto(cls, pedido_id, producto_id, cantidad, precio_total):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.INSERTAR_PEDIDO_PRODUCTO, (pedido_id, producto_id, cantidad, precio_total))
            conexion.commit()
        except Exception as e:
            print(f'Ocurrió un error al insertar el producto del pedido: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def obtener_productos_por_pedido(cls, pedido_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.OBTENER_PRODUCTOS_POR_PEDIDO, (pedido_id,))
            productos = cursor.fetchall()
            return productos
        except Exception as e:
            print(f'Ocurrió un error al obtener los productos del pedido: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)