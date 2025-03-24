from conexion import Conexion

class PedidoDAO:
    INSERTAR_PEDIDO = """
        INSERT INTO pedidos(usuario_id, total, estado) VALUES(%s, %s, %s)
    """
    OBTENER_PEDIDOS_POR_USUARIO = """
        SELECT id, usuario_id, total, estado, fecha_pedido, fecha_entregado 
        FROM pedidos
        WHERE usuario_id = %s
    """
    OBTENER_PEDIDO_POR_ID = """
        SELECT id, usuario_id, total, estado, fecha_pedido, fecha_entregado
        FROM pedidos
        WHERE id = %s
    """

    @classmethod
    def insertar_pedido(cls, usuario_id, total, estado="pendiente"):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.INSERTAR_PEDIDO, (usuario_id, total, estado))
            conexion.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f'Ocurrió un error al insertar el pedido: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def obtener_pedidos_por_usuario(cls, usuario_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.OBTENER_PEDIDOS_POR_USUARIO, (usuario_id,))
            pedidos = cursor.fetchall()
            return pedidos
        except Exception as e:
            print(f'Ocurrió un error al obtener los pedidos: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def obtener_pedido_por_id(cls, pedido_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.OBTENER_PEDIDO_POR_ID, (pedido_id,))
            pedido = cursor.fetchone()
            return pedido
        except Exception as e:
            print(f'Ocurrió un error al obtener el pedido: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)