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


def get_company_parser_config(
    company_name: str,
    config: Dict[str, Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Find and return configuration for a specific company.
    
    Args:
        company_name: Name of the company to find
        config: Loaded configuration dictionary
        
    Returns:
        Company configuration dictionary or None if not found
    """
    for company_id, company_config in config.items():
        if company_config.get("name") == company_name:
            return company_config
    return None
