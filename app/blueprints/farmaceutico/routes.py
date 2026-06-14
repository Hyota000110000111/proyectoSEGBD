from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text, func
from datetime import datetime, timedelta
from . import farmaceutico_bp
from ...utils.decorators import roles_required
from ...utils.security import verificar_permiso_escritura
from ...extensions import db, csrf

# Modelos públicos (vistas) para lectura
from ...models.operativa.medicamento_public import MedicamentoPublic
from ...models.operativa.cliente_public import ClientePublic
from ...models.operativa.venta_public import VentaPublic

# Modelos reales (tablas) para escritura
from ...models.operativa.medicamento import Medicamento
from ...models.operativa.cliente import Cliente
from ...models.operativa.venta import Venta
from ...models.operativa.detalle_venta import DetalleVenta
from ...models.operativa.detalle_venta_public import DetalleVentaPublic
from ...models.operativa.sucursal import Sucursal

# ====================================================
# LISTAR MEDICAMENTOS
# ====================================================
@farmaceutico_bp.route('/medicamentos')
@login_required
@roles_required('FARMACEUTICO', 'GERENTE', 'ADMINISTRADOR', 'AUDITOR')
def listar_medicamentos():
    if current_user.rol in ('ADMINISTRADOR', 'AUDITOR'):
        medicamentos = MedicamentoPublic.query.all()
    else:
        medicamentos = MedicamentoPublic.query.filter_by(id_sucursal=current_user.id_sucursal).all()
    return render_template('farmaceutico/medicamentos.html', medicamentos=medicamentos)

# ====================================================
# ACTUALIZAR STOCK
# ====================================================
@farmaceutico_bp.route('/medicamentos/<int:id>/stock', methods=['GET', 'POST'])
@login_required
@roles_required('FARMACEUTICO', 'GERENTE', 'ADMINISTRADOR')
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
        return redirect(url_for('farmaceutico.listar_medicamentos'))
    return render_template('farmaceutico/stock.html', medicamento=medicamento)

# ====================================================
# FORMULARIO NUEVA VENTA (GET)
# ====================================================
@farmaceutico_bp.route('/ventas/nueva', methods=['GET'])
@login_required
@roles_required('FARMACEUTICO', 'GERENTE')
def nueva_venta_form():
    clientes = ClientePublic.query.filter_by(sucursal_registro_id=current_user.id_sucursal).all()
    medicamentos = MedicamentoPublic.query.filter_by(id_sucursal=current_user.id_sucursal).all()
    return render_template('ventas/crear.html', clientes=clientes, medicamentos=medicamentos)

