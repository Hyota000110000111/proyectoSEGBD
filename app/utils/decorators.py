from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
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
    # Obtener el id_sucursal del registro (asumiendo que tiene el atributo)
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
    abort(403)
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sucursal_permitida(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.rol != 'AUDITOR' and current_user.id_sucursal is None:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function