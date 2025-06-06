"""
Módulo de base de datos para la aplicación de pacientes.
Implementa el esquema OMOP-CDM para el almacenamiento de datos médicos.
"""
from .database import Base, engine, db_session, get_db

__all__ = ["Base", "engine", "db_session", "get_db"]
