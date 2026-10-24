from flask import Flask, render_template
from config import Config

# Importação das rotas separadas
from routes.familia import familia_bp
from routes.produtos import produtos_bp
from routes.redes import redes_bp
from routes.configuracoes import config_bp

app = Flask(__name__)
app.config.from_object(Config)

# Registro dos Módulos (Blueprints)
app.register_blueprint(familia_bp, url_prefix="/familia")
app.register_blueprint(produtos_bp, url_prefix="/produtos")
app.register_blueprint(redes_bp, url_prefix="/redes")
app.register_blueprint(config_bp, url_prefix="/configuracoes")


@app.route("/")
def index():
    return render_template("index.html", company_name=app.config["COMPANY_NAME"])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
