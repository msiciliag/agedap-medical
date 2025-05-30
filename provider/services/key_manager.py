from pathlib import Path
import json
import configparser
from typing import List, Optional
from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44, Bip44Coins,
    Bip44Changes
)

class KeyManager:
    """
    KeyManager is responsible for managing one-time keys used for authentication.
    It handles the generation, storage, and validation of these keys.
    It uses BIP44 standards for key generation and manages keys in a JSON format.
    The keys are stored in a specified directory, and the configuration is loaded from a file.
    The KeyManager ensures that the necessary directories exist and provides methods to generate,
    validate, and mark keys as used.
    Attributes:
        config (configparser.ConfigParser): Configuration parser for key authentication.
        master_xpub (Optional[str]): The master xPub for the server.
        valid_keys (List[str]): List of valid one-time keys.
        used_keys (List[str]): List of used one-time keys.
    """
    def __init__(self, service_name: str):
        """
        Initialize the KeyManager with the given service name.
        Args:
            service_name (str): The name of the service for which keys will be managed.
        """
        self.service_name = service_name
        self.config = self._load_key_auth_config()
        self._load_config_parameters()
        self._ensure_keys_directory_exists()
        self.master_xpub: Optional[str] = None
        self.valid_keys: List[str] = []
        self.used_keys: List[str] = []
        self._initialize_service_state()

    def _load_key_auth_config(self) -> configparser.ConfigParser:
        """Create the configuration parser for key authentication."""
        config = configparser.ConfigParser()
        project_root = Path(__file__).resolve().parent.parent.parent
        config_path = project_root / "key_auth_config.ini"
        if not config_path.exists():
            raise FileNotFoundError(f"File not found or invalid: {config_path}")
        config.read(config_path)
        return config
    
    def _load_config_parameters(self):
        """Load configuration parameters from the config file."""
        base_keys_dir = f"keys/{self.service_name}"
        self.server_xpub_file = f"{base_keys_dir}/server_xpub.txt"
        self.valid_keys_file = f"{base_keys_dir}/valid.json"
        self.used_keys_file = f"{base_keys_dir}/used.json"
        self.initial_key_batch_size = self.config.getint("server", "initial_key_batch_size", fallback=50)
        self.crypto_validation_window_size = self.config.getint("server", "crypto_validation_window_size", fallback=200)
        self.default_account_index = self.config.getint("server", "default_account_index", fallback=0)
        self.max_index_to_check_crypto = self.config.getint("server", "max_index_to_check_crypto", fallback=1000)

    def _ensure_keys_directory_exists(self):
        """Ensure the directory for keys exists.
        If the directory does not exist, it will be created."""
        keys_dir = Path(self.server_xpub_file).parent
        if keys_dir and not keys_dir.exists():
            keys_dir.mkdir(parents=True, exist_ok=True)

    def _generate_and_save_master_xpub(self) -> str:
        """Generate and save the server master xPub (at BIP44 account level, m/44'/1'/account').
        The generated xPub corresponds to the account node (m/44'/1'/account').
        Returns:
            str: The generated master xPub.
        """
        mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
        seed_bytes = Bip39SeedGenerator(mnemonic.ToStr()).Generate()
        bip44_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN_TESTNET)
        bip44_acc_node = bip44_mst.Purpose().Coin().Account(self.default_account_index)
        master_xpub = bip44_acc_node.PublicKey().ToExtended()
        server_xpub_path = Path(self.server_xpub_file)
        server_xpub_path.write_text(master_xpub)
        return master_xpub

    def _load_master_xpub(self) -> Optional[str]:
        """Load the server master xPub from file.
        If the file does not exist, it generates a new one.
        Returns:
            str: The master xPub if it exists, otherwise None.
        """
        server_xpub_path = Path(self.server_xpub_file)
        if server_xpub_path.exists():
            return server_xpub_path.read_text().strip()
        return None

    def _load_keys_from_file(self, file_path: str) -> List[str]:
        """Load keys from a JSON file.
        Args:
            file_path (str): Path to the JSON file containing keys.
        Returns:
            List[str]: A list of keys loaded from the file, or an empty list if the file does not exist or is invalid.
        """
        keys_path = Path(file_path)
        if not keys_path.exists():
            return []
        try:
            with keys_path.open('r') as f:
                keys = json.load(f)
                return keys if isinstance(keys, list) else []
        except (IOError, json.JSONDecodeError):
            return []

    def _save_keys_to_file(self, keys_list: List[str], file_path: str) -> bool:
        keys_path = Path(file_path)
        try:
            with keys_path.open('w') as f:
                json.dump(keys_list, f, indent=4)
            return True
        except IOError:
            return False

    def _initialize_service_state(self):
        """Initialize the service state by loading or generating the master xPub and keys."""
        self.master_xpub = self._load_master_xpub()
        if not self.master_xpub:
            self.master_xpub = self._generate_and_save_master_xpub()

        self.valid_keys = self._load_keys_from_file(self.valid_keys_file)
        self.used_keys = self._load_keys_from_file(self.used_keys_file)

        if not self.valid_keys and self.master_xpub:
            start_idx = len(self.used_keys) if self.used_keys else 0
            new_keys = self._generate_one_time_keys(
                start_index=start_idx,
                count=self.initial_key_batch_size,
                change_level_bip44=Bip44Changes.CHAIN_EXT
            )
            if new_keys:
                self.valid_keys.extend(new_keys)
                self._save_keys_to_file(self.valid_keys, self.valid_keys_file)
                self._save_keys_to_file(self.used_keys, self.used_keys_file)

    def _generate_one_time_keys(self, start_index: int, count: int, change_level_bip44: Bip44Changes) -> List[str]:
        """
        Generate a batch of one-time keys.
        Args:
            start_index (int): The starting index for key generation.
            count (int): The number of keys to generate.
            change_level_bip44 (Bip44Changes): The BIP44 change level (external or internal).
        Returns:
            List[str]: A list of generated keys.
        """
        if not self.master_xpub: return []
        keys = []
        try:
            xpub_account_obj = Bip44.FromExtendedKey(self.master_xpub, Bip44Coins.BITCOIN_TESTNET)
            change_node = xpub_account_obj.Change(change_level_bip44)
            for i in range(count):
                address_node = change_node.AddressIndex(start_index + i)
                address = address_node.PublicKey().ToAddress()
                keys.append(address)
        except Exception:
            return Exception("Failed to generate keys from master xPub.")
        return keys

    def _derive_and_check_key(self, change_level: Bip44Changes, key_index: int, key_to_validate: str) -> bool:
        """Derives a key from the master xPub and checks if it matches the provided key.
        Args:
            change_level (Bip44Changes): The BIP44 change level (external or internal).
            key_index (int): The index of the key to derive.
            key_to_validate (str): The key to validate against the derived key.
        Returns:
            bool: True if the derived key matches the provided key, False otherwise.
        """
        if not self.master_xpub: return False
        try:
            xpub_account_obj = Bip44.FromExtendedKey(self.master_xpub, Bip44Coins.BITCOIN_TESTNET)
            change_node = xpub_account_obj.Change(change_level)
            address_node = change_node.AddressIndex(key_index)
            derived_address = address_node.PublicKey().ToAddress()
            return derived_address == key_to_validate
        except Exception: return False

    def validate_key(self, key_to_validate: str) -> bool:
        """Validates a key against the valid keys list.
        Args:
            key_to_validate (str): The key to validate.
        Returns:
            bool: True if the key is valid, False otherwise.
        """
        if key_to_validate in self.used_keys:
            return False
        elif key_to_validate in self.valid_keys:
            return True
        elif self.master_xpub:
            return self.validate_key_cryptographically(key_to_validate)

    def validate_key_cryptographically(self, key_to_validate: str) -> bool:
        if not self.master_xpub: return False
        for i in range(min(self.crypto_validation_window_size, self.max_index_to_check_crypto)):
            if self._derive_and_check_key(Bip44Changes.CHAIN_EXT, i, key_to_validate): return True
        for i in range(min(self.crypto_validation_window_size, self.max_index_to_check_crypto)):
            if self._derive_and_check_key(Bip44Changes.CHAIN_INT, i, key_to_validate): return True
        return False

    def mark_key_as_used(self, key: str) -> bool:
        key_was_in_valid = False
        if key in self.valid_keys:
            try: self.valid_keys.remove(key); key_was_in_valid = True
            except ValueError: 
                return False
        if key not in self.used_keys: self.used_keys.append(key)
        
        saved_used = self._save_keys_to_file(self.used_keys, self.used_keys_file)
        saved_valid = True
        if key_was_in_valid: saved_valid = self._save_keys_to_file(self.valid_keys, self.valid_keys_file)
        return saved_used and saved_valid