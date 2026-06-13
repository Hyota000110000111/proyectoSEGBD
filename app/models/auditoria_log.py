from ..extensions import db

class AuditoriaLog(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'auditoria_log'
    id_log = db.Column(db.BigInteger, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=db.func.current_timestamp())
    usuario_real = db.Column(db.String(100), nullable=False)
    tabla_afectada = db.Column(db.String(100), nullable=False)
    operacion = db.Column(db.Enum('INSERT','UPDATE','DELETE'), nullable=False)
    valores_anteriores = db.Column(db.JSON, nullable=True)
    valores_nuevos = db.Column(db.JSON, nullable=True)
    ip_origen = db.Column(db.String(50), nullable=True)