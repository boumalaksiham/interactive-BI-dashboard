"""
Data processing module using Strategy Pattern for flexible data operations.
Handles data loading, cleaning, filtering, and transformation.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple
import io


# ============================================================================
# STRATEGY PATTERN IMPLEMENTATION
# ============================================================================

class DataLoaderStrategy(ABC):
    """Abstract base class for data loading strategies."""
    
    @abstractmethod
    def load(self, file_path: str) -> pd.DataFrame:
        """
        Load data from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Loaded DataFrame
        """
        pass


class CSVLoaderStrategy(DataLoaderStrategy):
    """Strategy for loading CSV files."""
    
    def load(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with automatic type inference and detailed error handling."""
        try:
            df = pd.read_csv(file_path, parse_dates=True, infer_datetime_format=True)
            
            # Validate the loaded data
            if df.empty:
                raise ValueError("The CSV file is empty (contains no data rows)")
            
            if len(df.columns) == 0:
                raise ValueError("The CSV file has no columns")
            
            # Check for all-null columns
            all_null_cols = df.columns[df.isnull().all()].tolist()
            if len(all_null_cols) == len(df.columns):
                raise ValueError("All columns in the CSV file contain only missing values")
            
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("The CSV file is empty or contains no data")
        except pd.errors.ParserError as e:
            raise ValueError(f"CSV parsing error: The file may have inconsistent columns or formatting. Details: {str(e)}")
        except FileNotFoundError:
            raise ValueError("File not found. Please check the file path and try again")
        except PermissionError:
            raise ValueError("Permission denied. Cannot read the file - it may be open in another program")
        except UnicodeDecodeError:
            raise ValueError("Encoding error: The file may not be a valid CSV or uses an unsupported encoding. Try saving it as UTF-8")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")


class ExcelLoaderStrategy(DataLoaderStrategy):
    """Strategy for loading Excel files."""
    
    def load(self, file_path: str) -> pd.DataFrame:
        """Load Excel file from first sheet with detailed error handling."""
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Validate the loaded data
            if df.empty:
                raise ValueError("The Excel file is empty (contains no data rows)")
            
            if len(df.columns) == 0:
                raise ValueError("The Excel file has no columns")
            
            # Check for all-null columns
            all_null_cols = df.columns[df.isnull().all()].tolist()
            if len(all_null_cols) == len(df.columns):
                raise ValueError("All columns in the Excel file contain only missing values")
            
            return df
            
        except FileNotFoundError:
            raise ValueError("File not found. Please check the file path and try again")
        except PermissionError:
            raise ValueError("Permission denied. Cannot read the file - it may be open in Excel or another program")
        except ValueError as e:
            if "Excel file format" in str(e):
                raise ValueError("Invalid Excel file format. The file may be corrupted or not a valid Excel file")
            raise e
        except ImportError:
            raise ValueError("Excel support not installed. Please run: pip install openpyxl")
        except Exception as e:
            error_msg = str(e).lower()
            if "no module named" in error_msg:
                raise ValueError("Missing required library. Please install openpyxl: pip install openpyxl")
            elif "corrupted" in error_msg or "damaged" in error_msg:
                raise ValueError("The Excel file appears to be corrupted or damaged. Try re-saving it")
            else:
                raise ValueError(f"Error loading Excel file: {str(e)}")


