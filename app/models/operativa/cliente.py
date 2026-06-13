from app.extensions import db

class Cliente(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'clientes'

    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(200))
    sucursal_registro_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Cliente {self.nombre}>'