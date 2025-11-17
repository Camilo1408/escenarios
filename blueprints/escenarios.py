from flask import Blueprint, render_template, request, redirect, url_for, send_file
from db.models import Escenario, db
import pandas as pd
import io

bp = Blueprint('escenarios', __name__)

@bp.get('/')
def list_esc():
    q = Escenario.query
    comuna = request.args.get('comuna')
    if comuna: q = q.filter_by(comuna=int(comuna))
    data = q.order_by(Escenario.id.desc()).all()
    return render_template('escenarios_list.html', data=data)

@bp.get('/new')
def new_form():
    return render_template('escenarios_form.html', item=None)

@bp.post('/new')
def create():
    e = Escenario(
        comuna=int(request.form['comuna']),
        barrio=request.form['barrio'],
        escenario=request.form['escenario'],
        direccion=request.form.get('direccion',''),
        url_maps=request.form.get('url_maps','')
    )
    db.session.add(e); db.session.commit()
    return redirect(url_for('.list_esc'))

@bp.get('/<int:id>/edit')
def edit_form(id):
    return render_template('escenarios_form', item=Escenario.query.get_or_404(id))

@bp.post('/<int:id>/edit')
def update(id):
    e = Escenario.query.get_or_404(id)
    e.comuna=int(request.form['comuna']),
    e.barrio=request.form['barrio'],
    e.escenario=request.form['escenario'],
    e.direccion=request.form.get('direccion',''),
    e.url_maps=request.form.get('url_maps','')
    db.session.commit()
    return redirect(url_for('.list_esc'))

@bp.post('/<int:id>/delete')
def delete(id):
    e = Escenario.query.get_or_404(id)
    db.session.delete(e); db.session.commit()
    return redirect(url_for('.list_esc'))

@bp.get('/export/excel')
def export_excel():
    q = Escenario.query.all()
    df = pd.DataFrame([{
        'COMUNA':x.comuna, 'BARRIO':x.barrio, 'ESCENARIO':x.escenario, 'DIRECCION':x.direccion, 'Enlace Google Maps':x.url_maps
    }for x in q])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Escenarios')
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name='escenarios.xlsx')