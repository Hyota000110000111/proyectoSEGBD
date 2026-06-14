from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from . import admin_bp
from ...utils.decorators import roles_required
from ...utils.security import verificar_permiso_por_sucursal, verificar_permiso_escritura
from ...utils.audit import registrar_auditoria  # ← Importamos la función de auditoría
from ...extensions import db, bcrypt
from ...models.operativa.empleado import Empleado
from ...models.operativa.sucursal import Sucursal
from ...models.operativa.empleado_public import EmpleadoPublic
from ...models.operativa.cliente import Cliente
from ...models.operativa.medicamento import Medicamento
from ...models.operativa.venta import Venta
from ...models.operativa.detalle_venta import DetalleVenta

# ====================================================
# EMPLEADOS
# ====================================================
@admin_bp.route('/empleados')
@login_required
@roles_required('ADMINISTRADOR')
def listar_empleados():
    empleados = EmpleadoPublic.query.all()
    return render_template('admin/empleados.html', empleados=empleados)


@admin_bp.route('/empleados/nuevo', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR')
def nuevo_empleado():
    if request.method == 'POST':
        sucursal_id = request.form.get('id_sucursal', type=int)
        if sucursal_id == 0:
            sucursal_id = None
        if sucursal_id:
            sucursal = Sucursal.query.get(sucursal_id)
            if not sucursal:
                flash('Sucursal no válida', 'danger')
                return redirect(url_for('admin.nuevo_empleado'))

        hashed = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        empleado = Empleado(
            nombre=request.form['nombre'],
            usuario=request.form['usuario'],
            password_hash=hashed,
            rol=request.form['rol'],
            id_sucursal=sucursal_id,
            activo=True
        )
        db.session.add(empleado)
        db.session.flush()  # Para obtener el id_empleado antes de commit
        # Registrar auditoría
        registrar_auditoria(
            tabla='empleados',
            operacion='INSERT',
            valores_nuevos={
                'id_empleado': empleado.id_empleado,
                'nombre': empleado.nombre,
                'usuario': empleado.usuario,
                'rol': empleado.rol,
                'activo': empleado.activo
            }
        )
        db.session.commit()
        flash('Empleado creado', 'success')
        return redirect(url_for('admin.listar_empleados'))

    sucursales = Sucursal.query.all()
    return render_template('admin/empleado_form.html', sucursales=sucursales)


@admin_bp.route('/empleados/<int:id>/eliminar')
@login_required
@roles_required('ADMINISTRADOR')
def eliminar_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    # Guardar datos antes de eliminar
    datos_eliminados = {
        'id_empleado': empleado.id_empleado,
        'nombre': empleado.nombre,
        'usuario': empleado.usuario,
        'rol': empleado.rol,
        'id_sucursal': empleado.id_sucursal,
        'activo': empleado.activo
    }
    db.session.delete(empleado)
    # Registrar auditoría antes del commit
    registrar_auditoria(
        tabla='empleados',
        operacion='DELETE',
        valores_anteriores=datos_eliminados
    )
    db.session.commit()
    flash('Empleado eliminado', 'success')
    return redirect(url_for('admin.listar_empleados'))


@admin_bp.route('/empleados/<int:id>/toggle')
@login_required
@roles_required('ADMINISTRADOR')
def toggle_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    estado_anterior = empleado.activo
    empleado.activo = not empleado.activo
    # Registrar auditoría
    registrar_auditoria(
        tabla='empleados',
        operacion='UPDATE',
        valores_anteriores={'id_empleado': empleado.id_empleado, 'activo': estado_anterior},
        valores_nuevos={'id_empleado': empleado.id_empleado, 'activo': empleado.activo}
    )
    db.session.commit()
    estado = 'activado' if empleado.activo else 'desactivado'
    flash(f'Empleado {empleado.usuario} {estado}', 'success')
    return redirect(url_for('admin.listar_empleados'))


# ====================================================
# SUCURSALES (solo listado; falta crear/editar/eliminar)
# ====================================================
@admin_bp.route('/sucursales')
@login_required
@roles_required('ADMINISTRADOR')
def listar_sucursales():
    sucursales = Sucursal.query.all()
    return render_template('sucursales/listar.html', sucursales=sucursales)

# (Opcional: podrías añadir rutas para crear/editar/eliminar sucursales con auditoría)


# ====================================================
# DASHBOARD
# ====================================================
@admin_bp.route('/dashboard')
@login_required
@roles_required('ADMINISTRADOR')
def dashboard():
    try:
        # Estadísticas básicas
        total_sucursales = Sucursal.query.count()
        total_empleados = Empleado.query.count()
        total_clientes = Cliente.query.count()
        total_medicamentos = Medicamento.query.count()

        # Ventas e ingresos del mes actual
        hoy = datetime.now()
        primer_dia_mes = datetime(hoy.year, hoy.month, 1)
        ventas_mes = Venta.query.filter(Venta.fecha >= primer_dia_mes).count()
        ingresos_mes = db.session.query(func.sum(Venta.total)).filter(Venta.fecha >= primer_dia_mes).scalar() or 0

        # Ventas por sucursal
        sucursales = Sucursal.query.all()
        sucursales_nombres = []
        ventas_por_sucursal = []
        for suc in sucursales:
            total = Venta.query.filter_by(id_sucursal=suc.id_sucursal).count()
            sucursales_nombres.append(suc.nombre)
            ventas_por_sucursal.append(total)

        # Top 5 medicamentos más vendidos
        top_meds = db.session.query(
            Medicamento.nombre,
            func.sum(DetalleVenta.cantidad).label('total_vendido')
        ).join(DetalleVenta, Medicamento.id_medicamento == DetalleVenta.id_medicamento)\
         .group_by(Medicamento.id_medicamento)\
         .order_by(func.sum(DetalleVenta.cantidad).desc())\
         .limit(5).all()

        top_medicamentos_nombres = [med[0] for med in top_meds] if top_meds else []
        top_medicamentos_cantidades = [int(med[1]) for med in top_meds] if top_meds else []

        # Tendencia de ventas últimos 6 meses
        meses_labels = []
        ventas_por_mes = []
        for i in range(5, -1, -1):
            fecha_inicio = datetime(hoy.year, hoy.month, 1) - timedelta(days=i*30)
            fecha_fin = fecha_inicio + timedelta(days=32)
            fecha_fin = datetime(fecha_fin.year, fecha_fin.month, 1)
            total = Venta.query.filter(Venta.fecha >= fecha_inicio, Venta.fecha < fecha_fin).count()
            meses_labels.append(fecha_inicio.strftime('%b %Y'))
            ventas_por_mes.append(total)

        return render_template('dashboard_admin.html',
                               total_sucursales=total_sucursales,
                               total_empleados=total_empleados,
                               total_clientes=total_clientes,
                               total_medicamentos=total_medicamentos,
                               ventas_mes=ventas_mes,
                               ingresos_mes=ingresos_mes,
                               sucursales_nombres=sucursales_nombres,
                               ventas_por_sucursal=ventas_por_sucursal,
                               top_medicamentos_nombres=top_medicamentos_nombres,
                               top_medicamentos_cantidades=top_medicamentos_cantidades,
                               meses_labels=meses_labels,
                               ventas_por_mes=ventas_por_mes)
    except Exception as e:
        # Log del error (puedes usar app.logger)
        flash(f'Error al cargar el dashboard: {str(e)}', 'danger')
        return redirect(url_for('home'))