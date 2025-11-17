from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Escenario(db.Model):
    __tablename__ = 'escenarios'
    id = db.Column(db.Integer, primary_key=True)
    comuna = db.Column(db.Integer, nullable=False)
    barrio = db.Column(db.String(120), nullable=False)
    escenario = db.Column(db.String(160), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    url_maps = db.Column(db.Text, nullable=True)
    
