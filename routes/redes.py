from flask import Blueprint, render_template

redes_bp = Blueprint("redes", __name__)


@redes_bp.route("/")
def inicio():
    return render_template("base.html", titulo="Canais e Automações")