class DataLoader:
    """Context class that uses loading strategies."""
    
    def __init__(self, strategy: Optional[DataLoaderStrategy] = None):
        """
        Initialize with an optional strategy.
        
        Args:
            strategy: DataLoaderStrategy instance
        """
        self._strategy = strategy
    
    def set_strategy(self, strategy: DataLoaderStrategy):
        """Set or change the loading strategy."""
        self._strategy = strategy
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data using the current strategy.
        
        Args:
            file_path: Path to file
            
        Returns:
            Loaded DataFrame
        """
        if self._strategy is None:
            # Auto-detect strategy based on file extension
            if file_path.endswith('.csv'):
                self._strategy = CSVLoaderStrategy()
            elif file_path.endswith(('.xlsx', '.xls')):
                self._strategy = ExcelLoaderStrategy()
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")
        
        return self._strategy.load(file_path)


# ============================================================================
# DATA PROCESSING CLASS
# ============================================================================

class DataProcessor:
    """Main class for data processing operations."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None
        self.loader = DataLoader()
    
    def load_file(self, file_obj) -> Tuple[pd.DataFrame, str]:
        """
        Load data from a file object with comprehensive validation.
        
        Args:
            file_obj: File object from Gradio
            
        Returns:
            Tuple of (DataFrame, success_message)
        """
        try:
            # Get file path from the file object
            file_path = file_obj.name if hasattr(file_obj, 'name') else file_obj
            
            # Check file size (warn if > 500MB)
            import os
            if os.path.exists(file_path):
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                if file_size_mb > 500:
                    return None, f"File is too large ({file_size_mb:.1f}MB). Please use files smaller than 500MB for optimal performance"
            
            # Load the data
            self.df = self.loader.load_data(file_path)
            self.original_df = self.df.copy()
            
            # Validate minimum requirements
            if len(self.df) < 2:
                return None, "Dataset must have at least 2 rows for meaningful analysis"
            
            if len(self.df.columns) < 2:
                return None, "Dataset must have at least 2 columns for analysis"
            
            # Check for reasonable column count
            if len(self.df.columns) > 200:
                return None, f"Dataset has {len(self.df.columns)} columns. Please limit to 200 columns or less for optimal performance"
            
            # Auto-convert potential date columns
            self._auto_convert_dates()
            
            # Check data quality
            total_missing = self.df.isna().sum().sum()
            total_cells = self.df.size
            missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
            
            # Warn if mostly empty
            if missing_pct > 90:
                return None, f"Dataset is {missing_pct:.1f}% empty. Please provide a dataset with more complete data"
            
            # Success message with data quality info
            message = f"Successfully loaded {len(self.df):,} rows and {len(self.df.columns)} columns"
            
            if missing_pct > 50:
                message += f"\n\nWarning: Dataset has {missing_pct:.1f}% missing values. Results may be affected"
            
            return self.df, message
            
        except ValueError as e:
            # These are our custom error messages - pass them through
            return None, str(e)
        except Exception as e:
            error_msg = f"Unexpected error loading file: {str(e)}"
            return None, error_msg
    
    def _auto_convert_dates(self):
        """Automatically detect and convert date columns."""
        if self.df is None:
            return
        
        for col in self.df.select_dtypes(include=['object']).columns:
            # Try to convert to datetime
            try:
                # Sample first non-null value
                sample = self.df[col].dropna().head(1)
                if len(sample) > 0:
                    pd.to_datetime(sample, errors='raise')
                    # If successful, convert entire column
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            except:
                continue
    
    def get_data_preview(self, n_rows: int = 10) -> pd.DataFrame:
        """
        Get preview of the data.
        
        Args:
            n_rows: Number of rows to show
            
        Returns:
            DataFrame with first n rows
        """
        if self.df is None:
            return pd.DataFrame()
        return self.df.head(n_rows)
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get basic information about the dataset.
        
        Returns:
            Dictionary with dataset information
        """
        if self.df is None:
            return {}
        
        info = {
            'n_rows': len(self.df),
            'n_cols': len(self.df.columns),
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'memory_mb': self.df.memory_usage(deep=True).sum() / 1024**2,
            'missing_cells': self.df.isna().sum().sum()
        }
        
        return info
    
    def get_numerical_stats(self) -> pd.DataFrame:
        """
        Get summary statistics for numerical columns.
        
        Returns:
            DataFrame with statistics including median with column names as first column
        """
        if self.df is None:
            return pd.DataFrame()
        
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) == 0:
            return pd.DataFrame()
        
        stats_df = self.df[numerical_cols].describe().T
        
        # Rename 50% to median for clarity
        stats_df = stats_df.rename(columns={'50%': 'median'})
        
        # Add missing value information
        stats_df['missing'] = self.df[numerical_cols].isna().sum()
        stats_df['missing_pct'] = (stats_df['missing'] / len(self.df) * 100).round(2)
        
        # Reset index to make column names a regular column
        stats_df = stats_df.reset_index()
        stats_df = stats_df.rename(columns={'index': 'Column'})
        
        # Reorder columns for better readability
        column_order = ['Column', 'count', 'mean', 'median', 'std', 'min', '25%', '75%', 'max', 'missing', 'missing_pct']
        # Only include columns that exist
        column_order = [col for col in column_order if col in stats_df.columns]
        stats_df = stats_df[column_order]
        
        return stats_df
    
    def get_categorical_stats(self) -> pd.DataFrame:
        """
        Get summary statistics for categorical columns including value counts.
        
        Returns:
            DataFrame with statistics
        """
        if self.df is None:
            return pd.DataFrame()
        
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) == 0:
            return pd.DataFrame()
        
        stats_list = []
        for col in categorical_cols:
            value_counts = self.df[col].value_counts()
            
            # Get top 5 values with their counts for display
            top_values = []
            for i, (val, count) in enumerate(value_counts.head(5).items()):
                top_values.append(f"{val} ({count})")
            
            stats = {
                'Column': col,
                'Unique Values': self.df[col].nunique(),
                'Mode (Most Common)': value_counts.index[0] if len(value_counts) > 0 else 'N/A',
                'Mode Count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                'Top 5 Value Counts': ', '.join(top_values) if top_values else 'N/A',
                'Missing': self.df[col].isna().sum(),
                'Missing %': round(self.df[col].isna().sum() / len(self.df) * 100, 2)
            }
            stats_list.append(stats)
        
        return pd.DataFrame(stats_list)
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix for numerical columns.
        
        Returns:
            Correlation matrix DataFrame
        """
        if self.df is None:
            return pd.DataFrame()
        
        numerical_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numerical_cols) < 2:
            return pd.DataFrame()
        
        return self.df[numerical_cols].corr()
    
    def apply_filters(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply multiple filters to the DataFrame.
        
        Args:
            filters: Dictionary of filter specifications
            
        Returns:
            Filtered DataFrame
        """
        if self.df is None or not filters:
            return self.df if self.df is not None else pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        for col, filter_spec in filters.items():
            if col not in filtered_df.columns:
                continue
            
            filter_type = filter_spec.get('type')
            
            if filter_type == 'range':
                # Numerical range filter
                min_val = filter_spec.get('min')
                max_val = filter_spec.get('max')
                if min_val is not None:
                    filtered_df = filtered_df[filtered_df[col] >= min_val]
                if max_val is not None:
                    filtered_df = filtered_df[filtered_df[col] <= max_val]
            
            elif filter_type == 'categorical':
                # Categorical filter
                selected_values = filter_spec.get('values', [])
                if selected_values:
                    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
            
            elif filter_type == 'date_range':
                # Date range filter
                start_date = filter_spec.get('start')
                end_date = filter_spec.get('end')
                if start_date:
                    filtered_df = filtered_df[filtered_df[col] >= pd.to_datetime(start_date)]
                if end_date:
                    filtered_df = filtered_df[filtered_df[col] <= pd.to_datetime(end_date)]
        
        return filtered_df
    
    def clean_data(self, 
                   drop_duplicates: bool = False,
                   fill_numerical: Optional[str] = None,
                   fill_categorical: Optional[str] = None) -> Tuple[pd.DataFrame, str]:
        """
        Clean the data with specified operations.
        
        Args:
            drop_duplicates: Whether to drop duplicate rows
            fill_numerical: Method for filling numerical NAs ('mean', 'median', 'zero')
            fill_categorical: Method for filling categorical NAs ('mode', 'unknown')
            
        Returns:
            Tuple of (cleaned DataFrame, summary message)
        """
        if self.df is None:
            return None, "No data loaded"
        
        cleaned_df = self.df.copy()
        operations = []
        
        # Drop duplicates
        if drop_duplicates:
            before = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates()
            after = len(cleaned_df)
            if before > after:
                operations.append(f"Removed {before - after} duplicate rows")
        
        # Fill numerical missing values
        if fill_numerical:
            numerical_cols = cleaned_df.select_dtypes(include=[np.number]).columns
            for col in numerical_cols:
                missing_before = cleaned_df[col].isna().sum()
                if missing_before > 0:
                    if fill_numerical == 'mean':
                        cleaned_df[col].fillna(cleaned_df[col].mean(), inplace=True)
                    elif fill_numerical == 'median':
                        cleaned_df[col].fillna(cleaned_df[col].median(), inplace=True)
                    elif fill_numerical == 'zero':
                        cleaned_df[col].fillna(0, inplace=True)
                    operations.append(f"Filled {missing_before} missing values in {col}")
        
        # Fill categorical missing values
        if fill_categorical:
            categorical_cols = cleaned_df.select_dtypes(include=['object', 'category']).columns
            for col in categorical_cols:
                missing_before = cleaned_df[col].isna().sum()
                if missing_before > 0:
                    if fill_categorical == 'mode':
                        mode_val = cleaned_df[col].mode()
                        if len(mode_val) > 0:
                            cleaned_df[col].fillna(mode_val[0], inplace=True)
                    elif fill_categorical == 'unknown':
                        cleaned_df[col].fillna('Unknown', inplace=True)
                    operations.append(f"Filled {missing_before} missing values in {col}")
        
        self.df = cleaned_df
        
        if operations:
            message = "✅ Cleaning complete:\n" + "\n".join(f"• {op}" for op in operations)
        else:
            message = "No cleaning operations performed"
        
        return self.df, message
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        """Get the current DataFrame."""
        return self.df
    
    def reset_data(self):
        """Reset to original loaded data."""
        if self.original_df is not None:
            self.df = self.original_df.copy()