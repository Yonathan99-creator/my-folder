class Producto:
    def __init__(self, id=None, nombre=None, marca=None, contenido=None, ingredientes=None, precio=None, stock=None, categoria=None, fecha_creacion=None, estado=None):
        self.id = id
        self.nombre = nombre
        self.marca = marca
        self.contenido = contenido
        self.ingredientes = ingredientes
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
        self.fecha_creacion = fecha_creacion
        self.estado = estado