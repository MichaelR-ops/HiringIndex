"""Configuration loading and management."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def load_company_config(config_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load company configuration from JSON file.
    
    Args:
        config_path: Path to the company configuration JSON file
        
    Returns:
        Dictionary mapping company IDs to their configurations
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)
