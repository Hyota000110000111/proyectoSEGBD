from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from . import auth_bp
from ...extensions import db, bcrypt
from ...models.operativa.empleado import Empleado
from ...models.password_reset_token import PasswordResetToken
from ...forms.auth import LoginForm, CambioPasswordForm, SolicitarRecuperacionForm, ResetPasswordForm
from ...utils.security import create_reset_token

# ====================== LOGIN ======================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        empleado = Empleado.query.filter_by(usuario=form.usuario.data).first()
        if empleado and bcrypt.check_password_hash(empleado.password_hash, form.password.data):
            login_user(empleado, remember=form.remember.data)
            flash(f'Bienvenido {empleado.nombre}', 'success')
            
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/auth/'):
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('auth/login.html', form=form)

# ====================== LOGOUT ======================
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))

# ====================== CAMBIAR CONTRASEÑA ======================
@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    form = CambioPasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password_hash, form.actual_password.data):
            nuevo_hash = bcrypt.generate_password_hash(form.nueva_password.data).decode('utf-8')
            current_user.password_hash = nuevo_hash
            db.session.commit()
            flash('Contraseña actualizada correctamente', 'success')
            return redirect(url_for('home'))
        else:
            flash('Contraseña actual incorrecta', 'danger')
    return render_template('auth/cambiar_password.html', form=form)

# ====================== SOLICITAR RECUPERACIÓN ======================
@auth_bp.route('/recuperar', methods=['GET', 'POST'])
def recuperar():
    form = SolicitarRecuperacionForm()
    if form.validate_on_submit():
        empleado = Empleado.query.filter_by(usuario=form.usuario.data).first()
        if empleado:
            token = create_reset_token(empleado.id_empleado)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print(f"*** Enlace de recuperación: {reset_url} ***")
            flash(f'Se ha generado un enlace de recuperación. Revisa la consola del servidor o haz clic en el siguiente enlace: <a href="{reset_url}">{reset_url}</a>', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('No existe un usuario con ese nombre.', 'danger')
    return render_template('auth/recuperar.html', form=form)

# ====================== RESTABLECER CONTRASEÑA ======================
@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_record = PasswordResetToken.query.filter_by(token=token, usado=False).first()
    if not reset_record or reset_record.expiracion < datetime.utcnow():
        flash('El enlace de recuperación es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        empleado = Empleado.query.get(reset_record.id_empleado)
        if empleado:
            empleado.password_hash = bcrypt.generate_password_hash(form.nueva_password.data).decode('utf-8')
            reset_record.usado = True
            db.session.commit()
            flash('Contraseña actualizada. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Usuario no encontrado.', 'danger')
    return render_template('auth/reset_password.html', form=form, token=token)