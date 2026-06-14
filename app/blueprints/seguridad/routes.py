from flask import render_template, request, make_response, abort
from flask_login import login_required, current_user
from datetime import datetime
from io import BytesIO
from fpdf import FPDF

from . import seguridad_bp
from ...utils.decorators import roles_required
from ...models.intento_login import IntentoLogin
from ...models.auditoria_log import AuditoriaLog
from ...models.eventos_seguridad import EventoSeguridad
from ...models.alertas_seguridad import AlertaSeguridad
from ...models.sesiones_usuarios import SesionUsuario

# ====================================================
# Exportar auditoría a PDF
# ====================================================
from flask import send_file
from io import BytesIO

@seguridad_bp.route('/exportar-pdf')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def exportar_auditoria_pdf():
    try:
        logs = AuditoriaLog.query.order_by(AuditoriaLog.fecha_hora.desc()).all()

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'FarmaSegura - Reporte de Auditoría', 0, 1, 'C')
                self.set_font('Arial', 'I', 10)
                self.cell(0, 10, f'Generado: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

        pdf = PDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font('Arial', 'B', 9)

        col_widths = [15, 35, 35, 30, 25, 30, 60]
        headers = ['ID', 'Fecha', 'Usuario', 'Tabla', 'Op.', 'IP', 'Detalles']

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()

        pdf.set_font('Arial', '', 8)
        for log in logs:
            fecha = log.fecha_hora.strftime('%d/%m/%Y %H:%M') if log.fecha_hora else ''
            detalles = ''
            if log.operacion == 'INSERT':
                detalles = str(log.valores_nuevos)[:50] if log.valores_nuevos else ''
            elif log.operacion == 'UPDATE':
                old = str(log.valores_anteriores)[:25] if log.valores_anteriores else ''
                new = str(log.valores_nuevos)[:25] if log.valores_nuevos else ''
                detalles = f"{old} -> {new}"
            else:
                detalles = str(log.valores_anteriores)[:50] if log.valores_anteriores else ''

            row = [
                str(log.id_log),
                fecha,
                log.usuario_real,
                log.tabla_afectada,
                log.operacion,
                log.ip_origen or '',
                detalles
            ]
            for i, cell in enumerate(row):
                pdf.cell(col_widths[i], 8, cell, 1, 0, 'L')
            pdf.ln()

        # Obtener el PDF como bytes (en fpdf2 ya es bytes)
        pdf_bytes = pdf.output(dest='S')
        # Asegurarse de que sea bytes (por si acaso)
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1')

        # Enviar el archivo usando send_file (maneja correctamente las cabeceras)
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name='auditoria_farmasegura.pdf'
        )

    except Exception as e:
        # Para depuración, imprime el error en la consola de Flask
        print(f"Error en exportación PDF: {str(e)}")
        return f"Error generando el PDF: {str(e)}", 500
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
# Eventos de seguridad
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
# Alertas de seguridad
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
# Sesiones activas
# ====================================================
@seguridad_bp.route('/sesiones-activas')
@login_required
@roles_required('ADMINISTRADOR', 'AUDITOR')
def sesiones_activas():
    sesiones = SesionUsuario.query.filter_by(activa=True).order_by(SesionUsuario.fecha_inicio.desc()).all()
    return render_template('seguridad/sesiones_activas.html',
                           sesiones=sesiones)