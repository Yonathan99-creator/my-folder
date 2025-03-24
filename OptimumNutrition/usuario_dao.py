from usuario import Usuario
from conexion import Conexion


class UsuarioDAO:
    SELECCIONAR_LOGIN = """
        SELECT id, nombre, tipo_usuario
        FROM usuarios
        WHERE email = %s AND password = %s
    """
    INSERTAR_LOGIN = """
        INSERT INTO usuarios (nombre, apellido, email, password, telefono, direccion, tipo_usuario, fecha_registro, estado) 
        VALUES (%s, %s, %s, %s, %s, %s, 'cliente', NOW(), 'activo')
    """

    @classmethod
    def seleccionar_login(cls, email, password):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            valores = (email, password)
            cursor.execute(cls.SELECCIONAR_LOGIN, valores)
            registro = cursor.fetchone()
            if registro:
                # Mapeo de los datos a la clase Usuario
                cliente = Usuario(id=registro[0], nombre=registro[1], tipo_usuario=registro[2])
                return cliente
            return None  # Si no se encuentra el usuario
        except Exception as e:
            print(f'Excepción al seleccionar cliente por email y password: {e}')
        finally:
            if conexion:
                cursor.close()
                Conexion.liberar_conexion(conexion)

    @classmethod
    def insertar(cls, cliente):
        conexion = None
        try:
            conexion = Conexion.obtener_conexion()
            cursor = conexion.cursor()
            valores = (cliente.nombre, cliente.apellido, cliente.email, cliente.password, 
                       cliente.telefono, cliente.direccion)
            cursor.execute(cls.INSERTAR_LOGIN, valores)
            conexion.commit()
            return cursor.rowcount  # Retorna la cantidad de filas afectadas
        except Exception as e:
            print(f'Ocurrió un error al insertar cliente: {e}')
        finally:
            if conexion:
                cursor.close()
                Conexion.liberar_conexion(conexion)

if __name__ == '__main__':
    #  Insertar cliente
    # cliente1 = Cliente(nombre='Alejandra', apellido='Tellez', membresia=300)
    # clientes_insertados = ClienteDAO.insertar(cliente1)
    # print(f'Clientes insertados: {clientes_insertados}')

    # Actualizacion cliente
    # cliente_actualizar = Cliente(3, 'Alexa', 'Tellez', 400)
    # clientes_actualizados = ClienteDAO.actualizar(cliente_actualizar)
    # print(f'Clientes actualizados: {clientes_actualizados}')

    # Eliminar cliente
    # cliente_eliminar = Cliente(id=3)
    # clientes_eliminados = ClienteDAO.eliminar(cliente_eliminar)
    # print(f'Clientes eliminados: {clientes_eliminados}')

    # Seleccionar clientes
    cliente = UsuarioDAO.seleccionar_login('yonathangonzalez@gmail.com','12345678')
    print(f'Cliente logeado: {cliente}')
