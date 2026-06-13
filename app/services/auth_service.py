from ..extensions import db
from ..models.intento_login import IntentoLogin
from datetime import datetime, timedelta

def registrar_intento(usuario, ip, exitoso):
    intento = IntentoLogin(usuario=usuario, ip_origen=ip, exitoso=exitoso)
    db.session.add(intento)
    db.session.commit()

def verificar_bloqueo(usuario, ip, limite=3, minutos_bloqueo=5):
    tiempo_limite = datetime.now() - timedelta(minutes=minutos_bloqueo)
    fallidos = IntentoLogin.query.filter(
        IntentoLogin.usuario == usuario,
        IntentoLogin.ip_origen == ip,
        IntentoLogin.exitoso == False,
        IntentoLogin.fecha_hora >= tiempo_limite
    ).count()
    return fallidos >= limite