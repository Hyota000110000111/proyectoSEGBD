from app.extensions import db

class DetalleVentaPublic(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'vw_detalle_ventas_public'

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer)
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Numeric(10, 2))
    medicamento_nombre = db.Column(db.String(150))

    def __repr__(self):
        return f'<DetalleVentaPublic venta {self.id_venta} - {self.medicamento_nombre}>'