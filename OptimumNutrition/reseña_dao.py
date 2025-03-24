from reseña import Reseña
from conexion import Conexion

class ReseñaDAO:
    SELECCIONAR_RESEÑAS = """
        SELECT r.id, r.usuario_id, r.producto_id, r.calificacion, r.comentario, r.fecha_resena, u.nombre
        FROM resenas r
        INNER JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.producto_id = %s
    """
    INSERTAR_RESEÑAS = """
        INSERT INTO resenas (usuario_id, producto_id, calificacion, comentario, fecha_resena) 
        VALUES (%s, %s, %s, %s, NOW())
    """
    
    @classmethod
    def seleccionar_reseñas(cls, producto_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.SELECCIONAR_RESEÑAS, (producto_id,))
            registros = cursor.fetchall()
            reseñas = []
            for registro in registros:
                reseña = Reseña(*registro)
                reseñas.append(reseña)
            return reseñas
        except Exception as e:
            print(f'Ocurrió un error al seleccionar reseñas: {e}')
            return []
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def insertar_reseña(cls, reseña):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            valores = (reseña.usuario_id, reseña.producto_id, reseña.calificacion, reseña.comentario)
            cursor.execute(cls.INSERTAR_RESEÑAS, valores)
            conexion.commit()
            return cursor.rowcount  # Retorna la cantidad de filas afectadas
        except Exception as e:
            print(f'Ocurrió un error al insertar reseña: {e}')
        finally:
            if conexion:
                cursor.close()
                Conexion.liberar_conexion(conexion)