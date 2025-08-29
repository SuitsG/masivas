from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuracion de la API base
API_BASE = os.getenv('API_BASE', 'http://localhost:8080')

@app.route('/')
def index():
    """Pagina principal"""
    return render_template('index.html')

@app.route('/mundo')
def mundo():
    """Pagina del modulo mundo"""
    return render_template('mundo.html')

@app.route('/hojaVida')
def hoja_vida():
    """Pagina del modulo hoja de vida"""
    return render_template('hoja_vida.html')

@app.route('/historialFactura')
def historial_factura():
    """Pagina del modulo historial factura"""
    return render_template('historial_factura.html')

@app.route('/api/<path:path>', methods=['GET', 'POST'])
def proxy_api(path):
    """Proxy para reenviar peticiones a la API externa y evitar CORS"""
    try:
        # Construir URL completa de la API
        api_url = f"{API_BASE}/{path}"
        
        # Preparar headers minimos
        headers = {}
        if request.content_type:
            headers['Content-Type'] = request.content_type
        
        # Manejar peticion GET
        if request.method == 'GET':
            response = requests.get(
                api_url,
                params=request.args,
                headers=headers,
                timeout=30
            )
        
        # Manejar peticion POST
        elif request.method == 'POST':
            if request.content_type and 'application/json' in request.content_type:
                # Enviar como JSON
                json_data = request.get_json(silent=True)
                response = requests.post(
                    api_url,
                    json=json_data,
                    headers=headers,
                    timeout=30
                )
            else:
                # Enviar como form-data
                response = requests.post(
                    api_url,
                    data=request.form,
                    files=request.files,
                    headers=headers,
                    timeout=30
                )
        
        # Preparar respuesta
        response_headers = {}
        if 'content-type' in response.headers:
            response_headers['Content-Type'] = response.headers['content-type']
        
        return response.text, response.status_code, response_headers
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout al conectar con la API"}), 502
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Error de conexion con la API"}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error en la peticion: {str(e)}"}), 502
    except Exception as e:
        return jsonify({"error": f"Error interno del proxy: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
