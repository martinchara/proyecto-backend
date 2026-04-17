from flask import Blueprint, jsonify, request
from db import obtener_conexion

partidos_bp = Blueprint("partidos", __name__)



@partidos_bp.route('/partidos', methods=['POST'])
def crear_partido():
    datos = request.get_json(silent=True)
    campos_requeridos = {"equipo_local", "equipo_visitante", "fecha", "fase"}
    if not datos:
        return jsonify({"error": "Faltan datos requeridos"}), 400
    
    conn= obtener_conexion()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (datos["equipo_local"], datos["equipo_visitante"], datos["fecha"], datos["fase"]))
        conn.commit()
        return "" , 201
    except Exception as e:
        return jsonify({"error": f"Error al crear partido: {e}"}), 500
    finally:
        cursor.close()
        conn.close()


@partidos_bp.route('/partidos/<int:id>"', methods=['GET'])
def obtener_partidos(id):
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    try:
        query = "SELECT * FROM partidos WHERE id = %s"
        cursor.execute(query, (id,))
        partido = cursor.fetchone()
        if partido:
            return jsonify(partido), 200
        else:
            return jsonify({"error": "Partido no encontrado"}), 404
    except Exception as e:
        print(f"Error al obtener partido: {e}")
        return jsonify({"error": "Error al obtener partido"}), 500
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
            return jsonify({"error": "Partido no encontrado"}), 404
        
    finally:
        cursor.close()
        conn.close()

@partidos_bp.route('/partidos/<int:id>', methods=['PUT'])
def remplazar_partido(id):
    datos = request.get_json(silent=True)
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        query = "UPDATE partidos SET equipo_local = %s, equipo_visitante =%s, fecha = %s, fase = %s WHERE id = %s"
        cursor.execute(query, (datos["equipo_local"], datos["equipo_visitante"], datos["fecha"], datos["fase"], id))
        conn.commit()
        if cursor.rowcount > 0:
            return "" , 204
        else:
            return jsonify({"error": "Partido no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Error al actualizar partido"}), 500
    finally:
        cursor.close()
        conn.close()

@partidos_bp.route('/partidos/<int:id>', methods=['PATCH'])
def actualizar_partido(id):
    datos = request.get_json(silent=True)
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
            return jsonify({"error": "No se proporcionaron campos para actualizar"}), 400
        valores.append(id)
        query = f"UPDATE partidos SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, valores)
        conn.commit()
        if cursor.rowcount > 0:
            return "" , 204
        else:
            return jsonify({"error": "Partido no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": "Error al actualizar partido"}), 500
    finally:
        cursor.close()
        conn.close()


                

        



