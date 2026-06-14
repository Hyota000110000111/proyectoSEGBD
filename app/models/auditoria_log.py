from ..extensions import db
from datetime import datetime

class AuditoriaLog(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'auditoria_log'

    id_log = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, server_default=db.func.current_timestamp())
    usuario_real = db.Column(db.String(100), nullable=False)
    tabla_afectada = db.Column(db.String(100), nullable=False)
    operacion = db.Column(db.Enum('INSERT', 'UPDATE', 'DELETE', name='operacion_enum'), nullable=False)
    valores_anteriores = db.Column(db.JSON, nullable=True)
    valores_nuevos = db.Column(db.JSON, nullable=True)
    ip_origen = db.Column(db.String(50), nullable=True)

    # Índices para consultas rápidas
    __table_args__ = (
        db.Index('idx_auditoria_fecha', 'fecha_hora'),
        db.Index('idx_auditoria_tabla', 'tabla_afectada'),
        db.Index('idx_auditoria_usuario', 'usuario_real'),
    )

    def __repr__(self):
        return f'<AuditoriaLog {self.id_log} - {self.tabla_afectada} - {self.operacion} - {self.fecha_hora}>'

    def to_dict(self):
        """Devuelve un diccionario con los datos principales (útil para APIs)"""
        return {
            'id_log': self.id_log,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'usuario_real': self.usuario_real,
            'tabla_afectada': self.tabla_afectada,
            'operacion': self.operacion,
            'valores_anteriores': self.valores_anteriores,
            'valores_nuevos': self.valores_nuevos,
            'ip_origen': self.ip_origen
        }