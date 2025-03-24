from conexion import Conexion

class TarjetaDAO:
    OBTENER_TARJETAS_POR_USUARIO = """
        SELECT id, numero_tarjeta, tipo_tarjeta, titular, vencimiento 
        FROM tarjetas 
        WHERE id_usuario = %s AND estado = 'activo'
    """
    INSERTAR_TARJETA = """
        INSERT INTO tarjetas(numero_tarjeta, tipo_tarjeta, titular, vencimiento, cvv, id_usuario, estado) 
        VALUES(%s, %s, %s, %s, %s, %s, 'activo')
    """
    ACTUALIZAR_ESTADO_TARJETA = """
        UPDATE tarjetas SET estado = 'inactivo' WHERE id = %s AND id_usuario = %s
    """

    @classmethod
    def obtener_tarjetas_por_usuario(cls, id_usuario):
        tarjetas = []
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(cls.OBTENER_TARJETAS_POR_USUARIO, (id_usuario,))
            tarjetas = cursor.fetchall()
        except Exception as e:
            print(f'Error al obtener tarjetas: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)
        return tarjetas

    @classmethod
    def insertar_tarjeta(cls, numero, tipo, titular, vencimiento, cvv, id_usuario):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.INSERTAR_TARJETA, (numero, tipo, titular, vencimiento, cvv, id_usuario))
            conexion.commit()
        except Exception as e:
            print(f'Error al insertar tarjeta: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def marcar_tarjeta_inactiva(cls, tarjeta_id, usuario_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.ACTUALIZAR_ESTADO_TARJETA, (tarjeta_id, usuario_id))
            conexion.commit()
        except Exception as e:
            print(f'Ocurrió un error al marcar la tarjeta como inactiva: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)