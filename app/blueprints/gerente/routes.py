from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from . import gerente_bp   # ← IMPRESCINDIBLE
from ...utils.decorators import roles_required
from ...utils.security import verificar_permiso_por_sucursal, verificar_permiso_escritura
from ...extensions import db
from ...models.operativa.cliente_public import ClientePublic
from ...models.operativa.cliente import Cliente
from ...models.operativa.medicamento_public import MedicamentoPublic
from ...models.operativa.medicamento import Medicamento
from ...models.operativa.venta_public import VentaPublic
from ...models.operativa.venta import Venta
from ...models.operativa.detalle_venta import DetalleVenta
from ...models.operativa.sucursal import Sucursal
from ...forms.cliente import ClienteForm
from ...forms.medicamento import MedicamentoForm

# ============================================================
# CLIENTES
# ============================================================
@gerente_bp.route('/clientes')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def listar_clientes():
    if current_user.rol == 'ADMINISTRADOR':
        clientes = ClientePublic.query.all()
    else:
        clientes = ClientePublic.query.filter_by(sucursal_registro_id=current_user.id_sucursal).all()
    return render_template('gerente/clientes.html', clientes=clientes)

@gerente_bp.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def nuevo_cliente():
    form = ClienteForm()
    if current_user.rol == 'ADMINISTRADOR':
        form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
    else:
        form.sucursal_id.choices = [(current_user.id_sucursal, Sucursal.query.get(current_user.id_sucursal).nombre)]
        form.sucursal_id.data = current_user.id_sucursal
    if form.validate_on_submit():
        sucursal_id = form.sucursal_id.data if current_user.rol == 'ADMINISTRADOR' else current_user.id_sucursal
        cliente = Cliente(
            nombre=form.nombre.data,
            cedula=form.cedula.data,
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            sucursal_registro_id=sucursal_id
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('gerente.listar_clientes'))
    return render_template('clientes/crear.html', form=form)

