"""
Configuración de la base de datos OMOP-CDM usando omopmodel.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from omopmodel import OMOP_5_4_declarative as omop54

# Configuración de la base de datos
DATABASE_PATH = os.environ.get(
    "DATABASE_URL", 
    "sqlite:////root/agedap-medical/patient_app/src/db/omop_cdm.db"
)

# Crear el motor de base de datos
engine = create_engine(
    DATABASE_PATH, 
    echo=False  # Establecer en True para habilitar el logging de SQL
)

# Crear la sesión para interactuar con la base de datos
SessionMaker = sessionmaker(bind=engine)

# Crear el esquema si no existe
def create_omop_tables():
    """
    Inicializa la base de datos OMOP-CDM creando todas las tablas definidas en el modelo.
    """
    omop54.Base.metadata.create_all(engine)
    print("Base de datos OMOP-CDM inicializada correctamente")

def get_session():
    """
    Obtiene una sesión de la base de datos.
    """
    return SessionMaker()
