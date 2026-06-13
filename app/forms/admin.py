# app/forms/admin.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import re

class UsuarioForm(FlaskForm):
    nombre = StringField('Nombre completo', validators=[DataRequired(), Length(max=150)])
    usuario = StringField('Usuario', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Contraseña', validators=[
        DataRequired(), Length(min=8, message='Mínimo 8 caracteres'),
        EqualTo('confirmar', message='Las contraseñas no coinciden')
    ])
    confirmar = PasswordField('Confirmar contraseña')
    rol = SelectField('Rol', choices=[
        ('FARMACEUTICO', 'Farmacéutico'),
        ('GERENTE', 'Gerente'),
        ('AUDITOR', 'Auditor'),
        ('ADMINISTRADOR', 'Administrador')
    ], validators=[DataRequired()])
    id_sucursal = SelectField('Sucursal', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')

    def validate_password(self, field):
        if not re.search(r'[A-Z]', field.data):
            raise ValidationError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[0-9]', field.data):
            raise ValidationError('La contraseña debe contener al menos un número')