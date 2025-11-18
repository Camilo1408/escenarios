from flask import Blueprint, render_template, request, redirect, url_for, send_file, Response
from db.models import Escenario, db
import pandas as pd
import io
from datetime import datetime
from xhtml2pdf import pisa
import math
from weasyprint import HTML, CSS
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
    # --- parámetros de filtro / paginación ---
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    if per_page not in (10, 25, 50):
        per_page = 10

    comuna = request.args.get('comuna', default='', type=str)

    # --- comunas disponibles para el dropdown ---
    comunas_raw = [row[0] for row in db.session.query(Escenario.comuna).distinct().all()]
    comunas = sorted(comunas_raw, key=sort_comuna_value)

    # --- query base ---
    query = Escenario.query
    if comuna:
        query = query.filter(Escenario.comuna == comuna)

    # --- orden (1..10, luego textos) ---
    escenarios_all = query.all()
    escenarios_all_sorted = sorted(
        escenarios_all,
        key=lambda e: sort_comuna_value(e.comuna) + (e.id,)
    )

    # --- paginación manual ---
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
        comuna_seleccionada=comuna,
        page=page,
        pages=pages,
        per_page=per_page,
        total=total,
    )


@bp.get('/new')
def new_form():
    return render_template('escenarios_form.html', item=None)


@bp.post('/new')
def create():
    e = Escenario(
        comuna=request.form['comuna'],  # ahora comuna es texto
        barrio=request.form['barrio'],
        escenario=request.form['escenario'],
        direccion=request.form.get('direccion', ''),
        url_maps=request.form.get('url_maps', '')
    )
    db.session.add(e)
    db.session.commit()
    return redirect(url_for('.list_esc'))


@bp.get('/<int:id>/edit')
def edit_form(id):
    item = Escenario.query.get_or_404(id)
    return render_template('escenarios_form.html', item=item)


@bp.post('/<int:id>/edit')
def update(id):
    e = Escenario.query.get_or_404(id)
    e.comuna = request.form['comuna']
    e.barrio = request.form['barrio']
    e.escenario = request.form['escenario']
    e.direccion = request.form.get('direccion', '')
    e.url_maps = request.form.get('url_maps', '')
    db.session.commit()
    return redirect(url_for('.list_esc'))


@bp.post('/<int:id>/delete')
def delete(id):
    e = Escenario.query.get_or_404(id)
    db.session.delete(e)
    db.session.commit()
    return redirect(url_for('.list_esc'))


@bp.get('/export/excel')
def export_excel():
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

# Windows
# @bp.get('/export/pdf')
# def export_pdf():
#     data = Escenario.query.order_by(Escenario.comuna).all()
#     total = len(data)
#     fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

#     html = render_template('reporte.html', data=data, total=total, fecha=fecha)

#     pdf_buffer = io.BytesIO()
#     pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

#     if pisa_status.err:
#         return "Error al generar el PDF", 500

#     pdf_buffer.seek(0)
#     return send_file(
#         pdf_buffer,
#         as_attachment=True,
#         download_name="informe_escenarios.pdf",
#         mimetype="application/pdf"
#     )

#Linux
@bp.route('/export_pdf')
def export_pdf():
    # Obtener los datos reales para el reporte
    data = Escenario.query.order_by(Escenario.id.asc()).all()

    # Renderizar HTML del reporte
    html = render_template("reporte.html", data=data)

    # Crear PDF en archivo temporal (solo en memoria)
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
