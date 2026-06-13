from flask import render_template
from flask_login import login_required, current_user
from . import auditor_bp
from ...utils.decorators import roles_required
from ...models.auditoria_log import AuditoriaLog
# Si no usas estos modelos públicos en esta vista, no es necesario importarlos
# from ...models.operativa.empleado_public import EmpleadoPublic
# from ...models.operativa.cliente_public import ClientePublic
# from ...models.operativa.medicamento_public import MedicamentoPublic
# from ...models.operativa.venta_public import VentaPublic

@auditor_bp.route('/auditoria')
@login_required
@roles_required('AUDITOR')
def ver_auditoria():
    logs = AuditoriaLog.query.order_by(AuditoriaLog.fecha_hora.desc()).all()
    return render_template('seguridad/auditoria.html', logs=logs)
@auditor_bp.route('/dashboard')
@login_required
@roles_required('AUDITOR')
def dashboard():
    return render_template('dashboard_auditor.html')