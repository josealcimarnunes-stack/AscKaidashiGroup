from flask import Blueprint, render_template

produtos_bp = Blueprint("produtos", __name__)


@produtos_bp.route("/")
def inicio():
    return render_template("base.html", titulo="Gestão de Produtos e Links")
