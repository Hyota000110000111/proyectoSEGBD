from app.extensions import db

class DetalleVenta(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'detalle_ventas'

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, nullable=False)
    id_medicamento = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<DetalleVenta venta {self.id_venta}>'