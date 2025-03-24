from producto import Producto
from conexion import Conexion


class ProductoDAO:
    SELECCIONAR_PRODUCTOS = """
        SELECT *
        FROM productos
        WHERE stock >= 1 AND categoria = %s AND estado = 'activo'
    """
    SELECCIONAR_POR_ID = """ 
        SELECT * 
        FROM productos 
        WHERE id = %s 
    """
    DISMINUIR_STOCK = """
        UPDATE productos
        SET stock = stock - %s 
        WHERE id = %s
    """
    INCREMENTAR_STOCK = """
        UPDATE productos
        SET stock = stock + %s
        WHERE id = %s
    """

    @classmethod
    def seleccionar(cls, tipo):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute(cls.SELECCIONAR_PRODUCTOS, (tipo,))

            registros = cursor.fetchall()
            productos = []
            for registro in registros:
                producto = Producto(*registro)
                productos.append(producto)
            return productos
        except Exception as e:
            print(f'Ocurrió un error al seleccionar productos: {e}')
            raise
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def seleccionar_por_id(cls, producto_id):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.SELECCIONAR_POR_ID, (producto_id,))
            registro = cursor.fetchone()
            if registro:
                return Producto(*registro)
            else:
                return None
        except Exception as e:
            print(f'Ocurrió un error al seleccionar el producto: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def disminuir_stock(cls, producto_id, cantidad):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.DISMINUIR_STOCK, (cantidad, producto_id))
            conexion.commit()
        except Exception as e:
            print(f'Ocurrió un error al disminuir el stock: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def incrementar_stock(cls, producto_id, cantidad):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(cls.INCREMENTAR_STOCK, (cantidad, producto_id))
            conexion.commit()
        except Exception as e:
            print(f'Ocurrió un error al incrementar el stock: {e}')
        finally:
            if conexion is not None:
                cursor.close()
                Conexion.liberar_conexion(conexion)