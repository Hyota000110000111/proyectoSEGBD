from ..extensions import db
from datetime import datetime

class PasswordResetToken(db.Model):
    __bind_key__ = 'seguridad'
    __tablename__ = 'password_reset_tokens'

    id_token = db.Column(db.Integer, primary_key=True)
    id_empleado = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expiracion = db.Column(db.DateTime, nullable=False)
    usado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        return not self.usado and self.expiracion > datetime.utcnow()