# ====================================================
# REGISTRAR VENTA (POST)
# ====================================================
@farmaceutico_bp.route('/ventas/nueva', methods=['POST'])
@csrf.exempt
@login_required
@roles_required('FARMACEUTICO', 'GERENTE')
def registrar_venta():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No se recibieron datos JSON'}), 400

    id_cliente = data.get('id_cliente')
    items = data.get('items', [])
    if not id_cliente or not items:
        return jsonify({'error': 'Faltan datos (cliente o productos)'}), 400

    # Validar cliente
    cliente = Cliente.query.get(id_cliente)
    if not cliente or cliente.sucursal_registro_id != current_user.id_sucursal:
        return jsonify({'error': 'Cliente no pertenece a su sucursal'}), 400

    # Validar medicamentos
    for item in items:
        med = Medicamento.query.get(item.get('id_medicamento'))
        if not med or med.id_sucursal != current_user.id_sucursal:
            return jsonify({'error': f'Medicamento {item.get("id_medicamento")} no válido'}), 400
        if med.stock < item.get('cantidad', 0):
            return jsonify({'error': f'Stock insuficiente para {med.nombre}'}), 400

    try:
        from ...services.ventas_service import registrar_venta_con_procedimiento
        resultado = registrar_venta_con_procedimiento(
            id_cliente=id_cliente,
            id_empleado=current_user.id_empleado,
            id_sucursal=current_user.id_sucursal,
            items=items
        )
        return jsonify({'success': True, 'id_venta': resultado['id_venta'], 'total': str(resultado['total'])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ====================================================
# LISTAR VENTAS
# ====================================================
@farmaceutico_bp.route('/ventas')
@login_required
@roles_required('FARMACEUTICO', 'GERENTE', 'ADMINISTRADOR', 'AUDITOR')
def listar_ventas():
    if current_user.rol in ('ADMINISTRADOR', 'AUDITOR'):
        ventas = VentaPublic.query.order_by(VentaPublic.fecha.desc()).all()
    else:
        ventas = VentaPublic.query.filter_by(id_sucursal=current_user.id_sucursal).order_by(VentaPublic.fecha.desc()).all()
    return render_template('farmaceutico/ventas.html', ventas=ventas)

# ====================================================
# DETALLE DE VENTA
# ====================================================
@farmaceutico_bp.route('/ventas/<int:id>')
@login_required
@roles_required('FARMACEUTICO', 'GERENTE', 'ADMINISTRADOR', 'AUDITOR')
def detalle_venta(id):
    venta = VentaPublic.query.get_or_404(id)
    detalles = DetalleVentaPublic.query.filter_by(id_venta=id).all()
    return render_template('farmaceutico/detalle_venta.html', venta=venta, detalles=detalles)

# ====================================================
# DASHBOARD FARMACEUTICO (con estadísticas reales)
# ====================================================
@farmaceutico_bp.route('/dashboard')
@login_required
@roles_required('FARMACEUTICO', 'GERENTE', 'ADMINISTRADOR')
def dashboard():
    # ====================================================
    # 0. Estadísticas básicas para las tarjetas
    # ====================================================
    hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ventas_hoy = Venta.query.filter(
        Venta.id_sucursal == current_user.id_sucursal,
        Venta.fecha >= hoy
    ).count()
    
    total_meds = Medicamento.query.filter_by(id_sucursal=current_user.id_sucursal).count()
    stock_bajo = Medicamento.query.filter(
        Medicamento.id_sucursal == current_user.id_sucursal,
        Medicamento.stock <= 5
    ).count()
    
    # ====================================================
    # 1. Últimas ventas de la sucursal del farmacéutico
    # ====================================================
    ultimas_ventas = VentaPublic.query.filter_by(id_sucursal=current_user.id_sucursal)\
                                      .order_by(VentaPublic.fecha.desc())\
                                      .limit(5).all()
    
    # ====================================================
    # 2. Top 5 medicamentos más vendidos en su sucursal
    # ====================================================
    top_medicamentos = db.session.query(
        Medicamento.nombre,
        func.sum(DetalleVenta.cantidad).label('total_vendido')
    ).join(DetalleVenta, Medicamento.id_medicamento == DetalleVenta.id_medicamento)\
     .join(Venta, DetalleVenta.id_venta == Venta.id_venta)\
     .filter(Venta.id_sucursal == current_user.id_sucursal)\
     .group_by(Medicamento.id_medicamento)\
     .order_by(func.sum(DetalleVenta.cantidad).desc())\
     .limit(5).all()
    
    top_nombres = [m[0] for m in top_medicamentos]
    top_cantidades = [int(m[1]) for m in top_medicamentos]
    
    # ====================================================
    # 3. Ventas por sucursal (solo la suya, pero igual se pasa como lista)
    # ====================================================
    sucursal_nombre = Sucursal.query.get(current_user.id_sucursal).nombre
    sucursales_nombres = [sucursal_nombre]
    ventas_por_sucursal = [Venta.query.filter_by(id_sucursal=current_user.id_sucursal).count()]
    
    # ====================================================
    # 4. Tendencia de ventas últimos 6 meses (solo su sucursal)
    # ====================================================
    now = datetime.now()
    meses_labels = []
    ventas_por_mes = []
    
    for i in range(5, -1, -1):
        fecha_inicio = datetime(now.year, now.month, 1) - timedelta(days=i*30)
        fecha_fin = fecha_inicio + timedelta(days=32)
        fecha_fin = datetime(fecha_fin.year, fecha_fin.month, 1)
        
        total = Venta.query.filter(
            Venta.fecha >= fecha_inicio,
            Venta.fecha < fecha_fin,
            Venta.id_sucursal == current_user.id_sucursal
        ).count()
        meses_labels.append(fecha_inicio.strftime('%b %Y'))
        ventas_por_mes.append(total)
    
    # ====================================================
    # 5. Total de clientes en su sucursal
    # ====================================================
    total_clientes_sucursal = ClientePublic.query.filter_by(sucursal_registro_id=current_user.id_sucursal).count()
    
    return render_template('dashboard_farmaceutico.html',
                           ventas_hoy=ventas_hoy,
                           total_meds=total_meds,
                           stock_bajo=stock_bajo,
                           ultimas_ventas=ultimas_ventas,
                           top_medicamentos_nombres=top_nombres,
                           top_medicamentos_cantidades=top_cantidades,
                           sucursales_nombres=sucursales_nombres,
                           ventas_por_sucursal=ventas_por_sucursal,
                           meses_labels=meses_labels,
                           ventas_por_mes=ventas_por_mes,
                           total_clientes_sucursal=total_clientes_sucursal)