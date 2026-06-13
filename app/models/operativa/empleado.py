from app.extensions import db
from flask_login import UserMixin
from .sucursal import Sucursal

class Empleado(db.Model, UserMixin):
    __bind_key__ = 'operativa'
    __tablename__ = 'empleados'
    
    id_empleado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('FARMACEUTICO','GERENTE','AUDITOR','ADMINISTRADOR'), nullable=False)
    id_sucursal = db.Column(db.Integer, db.ForeignKey('sucursales.id_sucursal'), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación
    sucursal = db.relationship('Sucursal', backref='empleados', lazy=True)
    
    def get_id(self):
        return str(self.id_empleado)
    
    @property
    def is_active(self):
        return self.activo
    
    def tiene_permiso(self, roles_permitidos):
        return self.rol in roles_permitidos