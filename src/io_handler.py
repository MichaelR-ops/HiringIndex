"""File input/output operations."""

from pathlib import Path
from typing import Union
import pandas as pd


def load_companies(filepath: str) -> pd.DataFrame:
    """
    Load company data from Excel or CSV file.
    
    Args:
        filepath: Path to the input file (.xlsx, .xls, or .csv)
        
    Returns:
        DataFrame with company information
        
    Raises:
        ValueError: If file format is not supported
        FileNotFoundError: If file doesn't exist
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {filepath}")
    
    ext = path.suffix.lower()
    
    if ext == ".csv":
        return pd.read_csv(filepath)
    elif ext in (".xlsx", ".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def save_hiring_index(
    df: pd.DataFrame,
    filepath: str,
    format: str = "csv"
) -> None:
    """
    Save hiring index results to file.
    
    Args:
        df: DataFrame with results
        filepath: Output file path
        format: Output format ("csv" or "xlsx")
        
    Raises:
        ValueError: If format is not supported
    """
    if format.lower() == "csv":
        df.to_csv(filepath, index=False)
    elif format.lower() in ("xlsx", "xls"):
        df.to_excel(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")
