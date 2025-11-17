from flask import Blueprint, render_template
from db.models import Escenario, db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def home():
    total = db.session.query(Escenario).count()
    by_comuna = db.session.execute(
        db.text("SELECT comuna, COUNT(*) c FROM escenarios GROUP BY comuna ORDER BY comuna")
    ).mappings().all()
    return render_template('dashboard.html', total=total,by_comuna=by_comuna)