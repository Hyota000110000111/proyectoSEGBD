from flask import abort
from flask_login import current_user

def verificar_permiso_escritura(registro, columna_sucursal='id_sucursal'):
    """
    Verifica que el usuario actual pueda modificar/eliminar el registro.
    - ADMINISTRADOR: siempre puede.
    - Otros roles: deben pertenecer a la misma sucursal que el registro.
    """
    if current_user.rol == 'ADMINISTRADOR':
        return True
    sucursal_registro = getattr(registro, columna_sucursal, None)
    if sucursal_registro == current_user.id_sucursal:
        return True
    abort(403, description="No autorizado para modificar este registro")

def verificar_permiso_por_sucursal(sucursal_id):
    """Versión para cuando aún no tienes el registro (ej: creación)."""
    if current_user.rol == 'ADMINISTRADOR':
        return True
    if sucursal_id == current_user.id_sucursal:
        return True
    abort(403, description="No autorizado para operar en esta sucursal")
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from datetime import datetime, timedelta
from ..extensions import db
from ..models.password_reset_token import PasswordResetToken
from ..models.operativa.empleado import Empleado

def generate_reset_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_id, salt='password-reset')

def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        user_id = serializer.loads(token, salt='password-reset', max_age=expiration)
    except:
        return None
    return Empleado.query.get(user_id)

# Alternativa con tabla propia (opcional, más segura)
def create_reset_token(empleado_id):
    token = generate_reset_token(empleado_id)
    exp = datetime.utcnow() + timedelta(hours=1)
    reset = PasswordResetToken(id_empleado=empleado_id, token=token, expiracion=exp)
    db.session.add(reset)
    db.session.commit()
    return token