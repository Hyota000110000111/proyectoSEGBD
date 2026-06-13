from app.extensions import db

class ClientePublic(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'vw_clientes_public'

    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    cedula = db.Column(db.String(20))
    telefono = db.Column(db.String(20))      # Ya enmascarado en la vista
    direccion = db.Column(db.String(200))
    sucursal_registro_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<ClientePublic {self.nombre}>'