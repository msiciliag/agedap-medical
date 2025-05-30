import json
from pathlib import Path
from typing import Optional

class KeyManager:
    """
    KeyManager se encarga de gestionar las claves de un solo uso para un servicio específico.
    Proporciona métodos para cargar claves válidas desde un archivo JSON y obtener una clave disponible.
    """

    def __init__(self, service_name: str):
        """
        Inicializa el KeyManager con el nombre del servicio.
        
        Args:
            service_name (str): Nombre del servicio para el cual se gestionarán las claves.
        """
        self.service_name = service_name
        self.valid_keys_file = f"keys/{self.service_name}/valid.json"
        self.valid_keys = self._load_valid_keys()

    def _load_valid_keys(self) -> list[str]:
        """
        Carga las claves válidas desde el archivo JSON.
        
        Returns:
            list[str]: Lista de claves válidas.
        """
        keys_path = Path(self.valid_keys_file)
        if not keys_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de claves válidas: {self.valid_keys_file}")
        
        try:
            with keys_path.open('r') as f:
                keys = json.load(f)
                if not isinstance(keys, list):
                    raise ValueError("El archivo de claves válidas no contiene una lista.")
                return keys
        except (IOError, json.JSONDecodeError) as e:
            raise ValueError(f"Error al cargar las claves válidas: {e}")

    def get_single_use_key(self) -> Optional[str]:
        """
        Proporciona una clave válida disponible.
        
        Returns:
            Optional[str]: Una clave válida o None si no hay claves disponibles.
        """
        self.valid_keys = self._load_valid_keys()
        if not self.valid_keys:
            return None
        return self.valid_keys.pop(0)