@gerente_bp.route('/clientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    # Verificar permiso de escritura según sucursal
    verificar_permiso_escritura(cliente, columna_sucursal='sucursal_registro_id')
    
    # Si es GET, mostrar formulario
    form = ClienteForm(obj=cliente)
    if current_user.rol == 'ADMINISTRADOR':
        form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
    else:
        form.sucursal_id.choices = [(current_user.id_sucursal, Sucursal.query.get(current_user.id_sucursal).nombre)]
        form.sucursal_id.data = current_user.id_sucursal
    
    if form.validate_on_submit():
        # Guardar valores antiguos para auditoría
        valores_anteriores = {
            'id_cliente': cliente.id_cliente,
            'nombre': cliente.nombre,
            'cedula': cliente.cedula,
            'telefono': cliente.telefono,
            'direccion': cliente.direccion,
            'sucursal_registro_id': cliente.sucursal_registro_id
        }
        
        # Modificar el cliente
        cliente.nombre = form.nombre.data
        cliente.cedula = form.cedula.data
        cliente.telefono = form.telefono.data
        cliente.direccion = form.direccion.data
        if current_user.rol == 'ADMINISTRADOR' and hasattr(form, 'sucursal_id'):
            cliente.sucursal_registro_id = form.sucursal_id.data
        
        # Registrar auditoría (aún no se hace commit)
        registrar_auditoria(
            tabla='clientes',
            operacion='UPDATE',
            valores_anteriores=valores_anteriores,
            valores_nuevos={
                'id_cliente': cliente.id_cliente,
                'nombre': cliente.nombre,
                'cedula': cliente.cedula,
                'telefono': cliente.telefono,
                'direccion': cliente.direccion,
                'sucursal_registro_id': cliente.sucursal_registro_id
            }
        )
        db.session.commit()
        flash('Cliente actualizado correctamente', 'success')
        return redirect(url_for('gerente.listar_clientes'))
    
    return render_template('clientes/editar.html', form=form, cliente=cliente)
@gerente_bp.route('/clientes/<int:id>/eliminar', methods=['POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    verificar_permiso_escritura(cliente, columna_sucursal='sucursal_registro_id')
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado', 'success')
    return redirect(url_for('gerente.listar_clientes'))

# ============================================================
# MEDICAMENTOS
# ============================================================
@gerente_bp.route('/medicamentos')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE', 'FARMACEUTICO')
def listar_medicamentos():
    if current_user.rol == 'ADMINISTRADOR':
        medicamentos = MedicamentoPublic.query.all()
    else:
        medicamentos = MedicamentoPublic.query.filter_by(id_sucursal=current_user.id_sucursal).all()
    return render_template('medicamentos/listar.html', medicamentos=medicamentos)

@gerente_bp.route('/medicamentos/nuevo', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def nuevo_medicamento():
    form = MedicamentoForm()
    if current_user.rol == 'ADMINISTRADOR':
        form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
    else:
        form.sucursal_id.choices = [(current_user.id_sucursal, Sucursal.query.get(current_user.id_sucursal).nombre)]
        form.sucursal_id.data = current_user.id_sucursal
    if form.validate_on_submit():
        sucursal_id = form.sucursal_id.data if current_user.rol == 'ADMINISTRADOR' else current_user.id_sucursal
        medicamento = Medicamento(
            nombre=form.nombre.data,
            precio=form.precio.data,
            stock=form.stock.data,
            id_sucursal=sucursal_id
        )
        db.session.add(medicamento)
        db.session.commit()
        flash('Medicamento creado', 'success')
        return redirect(url_for('gerente.listar_medicamentos'))
    return render_template('medicamentos/crear.html', form=form)

@gerente_bp.route('/medicamentos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def editar_medicamento(id):
    medicamento = Medicamento.query.get_or_404(id)
    verificar_permiso_escritura(medicamento)
    form = MedicamentoForm(obj=medicamento)
    if current_user.rol == 'ADMINISTRADOR':
        form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
    if form.validate_on_submit():
        medicamento.nombre = form.nombre.data
        medicamento.precio = form.precio.data
        medicamento.stock = form.stock.data
        if current_user.rol == 'ADMINISTRADOR':
            medicamento.id_sucursal = form.sucursal_id.data
        db.session.commit()
        flash('Medicamento actualizado', 'success')
        return redirect(url_for('gerente.listar_medicamentos'))
    return render_template('medicamentos/editar.html', form=form, medicamento=medicamento)

@gerente_bp.route('/medicamentos/<int:id>/eliminar', methods=['POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def eliminar_medicamento(id):
    medicamento = Medicamento.query.get_or_404(id)
    verificar_permiso_escritura(medicamento)
    db.session.delete(medicamento)
    db.session.commit()
    flash('Medicamento eliminado', 'success')
    return redirect(url_for('gerente.listar_medicamentos'))

@gerente_bp.route('/medicamentos/<int:id>/stock', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE', 'FARMACEUTICO')
def actualizar_stock(id):
    medicamento = Medicamento.query.get_or_404(id)
    verificar_permiso_escritura(medicamento)
    if request.method == 'POST':
        nuevo_stock = request.form.get('stock', type=int)
        if nuevo_stock is not None and nuevo_stock >= 0:
            medicamento.stock = nuevo_stock
            db.session.commit()
            flash('Stock actualizado correctamente', 'success')
        else:
            flash('Stock inválido', 'danger')
        return redirect(url_for('gerente.listar_medicamentos'))
    return render_template('medicamentos/stock.html', medicamento=medicamento)

# ============================================================
# VENTAS
# ============================================================
@gerente_bp.route('/ventas')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def listar_ventas():
    if current_user.rol == 'ADMINISTRADOR':
        ventas = VentaPublic.query.all()
    else:
        ventas = VentaPublic.query.filter_by(id_sucursal=current_user.id_sucursal).all()
    return render_template('ventas/listar.html', ventas=ventas)

# ============================================================
# DASHBOARD GERENTE (mejorado)
# ============================================================
@gerente_bp.route('/dashboard')
@login_required
@roles_required('GERENTE', 'ADMINISTRADOR')
def dashboard():
    # Determinar filtro por sucursal (gerente solo ve la suya, admin puede ver todas)
    if current_user.rol == 'ADMINISTRADOR':
        sucursal_id = None
        sucursal_nombre = "Todas las sucursales"
        clientes_query = Cliente.query
        medicamentos_query = Medicamento.query
        ventas_query = Venta.query
        stock_bajo_query = Medicamento.query.filter(Medicamento.stock <= 5)
    else:
        sucursal_id = current_user.id_sucursal
        sucursal_obj = Sucursal.query.get(sucursal_id)
        sucursal_nombre = sucursal_obj.nombre if sucursal_obj else "Mi sucursal"
        clientes_query = Cliente.query.filter_by(sucursal_registro_id=sucursal_id)
        medicamentos_query = Medicamento.query.filter_by(id_sucursal=sucursal_id)
        ventas_query = Venta.query.filter_by(id_sucursal=sucursal_id)
        stock_bajo_query = Medicamento.query.filter(Medicamento.id_sucursal == sucursal_id, Medicamento.stock <= 5)

    # Estadísticas generales
    total_clientes = clientes_query.count()
    total_medicamentos = medicamentos_query.count()
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ventas_hoy = ventas_query.filter(Venta.fecha >= hoy).count()
    stock_bajo = stock_bajo_query.count()

    # Últimas ventas (5)
    if current_user.rol == 'ADMINISTRADOR':
        ventas_recientes = VentaPublic.query.order_by(VentaPublic.fecha.desc()).limit(5).all()
    else:
        ventas_recientes = VentaPublic.query.filter_by(id_sucursal=sucursal_id)\
                                            .order_by(VentaPublic.fecha.desc()).limit(5).all()

    # Productos con stock bajo (para lista)
    productos_stock_bajo = stock_bajo_query.all()

    # Top 5 medicamentos más vendidos
    top_meds = db.session.query(
        Medicamento.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta, Medicamento.id_medicamento == DetalleVenta.id_medicamento)\
     .join(Venta, DetalleVenta.id_venta == Venta.id_venta)
    if sucursal_id:
        top_meds = top_meds.filter(Venta.id_sucursal == sucursal_id)
    top_meds = top_meds.group_by(Medicamento.id_medicamento)\
                       .order_by(func.sum(DetalleVenta.cantidad).desc())\
                       .limit(5).all()

    top_nombres = [m[0] for m in top_meds]
    top_cantidades = [int(m[1]) for m in top_meds]

    # Ventas por mes (últimos 6 meses)
    meses_labels = []
    ventas_por_mes = []
    now = datetime.now()
    for i in range(5, -1, -1):
        fecha_inicio = datetime(now.year, now.month, 1) - timedelta(days=i*30)
        fecha_fin = fecha_inicio + timedelta(days=32)
        fecha_fin = datetime(fecha_fin.year, fecha_fin.month, 1)
        total = ventas_query.filter(Venta.fecha >= fecha_inicio, Venta.fecha < fecha_fin).count()
        meses_labels.append(fecha_inicio.strftime('%b %Y'))
        ventas_por_mes.append(total)

    return render_template('dashboard_gerente.html',
                           total_clientes=total_clientes,
                           total_medicamentos=total_medicamentos,
                           ventas_hoy=ventas_hoy,
                           stock_bajo=stock_bajo,
                           ventas_recientes=ventas_recientes,
                           productos_stock_bajo=productos_stock_bajo,
                           top_medicamentos_nombres=top_nombres,
                           top_medicamentos_cantidades=top_cantidades,
                           meses_labels=meses_labels,
                           ventas_por_mes=ventas_por_mes,
                           sucursal_nombre=sucursal_nombre)
@gerente_bp.route('/ventas/<int:id>')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def detalle_venta(id):
    from ...models.operativa.venta_public import VentaPublic
    from ...models.operativa.detalle_venta_public import DetalleVentaPublic
    venta = VentaPublic.query.get_or_404(id)
    detalles = DetalleVentaPublic.query.filter_by(id_venta=id).all()
    return render_template('ventas/detalle.html', venta=venta, detalles=detalles)