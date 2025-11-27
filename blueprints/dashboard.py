from flask import Blueprint, render_template
from db.models import Escenario, db, Comuna, Barrio, TipoEscenario
from sqlalchemy import func

bp = Blueprint('dashboard', __name__)


def sort_comuna_value(value: str):
    """
    Ordena las comunas de forma numérica (1..10) y deja los textos al final.
    Ejemplo: 1,2,3,...,10,'ZONA RURAL'
    """
    try:
        # Si se puede convertir a int, usamos ese valor directamente
        return (0, int(value))
    except ValueError:
        # Los textos van de últimos
        return (1, value)


@bp.route("/")
def home():
    """
    Dashboard principal:
    - Total de escenarios.
    - Conteo por comuna usando las tablas normalizadas.
    - Conteo por tipo de escenario para el gráfico de dona.
    """
    total = db.session.query(Escenario).count()

    rows = (
        db.session.query(
            Comuna.nombre.label("comuna"),
            func.count(Escenario.id).label("c"),
        )
        .join(Barrio, Barrio.comuna_id == Comuna.id)
        .join(Escenario, Escenario.barrio_id == Barrio.id)
        .group_by(Comuna.nombre)
        .all()
    )

    by_comuna = sorted(rows, key=lambda r: sort_comuna_value(r.comuna))
    labels_comunas = [r.comuna for r in by_comuna]
    data_comunas   = [r.c for r in by_comuna]

    tipos_data = (
        db.session.query(
            TipoEscenario.nombre,
            func.count(Escenario.id),
        )
        .join(Escenario, Escenario.tipo_escenario_id == TipoEscenario.id)
        .group_by(TipoEscenario.id)
        .order_by(TipoEscenario.nombre)
        .all()
    )

    tipos_labels = [nombre for nombre, _ in tipos_data]
    tipos_values = [cantidad for _, cantidad in tipos_data]

    return render_template(
        "dashboard.html",
        total=total,
        by_comuna=by_comuna,
        labels_comunas=labels_comunas,
        data_comunas=data_comunas,
        tipos_labels=tipos_labels,
        tipos_values=tipos_values,
    )