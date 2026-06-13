from ..extensions import db
from datetime import datetime

class IntentoLogin(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'intentos_login'

    id_intento = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    ip_origen = db.Column(db.String(45), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    exitoso = db.Column(db.Boolean, nullable=False)