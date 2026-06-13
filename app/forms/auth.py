from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
import re

class LoginForm(FlaskForm):
    usuario = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class CambioPasswordForm(FlaskForm):
    actual_password = PasswordField('Contraseña actual', validators=[DataRequired()])
    nueva_password = PasswordField('Nueva contraseña', validators=[
        DataRequired(), Length(min=8, message='Mínimo 8 caracteres'),
        EqualTo('confirmar', message='Las contraseñas no coinciden')
    ])
    confirmar = PasswordField('Confirmar nueva contraseña')
    submit = SubmitField('Cambiar contraseña')

    def validate_nueva_password(self, field):
        if not re.search(r'[A-Z]', field.data):
            raise ValidationError('Debe contener al menos una mayúscula')
        if not re.search(r'[0-9]', field.data):
            raise ValidationError('Debe contener al menos un número')
class SolicitarRecuperacionForm(FlaskForm):
    usuario = StringField('Nombre de usuario', validators=[DataRequired()])
    submit = SubmitField('Enviar enlace de recuperación')

class ResetPasswordForm(FlaskForm):
    nueva_password = PasswordField('Nueva contraseña', validators=[
        DataRequired(), Length(min=8, message='Mínimo 8 caracteres'),
        EqualTo('confirmar', message='Las contraseñas no coinciden')
    ])
    confirmar = PasswordField('Confirmar nueva contraseña')
    submit = SubmitField('Restablecer contraseña')
class SolicitarRecuperacionForm(FlaskForm):
    usuario = StringField('Nombre de Usuario', validators=[DataRequired()])
    submit = SubmitField('Enviar enlace de recuperación')
    