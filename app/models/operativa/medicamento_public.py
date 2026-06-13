from app.extensions import db

class MedicamentoPublic(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'vw_medicamentos_public'

    id_medicamento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    precio = db.Column(db.Numeric(10, 2))
    stock = db.Column(db.Integer)
    id_sucursal = db.Column(db.Integer)

    def __repr__(self):
        return f'<MedicamentoPublic {self.nombre}>'