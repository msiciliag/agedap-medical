"""
Configuración de la base de datos para el esquema OMOP-CDM.
"""
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configuración de la base de datos
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:////Users/miguel/Documents/dev/in2ai/agedap_medical/agedap-medical/patient_app/storage/data/omop_cdm.db"
)

# Convención de nomenclatura para restricciones (índices, claves primarias, etc.)
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Crear el motor de base de datos
engine = create_engine(
    DATABASE_URL, 
    echo=False,  # Establecer en True para habilitar el logging de SQL
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Crear una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Definir la metadata con la convención de nombres
metadata = MetaData(naming_convention=NAMING_CONVENTION)

# Crear la clase base para los modelos de SQLAlchemy
Base = declarative_base(metadata=metadata)

# Función para obtener una sesión de base de datos
def get_db():
    """
    Función generadora para obtener una sesión de base de datos y asegurar que se cierre
    después de su uso.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
