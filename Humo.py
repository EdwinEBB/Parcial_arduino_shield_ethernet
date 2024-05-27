from flask import Flask, request, render_template_string, redirect, url_for
import pymysql
import datetime
import matplotlib.pyplot as plt
import io
import base64

# Configuración de la base de datos MySQL
DB_HOST = 'localhost'
DB_USER = 'root'  
DB_PASSWORD = ''  
DB_NAME = 'humo'

app = Flask(__name__)

@app.route('/saveData', methods=['GET'])
def save_data():
    value = request.args.get('value')

    if value is not None:
        try:
            # Conexión a la base de datos
            connection = pymysql.connect(host=DB_HOST,
                                         user=DB_USER,
                                         password=DB_PASSWORD,
                                         db=DB_NAME,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)

            # Insertar dato en la base de datos
            with connection.cursor() as cursor:
                sql = "INSERT INTO sensor_readings (value, timestamp) VALUES (%s, %s)"
                cursor.execute(sql, (int(value), datetime.datetime.now()))
                connection.commit()

            return 'Dato guardado en la base de datos'

        except Exception as e:
            print("Error al guardar en la base de datos:", e)
            return 'Error al guardar en la base de datos', 500

        finally:
            connection.close()
    else:
        return 'Error: Falta el parámetro "value"', 400

@app.route('/deleteData', methods=['POST'])
def delete_data():
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(host=DB_HOST,
                                     user=DB_USER,
                                     password=DB_PASSWORD,
                                     db=DB_NAME,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sensor_readings")
            connection.commit()

        return redirect(url_for('index'))

    except Exception as e:
        print("Error al eliminar datos de la base de datos:", e)
        return 'Error al eliminar datos de la base de datos', 500

    finally:
        connection.close()

@app.route('/')
def index():
    try:
        # Conexión a la base de datos
        connection = pymysql.connect(host=DB_HOST,
                                     user=DB_USER,
                                     password=DB_PASSWORD,
                                     db=DB_NAME,
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 100")
            rows = cursor.fetchall()

        # Extraer datos para la gráfica
        times = [row['timestamp'] for row in rows]
        values = [row['value'] for row in rows]

        # Crear la gráfica
        plt.figure(figsize=(10, 5))
        plt.plot(times, values, marker='o')
        plt.title('Lecturas del Sensor de Humo')
        plt.xlabel('Fecha y Hora')
        plt.ylabel('Valor del Sensor (ppm)')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Convertir la gráfica a una imagen en base64
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        # plantila HTML a mostrar
        html = """
        <html>
        <head>
            <title>Lecturas del Sensor de Humo</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
                body { font-family: 'Roboto', sans-serif; text-align: center; }
                table { margin: 0 auto; border-collapse: collapse; width: 50%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
                th { background-color: #15817D; color: white; }
                h1 { color: #333; }
                .refresh-button, .delete-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    cursor: pointer;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px;
                }
                .refresh-button:hover, .delete-button:hover {
                    background-color: #45a049;
                }
                .delete-button {
                    background-color: #f44336;
                }
                .delete-button:hover {
                    background-color: #e53935;
                }
            </style>
        </head>
        <body>
            <h1>Lecturas del Sensor de Humo</h1>
            <a class="refresh-button" href="/">Refrescar Datos</a>
            <form action="/deleteData" method="post" style="display:inline;">
                <button type="submit" class="delete-button">Eliminar Datos</button>
            </form>
            <h2>Gráfica de Valores del Sensor</h2>
            <img src="data:image/png;base64,{{ plot_url }}" />
            <h2>Datos Recientes</h2>
            <table>
                <tr>
                    <th>Valor del Sensor (ppm)</th>
                    <th>Fecha y Hora</th>
                </tr>
                {% for row in rows %}
                <tr>
                    <td>{{ row.value }}</td>
                    <td>{{ row.timestamp }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        return render_template_string(html, rows=rows, plot_url=plot_url)

    except Exception as e:
        print("Error al obtener datos de la base de datos:", e)
        return 'Error al obtener datos de la base de datos', 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0c.0.0', port=8000)
