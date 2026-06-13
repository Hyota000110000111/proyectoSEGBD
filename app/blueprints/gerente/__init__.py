from flask import Blueprint 
gerente_bp = Blueprint('gerente', __name__, template_folder='templates') 
from . import routes 
