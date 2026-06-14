# app/utils/audit.py
from flask import request
from flask_login import current_user
from ..extensions import db
from ..models.auditoria_log import AuditoriaLog
import json

def registrar_auditoria(tabla, operacion, valores_anteriores=None, valores_nuevos=None):
    """
    Registra una acción en la tabla auditoria_log.
    
    Args:
        tabla (str): Nombre de la tabla afectada.
        operacion (str): 'INSERT', 'UPDATE' o 'DELETE'.
        valores_anteriores (dict, optional): Estado anterior del registro (para UPDATE/DELETE).
        valores_nuevos (dict, optional): Estado nuevo del registro (para INSERT/UPDATE).
    """
    try:
        usuario = current_user.usuario if current_user.is_authenticated else 'SISTEMA'
        ip = request.remote_addr if request else None

        log = AuditoriaLog(
            usuario_real=usuario,
            tabla_afectada=tabla,
            operacion=operacion,
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos,
            ip_origen=ip
        )
        db.session.add(log)
        db.session.flush()  # No hacer commit aún, se hará al final de la transacción principal
    except Exception as e:
        # Evitar que un error de auditoría rompa la operación principal
        print(f"Error al registrar auditoría: {e}")

def audit_decorator(tabla):
    """
    Decorador para registrar automáticamente auditoría en funciones que manejan escritura.
    Espera que la función retorne un diccionario con 'operacion', 'valores_anteriores' y 'valores_nuevos'.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if result and isinstance(result, dict):
                registrar_auditoria(
                    tabla=tabla,
                    operacion=result.get('operacion'),
                    valores_anteriores=result.get('valores_anteriores'),
                    valores_nuevos=result.get('valores_nuevos')
                )
            return result
        return wrapper
    return decorator