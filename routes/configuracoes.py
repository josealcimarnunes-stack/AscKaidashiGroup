from flask import Blueprint, render_template

config_bp = Blueprint("configuracoes", __name__)


@config_bp.route("/")
def inicio():
    return render_template("base.html", titulo="Configurações e Logs")
