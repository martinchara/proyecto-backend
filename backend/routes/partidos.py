from flask import Blueprint, jsonify, request
from db import obtener_conexion

partidos_bp = Blueprint("partidos", __name__)

FASES_VALIDAS = {"grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"}

def codigo_error(codigo, mensaje, descripcion, nivel= "error"):
    return jsonify({
        "code": codigo,
        "message": mensaje,
        "description": descripcion,
        "level": nivel
    }), codigo


@partidos_bp.route('/partidos', methods=['GET'])
def listar_partidos():
   
    equipo = request.args.get("equipo")
    fecha = request.args.get("fecha")
    fase = request.args.get("fase")
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)

    
    if limit < 1 or offset < 0:
        return codigo_error(400, "Bad_Request", "Los parámetros limit debe ser mayor a 0 y offset no puede ser negativo")
    
    if fase and fase not in FASES_VALIDAS:
        return codigo_error(400, "Bad_Request", f"La fase debe ser una de: {', '.join(FASES_VALIDAS)}")

    query = "SELECT * FROM partidos"
    condiciones = []
    valores = []

    if equipo:
        condiciones.append("(equipo_local = %s OR equipo_visitante = %s)")
        valores.extend([equipo, equipo])
    if fecha:
        condiciones.append("fecha = %s")
        valores.append(fecha)
    if fase:
        condiciones.append("fase = %s")
        valores.append(fase)
    if condiciones:
        query += " WHERE " + " AND ".join(condiciones)
    
    query_count = query.replace("SELECT *", "SELECT COUNT(*) as total")
    query += " ORDER BY fecha ASC LIMIT %s OFFSET %s"

    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query_count, valores)
        total = cursor.fetchone()["total"]

        if total == 0:
            return jsonify({
                "partidos": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }), 200

        cursor.execute(query, valores + [limit, offset])
        partidos = cursor.fetchall()
    except Exception as e:
        print(f"Error al listar partidos: {e}")
        return codigo_error(500, "Internal_Server_Error", "Ocurrió un error al listar los partidos")
    finally:
        cursor.close()
        conn.close()

    last_offset = max(0, ((total - 1) // limit) * limit)
    links = {
        "_first": {"href": f"{request.base_url}?_limit={limit}&_offset=0"},
        "_last":  {"href": f"{request.base_url}?_limit={limit}&_offset={last_offset}"},
    }
    if offset > 0:
        links["_prev"] = {"href": f"{request.base_url}?_limit={limit}&_offset={max(0, offset - limit)}"}
    if offset + limit < total:
        links["_next"] = {"href": f"{request.base_url}?_limit={limit}&_offset={offset + limit}"}

    return jsonify({
        "partidos": [{**p, "fecha": str(p["fecha"])} for p in partidos],
        "_links": links
    }), 200
    





@partidos_bp.route('/partidos', methods=['POST'])
def crear_partido():
    datos = request.get_json(silent=True)
    campos_requeridos = {"equipo_local", "equipo_visitante", "fecha", "fase"}
    
    if not datos or not campos_requeridos.issubset(datos.keys()):
        return codigo_error(400, "Bad_Request", "Los datos requeridos para crear un partido son incorrectos")

    if datos["fase"] not in FASES_VALIDAS:
        return codigo_error(400, "Bad_Request", f"La fase debe ser una de: {', '.join(FASES_VALIDAS)}")

    conn= obtener_conexion()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (datos["equipo_local"], datos["equipo_visitante"], datos["fecha"], datos["fase"]))
        conn.commit()
        return "Created" , 201
    except Exception as e:
        return codigo_error(500, "Internal_Server_Error", "Ocurrió un error al crear el partido")
    finally:
        cursor.close()
        conn.close()


@partidos_bp.route('/partidos/<int:id>', methods=['GET'])
def obtener_partido(id):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM partidos WHERE id = %s"
        cursor.execute(query, (id,))
        partido = cursor.fetchone()
        if partido:
            partido["fecha"] = str(partido["fecha"])
            return jsonify(partido), 200
        
        else:
            return codigo_error(404, "Not_Found", "Partido no encontrado")
    except Exception as e:
        print(f"Error al obtener partido: {e}")
        return codigo_error(500, "Internal_Server_Error", "Ocurrió un error al obtener el partido")
    finally:
        cursor.close()
        conn.close()

@partidos_bp.route('/partidos/<int:id>', methods=['DELETE'])
def eliminar_partido(id):
    conn = obtener_conexion()
    cursor = conn.cursor()


    try:
        query = "DELETE FROM partidos WHERE id = %s"
        cursor.execute(query, (id,))
        conn.commit()
        if cursor.rowcount > 0:
            return "" , 204
        else:
            return codigo_error(404, "Not_Found", "Partido no encontrado")
        
    finally:
        cursor.close()
        conn.close()

@partidos_bp.route('/partidos/<int:id>', methods=['PUT'])
def remplazar_partido(id):
    datos = request.get_json(silent=True)
    campos_requeridos = {"equipo_local", "equipo_visitante", "fecha", "fase"}

    if not datos or not campos_requeridos.issubset(datos.keys()):
        return codigo_error(400, "Bad_Request", "Los datos requeridos para actualizar un partido son incorrectos")
    
    if datos["fase"] not in FASES_VALIDAS:
        return codigo_error(400, "Bad_Request", f"La fase debe ser una de: {', '.join(FASES_VALIDAS)}")


    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        query = "UPDATE partidos SET equipo_local = %s, equipo_visitante =%s, fecha = %s, fase = %s WHERE id = %s"
        cursor.execute(query, (datos["equipo_local"], datos["equipo_visitante"], datos["fecha"], datos["fase"], id))
        conn.commit()
        if cursor.rowcount > 0:
            return "" , 204
        else:
            return codigo_error(404, "Not_Found", "Partido no encontrado")
    except Exception as e:
        return codigo_error(500, "Internal_Server_Error", "Ocurrió un error al actualizar el partido")
    finally:
        cursor.close()
        conn.close()

@partidos_bp.route('/partidos/<int:id>', methods=['PATCH'])
def actualizar_partido(id):
    datos = request.get_json(silent=True)
    
    if not datos:
        return codigo_error(400, "Bad_Request", "No se proporcionaron datos para actualizar el partido")
    if datos["fase"] not in FASES_VALIDAS:
        return codigo_error(400, "Bad_Request", f"La fase debe ser una de: {', '.join(FASES_VALIDAS)}")

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        campos = []
        valores = []
        for campo in ["equipo_local", "equipo_visitante", "fecha", "fase"]:
            if campo in datos:
                campos.append(f"{campo} = %s")
                valores.append(datos[campo])

        if not campos:
            return codigo_error(400, "Bad_Request", "No se proporcionaron campos para actualizar")  
        valores.append(id)
        query = f"UPDATE partidos SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        if cursor.rowcount > 0:
            return "" , 204
        else:
            return codigo_error(404, "Not_Found", "Partido no encontrado")
    except Exception as e:
        return codigo_error(500, "Internal_Server_Error", "Ocurrió un error al actualizar el partido")
    finally:
        cursor.close()
        conn.close()


                
@partidos_bp.route('/partidos/<int:id>/resultado', methods=['POST'])
def caragar_resultado(id):
    datos = request.get_json(silent=True)
    campos_requeridos = {"goles_local", "goles_visitante"}

    if not datos or not campos_requeridos.issubset(datos.keys()):
        return codigo_error(400, "Bad_Request", "Los datos requeridos para cargar el resultado son incorrectos")
    
    if not isinstance(datos["goles_local"], int) or not isinstance(datos["goles_visitante"], int):
        return codigo_error(400, "Bad_Request", "Los goles deben ser números enteros")
    
    if datos["goles_local"] < 0 or datos["goles_visitante"] < 0:
        return codigo_error(400, "Bad_Request", "Los goles no pueden ser negativos")
    
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        query = "UPDATE partidos SET goles_local = %s, goles_visitante = %s WHERE id = %s"
        cursor.execute(query, (datos["goles_local"], datos["goles_visitante"], id))
        conn.commit()
        if cursor.rowcount > 0:
            return "" , 204
        else:
            return codigo_error(404, "Not_Found", "Partido no encontrado")
    except Exception as e:
        return codigo_error(500, "Internal_Server_Error", "Ocurrió un error al cargar el resultado del partido")
    finally:
        cursor.close()
        conn.close()



        



