from ..extensions import db
from sqlalchemy import text
import json

def registrar_venta_con_procedimiento(id_cliente, id_empleado, id_sucursal, items):
    items_json = json.dumps(items)
    sql = text("CALL sp_insertar_venta(:p_id_cliente, :p_id_empleado, :p_id_sucursal, :p_items)")
    result = db.session.execute(sql, {
        'p_id_cliente': id_cliente,
        'p_id_empleado': id_empleado,
        'p_id_sucursal': id_sucursal,
        'p_items': items_json
    })
    db.session.commit()
    row = result.fetchone()
    return {'id_venta': row[0], 'total': float(row[1])}