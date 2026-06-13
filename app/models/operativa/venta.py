from app.extensions import db
from datetime import datetime

class Venta(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'ventas'

    id_venta = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_empleado = db.Column(db.Integer, nullable=False)
    id_sucursal = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f'<Venta {self.id_venta}>'