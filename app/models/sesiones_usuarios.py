from ..extensions import db
from datetime import datetime, timezone

class SesionUsuario(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'sesiones_usuarios'

    id_sesion = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, nullable=False, index=True, comment='Referencia a empleado en BD operativa')
    token_sesion = db.Column(db.String(255), nullable=False, unique=True, index=True)
    fecha_inicio = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    ip = db.Column(db.String(45), nullable=True, comment='Dirección IP del cliente')
    user_agent = db.Column(db.Text, nullable=True, comment='User-Agent del navegador')
    activa = db.Column(db.Boolean, default=True, nullable=False, index=True)

    def cerrar_sesion(self):
        """Marca la sesión como cerrada y registra la fecha de fin."""
        self.activa = False
        self.fecha_fin = datetime.now(timezone.utc)
        db.session.commit()

    def es_activa(self):
        """Devuelve True si la sesión está activa y no ha expirado (opcional)."""
        return self.activa and self.fecha_fin is None

    @staticmethod
    def crear_sesion(id_empleado, token, ip, user_agent):
        """Crea una nueva sesión y la guarda en la base de datos."""
        sesion = SesionUsuario(
            id_empleado=id_empleado,
            token_sesion=token,
            ip=ip,
            user_agent=user_agent,
            activa=True
        )
        db.session.add(sesion)
        db.session.commit()
        return sesion

    def __repr__(self):
        return f'<SesionUsuario {self.id_sesion} | Empleado {self.id_empleado} | Activa: {self.activa}>'