from flask import Blueprint, render_template
from db.models import Escenario, db
from sqlalchemy import text

bp = Blueprint('dashboard', __name__)


def sort_comuna_value(value: str):
    """Ordena primero comunas numéricas (1..10) y luego textos (ZONA RURAL)."""
    if value is None:
        return (2, '')
    v = str(value).strip()
    return (0, int(v)) if v.isdigit() else (1, v)


@bp.route('/')
def home():
    total = db.session.query(Escenario).count()

    # Recuento por comuna
    rows = db.session.execute(text("""
        SELECT comuna, COUNT(*) AS c
        FROM escenarios
        GROUP BY comuna
    """)).mappings().all()

    # Ordenar comunas (1..10, luego textos como ZONA RURAL)
    by_comuna = sorted(rows, key=lambda r: sort_comuna_value(r['comuna']))

    # Listas para las gráficas
    labels_comunas = [r['comuna'] for r in by_comuna]
    data_comunas = [r['c'] for r in by_comuna]

    return render_template(
        'dashboard.html',
        total=total,
        by_comuna=by_comuna,
        labels_comunas=labels_comunas,
        data_comunas=data_comunas
    )
