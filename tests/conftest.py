"""
Configuración de pruebas para el proyecto agedap-medical.
Este archivo ayuda a manejar los imports y configurar el entorno de pruebas.
"""
import sys
import os
from pathlib import Path

def setup_test_environment():
    """Configura el entorno de pruebas añadiendo las rutas necesarias."""
    project_root = Path(__file__).parent.parent
    
    # Añadir rutas al PYTHONPATH
    paths_to_add = [
        str(project_root),
        str(project_root / "patient_app" / "src"),
        str(project_root / "provider"),
        str(project_root / "standard_definitions"),
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

# Configurar automáticamente cuando se importe este módulo
setup_test_environment()
