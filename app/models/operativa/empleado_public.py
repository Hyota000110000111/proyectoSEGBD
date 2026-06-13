from app.extensions import db

class EmpleadoPublic(db.Model):
    __bind_key__ = 'operativa'
    __tablename__ = 'vw_empleados_public'
    # No necesitas definir __table_args__ porque es una vista
    id_empleado = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150))
    usuario = db.Column(db.String(50))
    rol = db.Column(db.Enum('FARMACEUTICO','GERENTE','AUDITOR','ADMINISTRADOR'))
    id_sucursal = db.Column(db.Integer)
    activo = db.Column(db.Boolean)