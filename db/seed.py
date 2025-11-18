import pandas as pd
import sys, os

# Añadimos la raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from db.models import db, Escenario


def limpiar_campo(valor):
    """Limpia valores tipo nan, None, NULL, espacios, etc."""
    if valor is None:
        return ""
    v = str(valor).strip()
    if v.lower() in ("", "nan", "none", "null"):
        return ""
    return v


def run_seed():
    app = create_app()

    with app.app_context():
        print("Cargando datos...")

        CSV_PATH = os.path.join("db", "ESCENARIO_DE_RECREACION_DEPORTIVA_NEIVA_2022_20251110.csv")
        df = pd.read_csv(CSV_PATH)

        # Normalizar nombres de columnas
        df = df.rename(columns={
            "COMUNA": "comuna",
            "BARRIO": "barrio",
            "ESCENARIO": "escenario",
            "DIRECCION": "direccion",
            "Enlace Google Maps": "url_maps"
        })

        registros = []

        for _, r in df.iterrows():
            comuna = limpiar_campo(r.get("comuna", ""))
            barrio = limpiar_campo(r.get("barrio", ""))
            escenario = limpiar_campo(r.get("escenario", ""))
            direccion = limpiar_campo(r.get("direccion", ""))
            url_maps = limpiar_campo(r.get("url_maps", ""))

            registros.append(Escenario(
                comuna=comuna,
                barrio=barrio,
                escenario=escenario,
                direccion=direccion,
                url_maps=url_maps
            ))

        db.session.add_all(registros)
        db.session.commit()

        print(f"Datos cargados correctamente. Total insertados: {len(registros)}")


if __name__ == "__main__":
    run_seed()
