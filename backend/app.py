from flask import Flask, jsonify
from routes.partidos import partidos_bp

app = Flask(__name__)

app.register_blueprint(partidos_bp)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "mensaje": "¡API del ProDe Mundial 2026 funcionando!",
        "estado": "OK"
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)