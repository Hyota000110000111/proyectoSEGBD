from app.extensions import db

class Medicamento(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'medicamentos'

    id_medicamento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    id_sucursal = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Medicamento {self.nombre}>'