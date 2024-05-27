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
            cursor.execute("SELECT * FROM sensor_readings ORDER BY timestamp ASC LIMIT 100")
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

        # Plantilla HTML a mostrar
        html = """
        <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Lecturas del Sensor de Humo</title>
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
                    body {
                        font-family: 'Roboto', sans-serif;
                        text-align: center;
                        background-color: #f4f4f9;
                        margin: 0;
                        padding: 0;
                    }
                    .header {
                        background-color: #15817D;
                        padding: 10px 0;
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .header img {
                        max-width: 100px;
                        height: auto;
                        margin-right: 20px;
                    }
                    h1 {
                        margin: 0;
                    }
                    .content {
                        width: 80%;
                        margin: 0 auto;
                    }
                    .table-container {
                        margin: 20px auto;
                        width: 100%;
                        overflow-x: auto;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                        font-size: 18px;
                        text-align: center;
                    }
                    th, td {
                        padding: 12px;
                        border: 1px solid #ddd;
                    }
                    th {
                        background-color: #15817D;
                        color: white;
                    }
                    .chart-container {
                        width: 100%;
                        margin: 20px auto;
                        overflow-x: auto;
                    }
                    .btn-refresh {
                        background-color: #15817D;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        cursor: pointer;
                        font-size: 16px;
                        margin-top: 20px;
                        border-radius: 5px;
                        transition: background-color 0.3s;
                        text-decoration: none;
                        display: inline-block;
                    }
                    .btn-refresh:hover {
                        background-color: #136b6a;
                    }
                    .delete-button {
                        background-color: #f44336;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        cursor: pointer;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 10px;
                        transition: background-color 0.3s;
                        display: inline-block;
                    }
                    .delete-button:hover {
                        background-color: #e53935;
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Monitor de Humo</h1>
                </div>
                <div class="content">
                    <div class="chart-container">
                        <canvas id="myChart"></canvas>
                    </div>
                    <a class="btn-refresh" href="/">Refrescar Datos</a>
                    <form action="/deleteData" method="post" style="display:inline;">
                        <button type="submit" class="delete-button">Eliminar Datos</button>
                    </form>
                    <h2>Gráfica de Valores del Sensor</h2>
                    <h2>Datos Recientes</h2>
                    <div class="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>Valor del Sensor (ppm)</th>
                                    <th>Fecha y Hora</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in rows %}
                                    <tr>
                                        <td>{{ row.value }}</td>
                                        <td>{{ row.timestamp }}</td>
                                    </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
                <script>
                    const data = {
                        labels: [{% for row in rows %}"{{ row.timestamp }}",{% endfor %}],
                        datasets: [{
                            label: 'Valor del Sensor (ppm)',
                            data: [{% for row in rows %}{{ row.value }},{% endfor %}],
                            borderColor: '#15817D',
                            fill: false,
                            tension: 0.1
                        }]
                    };
                    const config = {
                        type: 'line',
                        data: data,
                        options: {
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'Fecha y Hora'
                                    }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Valor del Sensor (ppm)'
                                    }
                                }
                            }
                        }
                    };
                    const myChart = new Chart(
                        document.getElementById('myChart'),
                        config
                    );
                </script>
            </body>
            </html>
        """
        return render_template_string(html, rows=rows)

    except Exception as e:
        print("Error al obtener datos de la base de datos:", e)
        return 'Error al obtener datos de la base de datos', 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
