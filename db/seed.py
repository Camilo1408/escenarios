import pandas as pd
from app import create_app
from db.models import db, Escenario

CSV_PATH = '/ESCENARIO_DE_RECREACION_DEPORTIVA_NEIVA_2022_20251110.csv'

app = create_app()
with app.app_context():
    df = pd.read_csv(CSV_PATH)
    df = df.rename(columns={
        'COMUNA':'comuna', 'BARRIO':'barrio', 'ESCENARIO':'escenario', 'DIRECCION':'direccion','Enlace Google Maps':'url_maps'
    })
    for _, r in df.iterrows():
        db.session.add(Escenario(
            comuna=int(r['comuna']),
            barrio=str(r['barrio']),
            escenario=str(r['escenario']),
            direccion=str(r.get('direcion') or ''),
            url_maps=str(r.get('url_maps') or '')
        ))
    db.session.commit()