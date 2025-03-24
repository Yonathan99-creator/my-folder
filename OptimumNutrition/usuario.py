class Usuario:
    def __init__(self, id=None, nombre=None, apellido=None, email=None, password=None, telefono=None, direccion=None, tipo_usuario=None, fecha_registro=None, estado=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password = password
        self.telefono = telefono
        self.direccion = direccion
        self.tipo_usuario = tipo_usuario
        self.fecha_registro = fecha_registro
        self.estado = estado