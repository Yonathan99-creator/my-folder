class Usuario:
    def __init__(self, id=None, numero_tarjeta=None, tipo_tarjeta=None, titular=None, vencimiento=None, cvv=None, id_usuario=None, estado=None):
        self.id = id
        self.numero_tarjeta = numero_tarjeta
        self.tipo_tarjeta = tipo_tarjeta
        self.titular = titular
        self.vencimiento = vencimiento
        self.cvv = cvv
        self.id_usuario = id_usuario
        self.estado = estado