class Pedido:
    def __init__(self, id=None, usuario_id=None, total=None, estado=None, fecha_pedido=None, fecha_entregado=None):
        self.id = id
        self.usuario_id = usuario_id
        self.total = total
        self.estado = estado
        self.fecha_pedido = fecha_pedido
        self.fecha_entregado = fecha_entregado