from flask import render_template, request
from flask_login import login_required, current_user
from . import seguridad_bp
from ...utils.decorators import roles_required
from ...models.intento_login import IntentoLogin
from ...models.auditoria_log import AuditoriaLog
from ...models.eventos_seguridad import EventoSeguridad
from ...models.alertas_seguridad import AlertaSeguridad
from ...models.sesiones_usuarios import SesionUsuario

# ====================================================
# Intentos de login (con paginación)
# ====================================================
@seguridad_bp.route('/intentos-login')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def intentos_login():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = IntentoLogin.query.order_by(IntentoLogin.fecha_hora.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    intentos = pagination.items
    return render_template('seguridad/intentos_login.html', 
                           intentos=intentos, 
                           pagination=pagination)

# ====================================================
# Auditoría (logs de cambios en tablas operativas)
# ====================================================
@seguridad_bp.route('/auditoria')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def auditoria():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = AuditoriaLog.query.order_by(AuditoriaLog.fecha_hora.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    logs = pagination.items
    return render_template('seguridad/auditoria.html', 
                           logs=logs, 
                           pagination=pagination)

# ====================================================
# Eventos de seguridad (cambios de rol, accesos denegados, etc.)
# ====================================================
@seguridad_bp.route('/eventos')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def eventos():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = EventoSeguridad.query.order_by(EventoSeguridad.fecha_hora.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    eventos = pagination.items
    return render_template('seguridad/eventos.html', 
                           eventos=eventos, 
                           pagination=pagination)

# ====================================================
# Alertas de seguridad (stock bajo, intentos fallidos, etc.)
# ====================================================
@seguridad_bp.route('/alertas')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def alertas():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = AlertaSeguridad.query.order_by(AlertaSeguridad.fecha_hora.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    alertas = pagination.items
    return render_template('seguridad/alertas.html', 
                           alertas=alertas, 
                           pagination=pagination)

# ====================================================
# Sesiones activas (usando la tabla sesiones_usuarios)
# ====================================================
@seguridad_bp.route('/sesiones-activas')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def sesiones_activas():
    # Filtrar sesiones activas (activa = True y fecha_fin NULL)
    sesiones = SesionUsuario.query.filter_by(activa=True).order_by(SesionUsuario.fecha_inicio.desc()).all()
    return render_template('seguridad/sesiones_activas.html', sesiones=sesiones)