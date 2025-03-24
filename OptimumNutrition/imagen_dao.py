from imagen import Imagen
from conexion import Conexion

class ImagenDAO:
    SELECCIONAR_IMAGENES = """
        SELECT *
        FROM imagenes
        WHERE producto_id = %s
    """
    
    @classmethod
    def seleccionar_imagenes(cls, producto_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.SELECCIONAR_IMAGENES, (producto_id,))
            registros = cursor.fetchall()
            imagenes = []
            for registro in registros:
                imagen = Imagen(*registro)
                imagenes.append(imagen)
            return imagenes
        except Exception as e:
            print(f'Ocurrió un error al seleccionar imagenes: {e}')
            return []
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)