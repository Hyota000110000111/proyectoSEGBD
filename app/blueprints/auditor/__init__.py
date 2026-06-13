from flask import Blueprint 
auditor_bp = Blueprint('auditor', __name__, template_folder='templates') 
from . import routes 
