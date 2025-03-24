from conexion import Conexion

class CarritoDAO:
    OBTENER_POR_USUARIO = """
        SELECT id FROM carritos WHERE usuario_id = %s
    """
    INSERTAR = """
        INSERT INTO carritos(usuario_id) VALUES(%s)
    """
    
    @classmethod
    def obtener_o_crear_carrito(cls, usuario_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.OBTENER_POR_USUARIO, (usuario_id,))
            carrito = cursor.fetchone()
            if carrito:
                return carrito[0]
            else:
                cursor.execute(cls.INSERTAR, (usuario_id,))
                conexion.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f'Ocurrió un error: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)