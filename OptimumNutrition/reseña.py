class Reseña:
    def __init__(self, id=None, usuario_id=None, producto_id=None, calificacion=None, comentario=None, fecha_resena=None, nombre=None):
        self.id = id
        self.usuario_id = usuario_id
        self.producto_id = producto_id
        self.calificacion = calificacion
        self.comentario = comentario
        self.fecha_resena = fecha_resena
        self.nombre = nombre