from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=150)])
    cedula = StringField('Cédula', validators=[DataRequired(), Length(max=20)])
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    direccion = StringField('Dirección', validators=[Length(max=200)])
    sucursal_id = SelectField('Sucursal', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')