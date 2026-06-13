from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from . import gerente_bp
from ...utils.decorators import roles_required
from ...utils.security import verificar_permiso_por_sucursal, verificar_permiso_escritura
from ...extensions import db
from ...models.operativa.cliente_public import ClientePublic
from ...models.operativa.cliente import Cliente
from ...models.operativa.medicamento_public import MedicamentoPublic
from ...models.operativa.medicamento import Medicamento
from ...models.operativa.venta_public import VentaPublic
from ...models.operativa.venta import Venta
from ...models.operativa.sucursal import Sucursal
from ...forms.cliente import ClienteForm
from ...forms.medicamento import MedicamentoForm

# ====================== CLIENTES ======================

@gerente_bp.route('/clientes')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def listar_clientes():
    """Lista clientes según rol y sucursal"""
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
    # Asignar choices siempre
    if current_user.rol == 'ADMINISTRADOR':
        form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
    else:
        # Para gerente, solo su sucursal (y se puede ocultar en la plantilla)
        form.sucursal_id.choices = [(current_user.id_sucursal, Sucursal.query.get(current_user.id_sucursal).nombre)]
        form.sucursal_id.data = current_user.id_sucursal   # valor por defecto
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
    # Verificar que el cliente pertenezca a la sucursal del gerente (a menos que sea admin)
    verificar_permiso_escritura(cliente, columna_sucursal='sucursal_registro_id')
    
    form = ClienteForm(obj=cliente)
    # Asignar choices para sucursal_id (si el campo existe en el formulario)
    if hasattr(form, 'sucursal_id'):
        if current_user.rol == 'ADMINISTRADOR':
            form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
        else:
            # Para gerente, mostrar solo su sucursal y deshabilitar el campo (o usar hidden)
            form.sucursal_id.choices = [(current_user.id_sucursal, Sucursal.query.get(current_user.id_sucursal).nombre)]
            form.sucursal_id.data = current_user.id_sucursal
    
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.cedula = form.cedula.data
        cliente.telefono = form.telefono.data
        cliente.direccion = form.direccion.data
        if current_user.rol == 'ADMINISTRADOR' and hasattr(form, 'sucursal_id'):
            cliente.sucursal_registro_id = form.sucursal_id.data
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
# ====================== MEDICAMENTOS ======================

@gerente_bp.route('/medicamentos')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE', 'FARMACEUTICO')
def listar_medicamentos():
    """Listar medicamentos según rol y sucursal"""
    if current_user.rol == 'ADMINISTRADOR':
        medicamentos = MedicamentoPublic.query.all()
    else:
        medicamentos = MedicamentoPublic.query.filter_by(id_sucursal=current_user.id_sucursal).all()
    return render_template('medicamentos/listar.html', medicamentos=medicamentos)

@gerente_bp.route('/medicamentos/nuevo', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def nuevo_medicamento():
    from ...forms.medicamento import MedicamentoForm
    from ...models.operativa.sucursal import Sucursal

    form = MedicamentoForm()

    # Asignar choices según el rol
    if current_user.rol == 'ADMINISTRADOR':
        form.sucursal_id.choices = [(s.id_sucursal, s.nombre) for s in Sucursal.query.all()]
    else:
        # Gerente: solo su sucursal (se puede ocultar en la plantilla)
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
    """Editar medicamento (solo de su sucursal)"""
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
    from ...models.operativa.medicamento import Medicamento
    medicamento = Medicamento.query.get_or_404(id)
    verificar_permiso_escritura(medicamento)  # controla sucursal
    db.session.delete(medicamento)
    db.session.commit()
    flash('Medicamento eliminado', 'success')
    return redirect(url_for('gerente.listar_medicamentos'))

@gerente_bp.route('/medicamentos/<int:id>/stock', methods=['GET', 'POST'])
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE', 'FARMACEUTICO')
def actualizar_stock(id):
    """Actualizar stock de un medicamento (solo de su sucursal)"""
    medicamento = Medicamento.query.get_or_404(id)
    verificar_permiso_escritura(medicamento)
    if request.method == 'POST':
        nuevo_stock = request.form.get('stock', type=int)
        if nuevo_stock is not None and nuevo_stock >= 0:
            medicamento.stock = nuevo_stock
            db.session.commit()
            flash('Stock actualizado correctamente', 'success')
        else:
            flash('Stock inválido (debe ser un número positivo)', 'danger')
        return redirect(url_for('gerente.listar_medicamentos'))
    return render_template('medicamentos/stock.html', medicamento=medicamento)

# ====================== VENTAS ======================

@gerente_bp.route('/ventas')
@login_required
@roles_required('ADMINISTRADOR', 'GERENTE')
def listar_ventas():
    """Listar ventas según rol y sucursal"""
    if current_user.rol == 'ADMINISTRADOR':
        ventas = VentaPublic.query.all()
    else:
        ventas = VentaPublic.query.filter_by(id_sucursal=current_user.id_sucursal).all()
    return render_template('ventas/listar.html', ventas=ventas)
@gerente_bp.route('/dashboard')
@login_required
@roles_required('GERENTE')
def dashboard():
    return render_template('dashboard_gerente.html')