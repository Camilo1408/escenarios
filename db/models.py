from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Comuna(db.Model):
    __tablename__ = "comunas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    barrios = db.relationship(
        "Barrio",
        back_populates="comuna",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Comuna {self.nombre}>"


class Barrio(db.Model):
    __tablename__ = "barrios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    comuna_id = db.Column(db.Integer, db.ForeignKey("comunas.id"), nullable=False)

    comuna = db.relationship("Comuna", back_populates="barrios")
    escenarios = db.relationship(
        "Escenario",
        back_populates="barrio",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Barrio {self.nombre} ({self.comuna.nombre if self.comuna else ''})>"


class TipoEscenario(db.Model):
    __tablename__ = "tipos_escenario"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    escenarios = db.relationship("Escenario", back_populates="tipo", lazy='selectin')

    def __repr__(self):
        return f"<TipoEscenario {self.nombre}>"


class Escenario(db.Model):
    """
    Tabla principal de escenarios.

    NOTA: Para no romper plantillas ni código viejo, se exponen
    propiedades .comuna, .barrio y .escenario que delegan a las
    relaciones y al campo 'nombre'.
    """
    __tablename__ = "escenarios"

    id = db.Column(db.Integer, primary_key=True)

    # Nombre del escenario (antes columna 'escenario')
    nombre = db.Column(db.String(160), nullable=False)

    direccion = db.Column(db.String(200), nullable=False)
    url_maps = db.Column(db.Text, nullable=True)

    barrio_id = db.Column(db.Integer, db.ForeignKey("barrios.id"), nullable=False)
    tipo_escenario_id = db.Column(db.Integer, db.ForeignKey("tipos_escenario.id"), nullable=True)

    barrio = db.relationship("Barrio", back_populates="escenarios")
    tipo = db.relationship("TipoEscenario", back_populates="escenarios")

    # --- Helpers de compatibilidad ---

    @property
    def escenario(self):
        """Compatibilidad con código/plantillas que usan item.escenario."""
        return self.nombre

    @escenario.setter
    def escenario(self, value):
        self.nombre = value

    @property
    def comuna(self):
        """Nombre de la comuna derivado del barrio."""
        if self.barrio and self.barrio.comuna:
            return self.barrio.comuna.nombre
        return None

    @property
    def barrio_nombre(self):
        """Nombre del barrio."""
        return self.barrio.nombre if self.barrio else None

    @property
    def barrio_str(self):
        """Alias opcional por si se quiere usar en plantillas."""
        return self.barrio_nombre

    @property
    def tipo_nombre(self):
        return self.tipo.nombre if self.tipo else None
