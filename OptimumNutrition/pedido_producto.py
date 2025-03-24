class CarritoProducto:
    def __init__(self, id=None, pedido_id=None, producto_id=None, cantidad=None, precio_total=None):
        self.id = id
        self.pedido_id = pedido_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.precio_total = precio_total