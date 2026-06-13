import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for
from flask_migrate import Migrate
from flask_login import current_user, login_required
from sqlalchemy import text

from .extensions import db, migrate, login_manager, bcrypt, csrf
from .config import DevelopmentConfig, ProductionConfig
from .blueprints.seguridad import seguridad_bp

# NOTA: Las importaciones de modelos se hacen dentro de las funciones o en los blueprints
# para evitar circular imports. No es necesario importar todos aquí.

def create_app(config_object=None):
    app = Flask(__name__)

    if config_object is None:
        config_class = DevelopmentConfig if os.getenv('FLASK_ENV') == 'development' else ProductionConfig
        app.config.from_object(config_class)
    else:
        app.config.from_object(config_object)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # User loader para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models.operativa.empleado import Empleado
        return Empleado.query.get(int(user_id))

    # Establecer variable de sesión @app_user_id antes de cada request
    @app.before_request
    def set_db_user():
        try:
            if current_user.is_authenticated:
                user = current_user.usuario
            else:
                user = 'ANONIMO'
            db.session.execute(text("SET @app_user_id = :user"), {"user": user})
        except Exception as e:
            app.logger.warning(f"No se pudo establecer @app_user_id: {e}")

    # Context processor para variables globales en plantillas (unificado)
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        alertas_no_leidas = 0
        alertas_recientes = []
        if current_user.is_authenticated:
            # Aquí puedes implementar la consulta real cuando tengas el modelo AlertaSeguridad
            # Por ahora se deja en 0 para evitar errores
            pass
        return {
            'alertas_no_leidas': alertas_no_leidas,
            'alertas_recientes': alertas_recientes,
            'now': datetime.now()
        }

    # Registrar blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.admin import admin_bp
    from .blueprints.gerente import gerente_bp
    from .blueprints.farmaceutico import farmaceutico_bp
    from .blueprints.auditor import auditor_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(gerente_bp, url_prefix='/gerente')
    app.register_blueprint(farmaceutico_bp, url_prefix='/farmaceutico')
    app.register_blueprint(auditor_bp, url_prefix='/auditor')
    app.register_blueprint(seguridad_bp, url_prefix='/seguridad')

    # ========================================================
    # RUTA PRINCIPAL (HOME)
    # ========================================================
    @app.route('/')
    def home():
        # Usuario no autenticado: mostrar landing page con medicamentos
        if not current_user.is_authenticated:
            from .models.operativa.medicamento_public import MedicamentoPublic
            medicamentos = MedicamentoPublic.query.all()
            return render_template('landing.html', medicamentos=medicamentos)
        
        # Usuario autenticado: redirigir según su rol
        if current_user.rol == 'ADMINISTRADOR':
            return redirect(url_for('admin.dashboard'))
        elif current_user.rol == 'GERENTE':
            return redirect(url_for('gerente.dashboard'))
        elif current_user.rol == 'FARMACEUTICO':
            return redirect(url_for('farmaceutico.dashboard'))
        elif current_user.rol == 'AUDITOR':
            return redirect(url_for('auditor.dashboard'))
        else:
            # Fallback: mostrar base.html
            return render_template('base.html')

    # Manejadores de error
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    return app