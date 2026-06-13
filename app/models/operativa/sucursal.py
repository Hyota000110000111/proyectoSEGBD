from app.extensions import db

class Sucursal(db.Model):
    __tablename__ = 'sucursales'
    __bind_key__ = 'operativa'
    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)