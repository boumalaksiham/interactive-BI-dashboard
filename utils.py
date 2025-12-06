"""
Utility functions for the Business Intelligence Dashboard.
Handles data validation, formatting, and common helper operations.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, List
import io


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that the DataFrame is suitable for analysis.
    
    Args:
        df: pandas DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None:
        return False, "No data loaded"
    
    if df.empty:
        return False, "DataFrame is empty"
    
    if len(df.columns) == 0:
        return False, "DataFrame has no columns"
    
    if len(df) < 2:
        return False, "DataFrame has too few rows for analysis"
    
    return True, "Valid"


def get_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Categorize columns by their data types.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Dictionary with keys 'numerical', 'categorical', 'datetime'
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    return {
        'numerical': numerical_cols,
        'categorical': categorical_cols,
        'datetime': datetime_cols
    }


def format_number(value: float) -> str:
    """
    Format numbers for display with appropriate precision.
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string
    """
    if pd.isna(value):
        return "N/A"
    
    if abs(value) >= 1e6:
        return f"{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f}K"
    elif abs(value) < 0.01 and value != 0:
        return f"{value:.4f}"
    else:
        return f"{value:.2f}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.
    
    Args:
        numerator: Top value
        denominator: Bottom value
        default: Value to return if denominator is zero
        
    Returns:
        Result of division or default
    """
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    except:
        return default


def detect_date_columns(df: pd.DataFrame) -> List[str]:
    """
    Detect columns that might contain dates but aren't datetime type yet.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        List of column names that might be dates
    """
    potential_date_cols = []
    
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].isna().all():
            continue
            
        # Sample non-null values
        sample = df[col].dropna().head(10)
        
        # Try to parse as dates
        try:
            pd.to_datetime(sample, errors='raise')
            potential_date_cols.append(col)
        except:
            continue
    
    return potential_date_cols


def create_summary_text(df: pd.DataFrame) -> str:
    """
    Create a formatted text summary of the DataFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        Formatted summary string
    """
    col_types = get_column_types(df)
    
    # Format column lists
    numerical_cols = ", ".join(col_types['numerical']) if col_types['numerical'] else "None"
    categorical_cols = ", ".join(col_types['categorical']) if col_types['categorical'] else "None"
    datetime_cols = ", ".join(col_types['datetime']) if col_types['datetime'] else "None"
    
    summary = f"""
**Dataset Overview**

**Shape:** {df.shape[0]:,} rows × {df.shape[1]} columns

**Column Types:**
- Numerical: {len(col_types['numerical'])} columns ({numerical_cols})
- Categorical: {len(col_types['categorical'])} columns ({categorical_cols})
- Datetime: {len(col_types['datetime'])} columns ({datetime_cols})

**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB

**Missing Values:** {df.isna().sum().sum():,} cells ({(df.isna().sum().sum() / df.size * 100):.2f}%)
"""
    
    return summary


def get_missing_value_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a summary DataFrame of missing values with column types.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        DataFrame with missing value statistics and column types
    """
    missing_counts = df.isna().sum()
    missing_percent = (missing_counts / len(df) * 100).round(2)
    
    # Determine column types
    col_types = get_column_types(df)
    type_map = {}
    for col in df.columns:
        if col in col_types['numerical']:
            type_map[col] = 'Numerical'
        elif col in col_types['categorical']:
            type_map[col] = 'Categorical'
        elif col in col_types['datetime']:
            type_map[col] = 'Datetime'
        else:
            type_map[col] = 'Other'
    
    missing_df = pd.DataFrame({
        'Column': missing_counts.index,
        'Type': [type_map[col] for col in missing_counts.index],
        'Missing Count': missing_counts.values,
        'Missing %': missing_percent.values
    })
    
    # Only show columns with missing values
    missing_df = missing_df[missing_df['Missing Count'] > 0]
    missing_df = missing_df.sort_values('Missing Count', ascending=False)
    missing_df = missing_df.reset_index(drop=True)
    
    return missing_df


def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    Convert DataFrame to CSV bytes for download.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        CSV data as bytes
    """
    return df.to_csv(index=False).encode('utf-8')


def clean_column_name(col_name: str) -> str:
    """
    Clean column names for display and processing.
    
    Args:
        col_name: Original column name
        
    Returns:
        Cleaned column name
    """
    # Replace underscores with spaces and title case
    cleaned = col_name.replace('_', ' ').title()
    return cleaned


def get_numeric_summary(series: pd.Series) -> Dict[str, Any]:
    """
    Get comprehensive summary statistics for a numerical series.
    
    Args:
        series: pandas Series with numerical data
        
    Returns:
        Dictionary of summary statistics
    """
    return {
        'count': int(series.count()),
        'mean': float(series.mean()),
        'median': float(series.median()),
        'std': float(series.std()),
        'min': float(series.min()),
        'max': float(series.max()),
        'q25': float(series.quantile(0.25)),
        'q75': float(series.quantile(0.75)),
        'missing': int(series.isna().sum())
    }


def get_categorical_summary(series: pd.Series) -> Dict[str, Any]:
    """
    Get comprehensive summary statistics for a categorical series.
    
    Args:
        series: pandas Series with categorical data
        
    Returns:
        Dictionary of summary statistics
    """
    value_counts = series.value_counts()
    
    return {
        'count': int(series.count()),
        'unique': int(series.nunique()),
        'top_value': str(value_counts.index[0]) if len(value_counts) > 0 else "N/A",
        'top_frequency': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
        'missing': int(series.isna().sum())
    }