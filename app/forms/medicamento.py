from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class MedicamentoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=150)])
    precio = DecimalField('Precio', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    sucursal_id = SelectField('Sucursal', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')