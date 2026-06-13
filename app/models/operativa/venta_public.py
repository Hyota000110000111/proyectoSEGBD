from app.extensions import db

class VentaPublic(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'vw_ventas_public'

    id_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    total = db.Column(db.Numeric(10, 2))
    id_sucursal = db.Column(db.Integer)
    cliente_nombre = db.Column(db.String(150))
    empleado_nombre = db.Column(db.String(150))

    def __repr__(self):
        return f'<VentaPublic {self.id_venta} - {self.cliente_nombre}>'