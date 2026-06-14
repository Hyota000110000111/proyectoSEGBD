from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from . import auditor_bp
from ...utils.decorators import roles_required
from ...models.auditoria_log import AuditoriaLog
from ...models.eventos_seguridad import EventoSeguridad
from ...models.intento_login import IntentoLogin
from ...models.sesiones_usuarios import SesionUsuario
from ...models.alertas_seguridad import AlertaSeguridad

# ====================================================
# AUDITORÍA (logs generales)
# ====================================================
@auditor_bp.route('/auditoria')
@login_required
@roles_required('AUDITOR', 'ADMINISTRADOR')
def ver_auditoria():
    # Podrías añadir paginación aquí, pero por ahora se deja simple
    logs = AuditoriaLog.query.order_by(AuditoriaLog.fecha_hora.desc()).all()
    return render_template('seguridad/auditoria.html', logs=logs)

# ====================================================
# DASHBOARD DEL AUDITOR
# ====================================================
@auditor_bp.route('/dashboard')
@login_required
@roles_required('AUDITOR', 'ADMINISTRADOR')
def dashboard():
    # Fechas de referencia
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hace30dias = datetime.now() - timedelta(days=30)

    # 1. Tarjetas de estadísticas
    eventos_criticos = EventoSeguridad.query.filter(
        EventoSeguridad.gravedad == 'CRITICA',
        EventoSeguridad.fecha_hora >= hace30dias
    ).count()

    intentos_fallidos = IntentoLogin.query.filter(
        IntentoLogin.exitoso == False,
        IntentoLogin.fecha_hora >= hoy
    ).count()

    sesiones_activas = SesionUsuario.query.filter_by(activa=True).count()
    alertas_pendientes = AlertaSeguridad.query.filter_by(estado='PENDIENTE').count()

    # 2. Últimos eventos de seguridad (10)
    ultimos_eventos = EventoSeguridad.query.order_by(
        EventoSeguridad.fecha_hora.desc()
    ).limit(10).all()

    # 3. Últimos intentos fallidos (10)
    ultimos_intentos_fallidos = IntentoLogin.query.filter_by(
        exitoso=False
    ).order_by(IntentoLogin.fecha_hora.desc()).limit(10).all()

    # 4. Sesiones activas (detalle)
    sesiones_activas_detalle = SesionUsuario.query.filter_by(
        activa=True
    ).order_by(SesionUsuario.fecha_inicio.desc()).all()

    # 5. Datos para gráfico de tendencia de intentos fallidos (últimos 7 días)
    ultimos_7_dias = [(datetime.now() - timedelta(days=i)).date() for i in range(6, -1, -1)]
    intentos_labels = [d.strftime('%a') for d in ultimos_7_dias]  # Lun, Mar, ...
    intentos_datos = []
    for dia in ultimos_7_dias:
        inicio = datetime.combine(dia, datetime.min.time())
        fin = datetime.combine(dia, datetime.max.time())
        count = IntentoLogin.query.filter(
            IntentoLogin.exitoso == False,
            IntentoLogin.fecha_hora >= inicio,
            IntentoLogin.fecha_hora <= fin
        ).count()
        intentos_datos.append(count)

    # 6. Datos para gráfico de eventos por gravedad
    gravedad_labels = ['CRITICA', 'ALTA', 'MEDIA', 'BAJA']
    gravedad_datos = []
    for g in gravedad_labels:
        count = EventoSeguridad.query.filter_by(gravedad=g).count()
        gravedad_datos.append(count)

    return render_template(
        'dashboard_auditor.html',
        eventos_criticos=eventos_criticos,
        intentos_fallidos=intentos_fallidos,
        sesiones_activas=sesiones_activas,
        alertas_pendientes=alertas_pendientes,
        ultimos_eventos=ultimos_eventos,
        ultimos_intentos_fallidos=ultimos_intentos_fallidos,
        sesiones_activas_detalle=sesiones_activas_detalle,
        intentos_labels=intentos_labels,
        intentos_datos=intentos_datos,
        gravedad_labels=gravedad_labels,
        gravedad_datos=gravedad_datos
    )