import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar .env desde la raíz del proyecto (con ruta explícita)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # SECRET_KEY con valor por defecto para desarrollo
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-para-desarrollo')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # URLs con valores por defecto amigables (usuario root sin contraseña)
    OPERATIVA_URL = os.getenv('DATABASE_OPERATIVA_URL', 'mysql+pymysql://root@localhost/farmasegura_operativa')
    SEGURIDAD_URL = os.getenv('DATABASE_SEGURIDAD_URL', 'mysql+pymysql://root@localhost/farmasegura_seguridad')
    
    SQLALCHEMY_BINDS = {
        'operativa': OPERATIVA_URL,
        'seguridad': SEGURIDAD_URL
    }
    SQLALCHEMY_DATABASE_URI = OPERATIVA_URL

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False