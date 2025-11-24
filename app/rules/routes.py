from flask import Blueprint, render_template
from app.extensions.utils import logged_in

rules_bp = Blueprint("rules", __name__)


@rules_bp.route("/rules", methods=["GET"])
@logged_in
def rules():
    return render_template("rules.html")