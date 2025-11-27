from flask import Blueprint, render_template, request, redirect, url_for, send_file, Response
from db.models import Escenario, db, Comuna, Barrio, TipoEscenario
import pandas as pd
import io
import math
from weasyprint import HTML
import tempfile

bp = Blueprint('escenarios', __name__)


def sort_comuna_value(value: str):
    """Ordena primero comunas numéricas (1..10) y luego textos (ZONA RURAL)."""
    if value is None:
        return (2, '')
    v = str(value).strip()
    return (0, int(v)) if v.isdigit() else (1, v)


@bp.get('/')
def list_esc():
    """
    Listado de escenarios con filtro por comuna (normalizada) y paginación.
    """
    # --- parámetros de filtro / paginación ---
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    if per_page not in (10, 25, 50):
        per_page = 10

    comuna_id = request.args.get('comuna_id', default=None, type=int)

    # Comunas disponibles para el dropdown (orden numérico y luego textos)
    comunas = Comuna.query.all()
    comunas = sorted(
        comunas,
        key=lambda c: sort_comuna_value(c.nombre)
    )

    # Query base: join para poder filtrar/ordenar por comuna
    query = (
        Escenario.query
        .join(Escenario.barrio)
        .join(Barrio.comuna)
    )

    if comuna_id:
        query = query.filter(Comuna.id == comuna_id)

    escenarios_all = query.all()

    # Orden (1..10, luego textos) usando la propiedad .comuna
    escenarios_all_sorted = sorted(
        escenarios_all,
        key=lambda e: sort_comuna_value(e.comuna) + (e.id,)
    )

    # Paginación manual
    total = len(escenarios_all_sorted)
    pages = max(1, math.ceil(total / per_page)) if total else 1
    if page < 1:
        page = 1
    if page > pages:
        page = pages

    start = (page - 1) * per_page
    end = start + per_page
    escenarios_page = escenarios_all_sorted[start:end]

    return render_template(
        'escenarios_list.html',
        data=escenarios_page,
        comunas=comunas,
        comuna_seleccionada=comuna_id,
        page=page,
        pages=pages,
        per_page=per_page,
        total=total,
    )



@bp.get('/new')
def new_form():
    """
    Formulario para crear un nuevo escenario.
    """
    comunas = Comuna.query.order_by(Comuna.nombre).all()
    barrios = Barrio.query.order_by(Barrio.nombre).all()
    tipos = TipoEscenario.query.order_by(TipoEscenario.nombre).all()
    return render_template(
        'escenarios_form.html',
        item=None,
        comunas=comunas,
        barrios=barrios,
        tipos=tipos
    )


@bp.post('/new')
def create():
    """
    Crea un nuevo escenario usando barrio y tipo como FK.
    """
    nombre = request.form['nombre']
    direccion = request.form.get('direccion', '')
    url_maps = request.form.get('url_maps', '') or None

    barrio_id = request.form.get('barrio_id')
    tipo_id = request.form.get('tipo_escenario_id') or None

    if not barrio_id:
        # En un caso real se debería manejar con validación
        return "Debes seleccionar un barrio", 400

    barrio = Barrio.query.get_or_404(int(barrio_id))
    tipo = TipoEscenario.query.get(int(tipo_id)) if tipo_id else None

    e = Escenario(
        nombre=nombre,
        direccion=direccion,
        url_maps=url_maps,
        barrio=barrio,
        tipo=tipo
    )
    db.session.add(e)
    db.session.commit()
    return redirect(url_for('.list_esc'))


@bp.get('/<int:id>/edit')
def edit_form(id):
    """
    Formulario de edición de escenario.
    """
    item = Escenario.query.get_or_404(id)
    comunas = Comuna.query.order_by(Comuna.nombre).all()
    barrios = Barrio.query.order_by(Barrio.nombre).all()
    tipos = TipoEscenario.query.order_by(TipoEscenario.nombre).all()
    return render_template(
        'escenarios_form.html',
        item=item,
        comunas=comunas,
        barrios=barrios,
        tipos=tipos
    )


@bp.post('/<int:id>/edit')
def update(id):
    """
    Actualiza un escenario existente.
    """
    e = Escenario.query.get_or_404(id)

    e.nombre = request.form['nombre']
    e.direccion = request.form.get('direccion', '')
    e.url_maps = request.form.get('url_maps', '') or None

    barrio_id = request.form.get('barrio_id')
    tipo_id = request.form.get('tipo_escenario_id') or None

    if not barrio_id:
        return "Debes seleccionar un barrio", 400

    e.barrio = Barrio.query.get_or_404(int(barrio_id))
    e.tipo = TipoEscenario.query.get(int(tipo_id)) if tipo_id else None

    db.session.commit()
    return redirect(url_for('.list_esc'))


@bp.post('/<int:id>/delete')
def delete(id):
    """
    Elimina un escenario.
    """
    e = Escenario.query.get_or_404(id)
    db.session.delete(e)
    db.session.commit()
    return redirect(url_for('.list_esc'))


@bp.get('/export/excel')
def export_excel():
    """
    Exporta todos los escenarios a Excel.
    Usa las propiedades .comuna, .barrio y .escenario como antes.
    """
    q = Escenario.query.all()
    df = pd.DataFrame([{
        'COMUNA': x.comuna,
        'BARRIO': x.barrio,
        'ESCENARIO': x.escenario,
        'DIRECCION': x.direccion,
        'Enlace Google Maps': x.url_maps
    } for x in q])

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Escenarios')
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='escenarios.xlsx')


@bp.route('/export_pdf')
def export_pdf():
    """
    Exporta todos los escenarios a PDF usando WeasyPrint.
    """
    data = Escenario.query.order_by(Escenario.id.asc()).all()
    html = render_template("reporte.html", data=data)

    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp:
        HTML(string=html).write_pdf(target=tmp.name)
        tmp.seek(0)
        return Response(
            tmp.read(),
            mimetype='application/pdf',
            headers={
                "Content-Disposition": "attachment; filename=escenarios.pdf"
            }
        )
