from ..extensions import db
from datetime import datetime

class HistorialContrasena(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'historial_contrasenas'

    id_historial = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, nullable=False, comment='Referencia a empleado en BD operativa')
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cambiado_por = db.Column(db.String(100), nullable=True, comment='Usuario o sistema que realizó el cambio')

    def __repr__(self):
        return f'<HistorialContrasena Empleado {self.id_empleado} - {self.fecha_cambio}>'