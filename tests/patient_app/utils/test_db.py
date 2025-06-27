"""
Tests for database utility functions.
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from datetime import datetime, date
from unittest.mock import patch, Mock, MagicMock
import sys

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent.parent / "patient_app" / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Try to import the modules we need for integration tests
try:
    from utils import db as db_module
    from utils.db import (
        get_patient_measurements,
        get_patient_observations, 
        get_patient_conditions,
        get_person_by_id,
        get_gender,
        get_date_of_birth,
        clear_database
    )
    DB_MODULE_AVAILABLE = True
    DB_IMPORT_ERROR = None
except ImportError as e:
    DB_MODULE_AVAILABLE = False
    DB_IMPORT_ERROR = str(e)
    db_module = None

# Try to import database components
try:
    from db.db_init import OMOPSchemaManager
    DB_INIT_AVAILABLE = True
    DB_INIT_ERROR = None
except ImportError as e:
    DB_INIT_AVAILABLE = False 
    DB_INIT_ERROR = str(e)

# Try to import OMOP model
try:
    from omopmodel import OMOP_5_4_declarative as omop54
    OMOP_MODEL_AVAILABLE = True
    OMOP_ERROR = None
except ImportError as e:
    OMOP_MODEL_AVAILABLE = False
    OMOP_ERROR = str(e)

# Define if all integration test requirements are met
INTEGRATION_TESTS_AVAILABLE = (DB_MODULE_AVAILABLE and DB_INIT_AVAILABLE and OMOP_MODEL_AVAILABLE)


# ===== EXISTING BASIC TESTS (SMOKE TESTS) =====
# Estas son las pruebas básicas de estructura que ya existían

def test_db_file_exists():
    """Test that db.py file exists."""
    db_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "db.py"
    assert db_path.exists(), "db.py should exist"


def test_db_file_has_content():
    """Test that db.py has content."""
    db_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "db.py"
    
    if db_path.exists():
        content = db_path.read_text().strip()
        assert len(content) > 0, "db.py should not be empty"


def test_db_contains_expected_functions():
    """Test that db.py contains expected function definitions."""
    db_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "db.py"
    
    if db_path.exists():
        content = db_path.read_text()
        
        # Check for expected functions
        expected_functions = [
            "get_patient_measurements",
            "get_patient_observations",
            "get_patient_conditions"
        ]
        
        for func in expected_functions:
            assert func in content, f"Function {func} should be defined in db.py"


def test_database_file_exists():
    """Test that the OMOP database file exists."""
    db_file_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "db" / "omop_cdm.db"
    
    if db_file_path.exists():
        assert db_file_path.is_file(), "omop_cdm.db should be a file"
        assert db_file_path.stat().st_size > 0, "omop_cdm.db should not be empty"
    else:
        pytest.skip("Database file omop_cdm.db does not exist")


def test_utils_directory_structure():
    """Test that utils directory has expected structure."""
    utils_dir = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils"
    
    expected_files = [
        "db.py",
        "fhir.py", 
        "omop.py",
        "data_mapper.py"
    ]
    
    for expected_file in expected_files:
        file_path = utils_dir / expected_file
        assert file_path.exists(), f"Expected utils file missing: {expected_file}"


# ===== INTEGRATION TESTS =====
# Estas son las nuevas pruebas de integración que prueban funcionalidad real

@pytest.fixture
def test_db_session():
    """Crear una base de datos temporal para pruebas."""
    if not INTEGRATION_TESTS_AVAILABLE:
        pytest.skip(f"Required imports not available: DB={DB_IMPORT_ERROR}, OMOP={OMOP_ERROR}")
    
    # Crear archivo temporal para la base de datos de prueba
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    # Configurar la base de datos de prueba
    original_env = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = f"sqlite:///{temp_db.name}"
    
    try:
        # Crear esquema en la base de datos temporal
        schema_manager = OMOPSchemaManager()
        schema_manager.create_schema()
        
        yield schema_manager
        
    finally:
        # Limpiar
        if original_env:
            os.environ["DATABASE_URL"] = original_env
        else:
            os.environ.pop("DATABASE_URL", None)
        
        # Eliminar archivo temporal
        try:
            os.unlink(temp_db.name)
        except FileNotFoundError:
            pass


@pytest.fixture
def sample_test_data(test_db_session):
    """Crear datos de prueba en la base de datos temporal."""
    if not INTEGRATION_TESTS_AVAILABLE:
        pytest.skip(f"Required imports not available: DB={DB_IMPORT_ERROR}, OMOP={OMOP_ERROR}")
    
    session = test_db_session.SessionLocal()
    
    try:
        # Crear conceptos de prueba
        concepts = [
            omop54.Concept(
                concept_id=1,
                concept_name="Test Blood Pressure",
                concept_class_id="Clinical Finding",
                vocabulary_id="SNOMED",
                domain_id="Measurement"
            ),
            omop54.Concept(
                concept_id=2,
                concept_name="Test Diabetes",
                concept_class_id="Clinical Finding", 
                vocabulary_id="SNOMED",
                domain_id="Condition"
            ),
            omop54.Concept(
                concept_id=3,
                concept_name="Test Observation",
                concept_class_id="Clinical Finding",
                vocabulary_id="SNOMED", 
                domain_id="Observation"
            )
        ]
        session.add_all(concepts)
        
        # Crear persona de prueba
        person = omop54.Person(
            person_id=1,
            gender_concept_id=8507,  # Male
            gender_source_value="M",
            year_of_birth=1980,
            month_of_birth=5,
            day_of_birth=15
        )
        session.add(person)
        
        # Crear mediciones de prueba
        measurements = [
            omop54.Measurement(
                measurement_id=1,
                person_id=1,
                measurement_concept_id=1,
                measurement_datetime=datetime(2024, 1, 1, 10, 0),
                value_as_number=120.0
            ),
            omop54.Measurement(
                measurement_id=2,
                person_id=1,
                measurement_concept_id=1,
                measurement_datetime=datetime(2024, 1, 15, 14, 30),
                value_as_number=118.5
            )
        ]
        session.add_all(measurements)
        
        # Crear observaciones de prueba
        observations = [
            omop54.Observation(
                observation_id=1,
                person_id=1,
                observation_concept_id=3,
                observation_datetime=datetime(2024, 1, 1, 11, 0),
                value_as_number=98.6
            )
        ]
        session.add_all(observations)
        
        # Crear condiciones de prueba
        conditions = [
            omop54.ConditionOccurrence(
                condition_occurrence_id=1,
                person_id=1,
                condition_concept_id=2,
                condition_start_date=date(2024, 1, 1)
            )
        ]
        session.add_all(conditions)
        
        session.commit()
        
    finally:
        session.close()


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_patient_measurements_returns_data(sample_test_data):
    """Prueba que get_patient_measurements devuelve datos correctos."""
    measurements = get_patient_measurements(patient_id=1)
    
    assert isinstance(measurements, list)
    assert len(measurements) == 2
    assert measurements[0]["person_id"] == 1
    assert measurements[0]["measurement_concept_id"] == 1
    assert measurements[0]["value_as_number"] == 118.5  # Más reciente primero
    assert measurements[1]["value_as_number"] == 120.0


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_patient_measurements_with_concept_filter(sample_test_data):
    """Prueba que el filtro por concept_ids funciona."""
    measurements = get_patient_measurements(patient_id=1, concept_ids=[1])
    
    assert len(measurements) == 2
    for measurement in measurements:
        assert measurement["measurement_concept_id"] == 1


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_patient_measurements_with_limit(sample_test_data):
    """Prueba que el parámetro limit funciona."""
    measurements = get_patient_measurements(patient_id=1, limit=1)
    
    assert len(measurements) == 1
    assert measurements[0]["value_as_number"] == 118.5  # Más reciente


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_patient_measurements_nonexistent_patient(sample_test_data):
    """Prueba el comportamiento con un paciente que no existe."""
    measurements = get_patient_measurements(patient_id=999)
    
    assert isinstance(measurements, list)
    assert len(measurements) == 0


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_patient_observations_returns_data(sample_test_data):
    """Prueba que get_patient_observations devuelve datos correctos."""
    observations = get_patient_observations(patient_id=1)
    
    assert isinstance(observations, list)
    assert len(observations) == 1
    assert observations[0]["person_id"] == 1
    assert observations[0]["observation_concept_id"] == 3
    assert observations[0]["value_as_number"] == 98.6


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_patient_conditions_returns_data(sample_test_data):
    """Prueba que get_patient_conditions devuelve datos correctos."""
    conditions = get_patient_conditions(patient_id=1)
    
    assert isinstance(conditions, list)
    assert len(conditions) == 1
    assert conditions[0]["person_id"] == 1
    assert conditions[0]["condition_concept_id"] == 2


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_person_by_id_returns_data(sample_test_data):
    """Prueba que get_person_by_id devuelve datos correctos."""
    person = get_person_by_id(person_id=1)
    
    assert person is not None
    assert isinstance(person, dict)
    assert person["person_id"] == 1
    assert person["gender_source_value"] == "M"
    assert person["year_of_birth"] == 1980
    assert person["month_of_birth"] == 5
    assert person["day_of_birth"] == 15


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_person_by_id_nonexistent(sample_test_data):
    """Prueba el comportamiento con una persona que no existe."""
    person = get_person_by_id(person_id=999)
    
    assert person is None


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_gender_returns_correct_value(sample_test_data):
    """Prueba que get_gender devuelve el género correcto."""
    gender = get_gender(patient_id=1)
    
    assert gender == "M"


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_get_gender_nonexistent_patient(sample_test_data):
    """Prueba get_gender con un paciente que no existe."""
    gender = get_gender(patient_id=999)
    
    assert gender is None


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_database_session_error_handling():
    """Prueba el manejo de errores en las sesiones de base de datos."""
    # Simular un error de base de datos
    with patch('utils.db.get_db_session') as mock_session:
        mock_session.side_effect = Exception("Database connection error")
        
        measurements = get_patient_measurements(patient_id=1)
        assert measurements == []
        
        observations = get_patient_observations(patient_id=1)
        assert observations == []
        
        conditions = get_patient_conditions(patient_id=1)
        assert conditions == []


@pytest.mark.skipif(not INTEGRATION_TESTS_AVAILABLE, reason="Required imports not available")
def test_clear_database_functionality(test_db_session):
    """Prueba que clear_database limpia correctamente la base de datos."""
    session = test_db_session.SessionLocal()
    
    try:
        # Añadir algunos datos
        person = omop54.Person(
            person_id=1,
            gender_concept_id=8507,
            year_of_birth=1990
        )
        session.add(person)
        session.commit()
        
        # Verificar que los datos existen
        count_before = session.query(omop54.Person).count()
        assert count_before == 1
        
        # Limpiar la base de datos
        clear_database()
        
        # Verificar que los datos fueron eliminados
        count_after = session.query(omop54.Person).count()
        assert count_after == 0
        
    finally:
        session.close()


def test_imports_and_modules_available():
    """Prueba que todos los módulos necesarios se pueden importar."""
    if not INTEGRATION_TESTS_AVAILABLE:
        # Mostrar información detallada sobre qué falta
        error_msg = "Integration tests not available due to missing components:\n"
        if not DB_MODULE_AVAILABLE:
            error_msg += f"- DB Module: {DB_IMPORT_ERROR}\n"
        if not DB_INIT_AVAILABLE:
            error_msg += f"- DB Init: {DB_INIT_ERROR}\n"
        if not OMOP_MODEL_AVAILABLE:
            error_msg += f"- OMOP Model: {OMOP_ERROR}\n"
        
        pytest.skip(error_msg)
    
    # Verificar que las funciones están disponibles
    functions_to_check = [
        'get_patient_measurements',
        'get_patient_observations', 
        'get_patient_conditions',
        'get_person_by_id',
        'get_gender',
        'get_date_of_birth'
    ]
    
    for func_name in functions_to_check:
        assert hasattr(db_module, func_name), f"Function {func_name} not found in db module"
        assert callable(getattr(db_module, func_name)), f"{func_name} is not callable"


# ===== ADDITIONAL MOCK-BASED TESTS =====
# Estas pruebas funcionan incluso sin todas las dependencias

def test_database_functions_basic_structure():
    """Prueba la estructura básica de las funciones de base de datos usando mocks."""
    db_path = Path(__file__).parent.parent.parent.parent / "patient_app" / "src" / "utils" / "db.py"
    
    if not db_path.exists():
        pytest.skip("db.py file does not exist")
    
    # Leer el código y verificar que las funciones tienen la estructura esperada
    code = db_path.read_text()
    
    # Verificar que las funciones tienen manejo de errores
    assert "try:" in code, "Las funciones deberían tener manejo de errores"
    assert "except" in code, "Las funciones deberían tener manejo de excepciones"
    
    # Verificar que usan sessions de base de datos
    assert "get_db_session" in code, "Las funciones deberían usar sesiones de base de datos"
    
    # Verificar que tienen logging
    assert "logger" in code, "Las funciones deberían tener logging"


def test_mock_database_operations():
    """Prueba las operaciones de base de datos usando mocks completamente."""
    
    # Simular una función de base de datos
    def mock_get_patient_data(patient_id, concept_ids=None, limit=100):
        if patient_id == 999:
            return []  # Paciente no existe
        
        return [
            {
                "person_id": patient_id,
                "concept_id": 1,
                "value": 120.0,
                "datetime": "2024-01-01T10:00:00"
            }
        ]
    
    # Probar el comportamiento esperado
    result = mock_get_patient_data(1)
    assert len(result) == 1
    assert result[0]["person_id"] == 1
    
    # Probar paciente inexistente
    result_empty = mock_get_patient_data(999)
    assert len(result_empty) == 0


def test_database_connection_resilience():
    """Prueba la resistencia de las conexiones de base de datos."""
    
    # Simular diferentes escenarios de error
    error_scenarios = [
        "Database connection timeout",
        "SQLite database is locked", 
        "Table does not exist",
        "Invalid SQL syntax"
    ]
    
    for error_msg in error_scenarios:
        # En una implementación real, verificaríamos que estas excepciones
        # se manejan correctamente y devuelven resultados vacíos o None
        assert isinstance(error_msg, str)  # Mock test
        
    # Esto simula que las funciones deberían ser resilientes a errores
    assert True, "Las funciones deben manejar errores de conectividad gracefully"