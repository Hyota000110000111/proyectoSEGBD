from ..extensions import db
from datetime import datetime

class EventoSeguridad(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'eventos_seguridad'

    id_evento = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo_evento = db.Column(db.String(50), nullable=False)  # ej: 'LOGIN_FALLIDO', 'ACCESO_DENEGADO', 'CAMBIO_ROL'
    gravedad = db.Column(db.Enum('BAJA', 'MEDIA', 'ALTA', 'CRITICA', name='gravedad_enum'), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    id_empleado_afectado = db.Column(db.Integer, nullable=True, comment='Empleado afectado o que realizó la acción')
    ip_origen = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f'<EventoSeguridad {self.id_evento} - {self.tipo_evento}>'