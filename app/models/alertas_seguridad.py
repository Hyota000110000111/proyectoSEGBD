from ..extensions import db
from datetime import datetime

class AlertaSeguridad(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'alertas_seguridad'

    id_alerta = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tipo_alerta = db.Column(db.String(50), nullable=False)  # ej: 'MUCHOS_LOGIN_FALLIDOS', 'INTENTO_SQLI'
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.Enum('PENDIENTE', 'LEIDA', 'RESUELTA', name='estado_alerta_enum'), default='PENDIENTE', nullable=False)
    id_empleado_destino = db.Column(db.Integer, nullable=True, comment='Empleado al que se asigna la alerta (ej. auditor)')

    def __repr__(self):
        return f'<AlertaSeguridad {self.id_alerta} - {self.tipo_alerta} ({self.estado})>'