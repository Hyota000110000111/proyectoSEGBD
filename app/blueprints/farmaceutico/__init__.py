from flask import Blueprint 
farmaceutico_bp = Blueprint('farmaceutico', __name__, template_folder='templates') 
from . import routes 
