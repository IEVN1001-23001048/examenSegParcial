from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pizzeria_db'

mysql = MySQL(app)

@app.route('/pedidos', methods=['POST'])
def guardar_pedido():
    try:
        data = request.json
        nombre = data['nombre']
        direccion = data['direccion']
        telefono = data['telefono']
        dia_semana = data.get('dia_semana', 'lunes').lower()
        mes = data.get('mes', 'enero').lower()
        total = data['total']
        pizzas = data['pizzas']
        
        fecha_actual = datetime.now().strftime('%Y-%m-%d')

        cursor = mysql.connection.cursor()
        
        sql_pedido = """INSERT INTO pedidos (nombre, direccion, telefono, fecha, dia_semana, mes, total) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_pedido, (nombre, direccion, telefono, fecha_actual, dia_semana, mes, total))
        pedido_id = cursor.lastrowid

        for p in pizzas:
            sql_detalle = """INSERT INTO detalle_pedidos (idpedido, tamano, ingredientes, num_pizzas, subtotal) 
                             VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql_detalle, (pedido_id, p['tamano'], p['ingredientes'], p['num_pizzas'], p['subtotal']))

        mysql.connection.commit()
        cursor.close()
        return jsonify({'mensaje': 'Pedido guardado con éxito', 'total': total}), 201
    except Exception as e:
        print("Error en Flask:", str(e))
        return jsonify({'mensaje': str(e)}), 500

@app.route('/ventas/dia/<dia>', methods=['GET'])
def ventas_por_dia(dia):
    cursor = mysql.connection.cursor()
    # Seleccionamos también el idpedido para poder consultar su detalle específico
    cursor.execute("SELECT idpedido, nombre, total FROM pedidos WHERE dia_semana = %s", (dia.lower(),))
    resultados = cursor.fetchall()
    cursor.close()

    ventas = [{'idpedido': row[0], 'nombre': row[1], 'total': float(row[2])} for row in resultados]
    total_dia = sum(v['total'] for v in ventas)

    return jsonify({'ventas': ventas, 'total_dia': total_dia}), 200

@app.route('/ventas/mes/<mes>', methods=['GET'])
def ventas_por_mes(mes):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT idpedido, nombre, total FROM pedidos WHERE mes = %s", (mes.lower(),))
    resultados = cursor.fetchall()
    cursor.close()

    ventas = [{'idpedido': row[0], 'nombre': row[1], 'total': float(row[2])} for row in resultados]
    total_mes = sum(v['total'] for v in ventas)

    return jsonify({'ventas': ventas, 'total_mes': total_mes}), 200

@app.route('/pedido/detalle/<int:idpedido>', methods=['GET'])
def detalle_pedido(idpedido):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tamano, ingredientes, num_pizzas, subtotal FROM detalle_pedidos WHERE idpedido = %s", (idpedido,))
    resultados = cursor.fetchall()
    cursor.close()

    detalle = [{'tamano': row[0], 'ingredientes': row[1], 'num_pizzas': row[2], 'subtotal': float(row[3])} for row in resultados]
    return jsonify({'detalle': detalle}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)