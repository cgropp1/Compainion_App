import json
import os
import logging
from typing import Dict, Any, Optional

# Get logger for this module
logger = logging.getLogger('pss_companion.config')

# Default values in case the file is missing or corrupt
_DEFAULT_CONFIG = {
    "essensal_rooms": [
        "Shield",
        "Engine",
        "Stealth",
        "Teleport",
        "Android"
    ],
    "armor_value_per_lvl": {
        "1": 2, "2": 4, "3": 5, "4": 6, "5": 7,
        "6": 8, "7": 9, "8": 10, "9": 12, "10": 14,
        "11": 16, "12": 18, "13": 18
    }
}

# Global variables to store loaded configuration
_config_data = {}
_config_loaded = False

def get_config(reload: bool = False) -> Dict[str, Any]:
    """Get the configuration data, loading it if necessary."""
    global _config_data, _config_loaded
    
    if not _config_loaded or reload:
        _config_data = _load_config()
        _config_loaded = True
    
    return _config_data

def _load_config() -> Dict[str, Any]:
    """Load configuration from the custom_data.json file."""
    config_paths = [
        'data/custom_data.json',
        'custom_data.json',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/custom_data.json')
    ]
    
    for path in config_paths:
        try:
            logger.debug(f"Attempting to load config from: {path}")
            with open(path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded configuration from {path}")
                return data
        except FileNotFoundError:
            logger.debug(f"Config file not found at: {path}")
            continue
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {path}")
            continue
        except Exception as e:
            logger.error(f"Error loading config from {path}: {e}")
            continue
    
    # If we get here, we couldn't load the config file
    logger.warning("Failed to load config file, using default configuration")
    return _DEFAULT_CONFIG

def get_essential_rooms() -> list:
    """Get the list of essential rooms."""
    return get_config().get("essensal_rooms", _DEFAULT_CONFIG["essensal_rooms"])

def get_armor_value(level: int) -> int:
    """Get the armor value for a given ship level."""
    armor_values = get_config().get("armor_value_per_lvl", _DEFAULT_CONFIG["armor_value_per_lvl"])
    # Convert level to string for dictionary lookup
    level_str = str(level)
    # Return the armor value for the level, or 0 if not found
    return int(armor_values.get(level_str, 0))

def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting from the config."""
    return get_config().get(key, default)

def reload_config() -> bool:
    """Force reload of configuration data."""
    try:
        global _config_loaded
        _config_loaded = False
        get_config(reload=True)
        logger.info("Configuration reloaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        return False