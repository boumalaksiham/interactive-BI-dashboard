"""
Visualization module using Strategy Pattern for flexible chart creation.
Supports multiple chart types with matplotlib, seaborn, and plotly.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import io
from datetime import datetime


# Set default style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ============================================================================
# STRATEGY PATTERN FOR VISUALIZATIONS
# ============================================================================

class VisualizationStrategy(ABC):
    """Abstract base class for visualization strategies."""
    
    @abstractmethod
    def create_plot(self, df: pd.DataFrame, **kwargs) -> plt.Figure:
        """
        Create a plot from the DataFrame.
        
        Args:
            df: pandas DataFrame
            **kwargs: Additional parameters
            
        Returns:
            matplotlib Figure object
        """
        pass


class TimeSeriesStrategy(VisualizationStrategy):
    """Strategy for creating time series plots."""
    
    def create_plot(self, df: pd.DataFrame, 
                    date_col: str, 
                    value_col: str,
                    aggregation: str = 'sum',
                    title: str = "Time Series Analysis") -> plt.Figure:
        """
        Create a time series line plot.
        
        Args:
            df: DataFrame with time series data
            date_col: Name of date column
            value_col: Name of value column to plot
            aggregation: How to aggregate data ('sum', 'mean', 'count', 'median')
            title: Plot title
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Prepare data
        plot_df = df.copy()
        plot_df[date_col] = pd.to_datetime(plot_df[date_col])
        plot_df = plot_df.sort_values(date_col)
        
        # Group by date and aggregate
        if aggregation == 'sum':
            grouped = plot_df.groupby(plot_df[date_col].dt.date)[value_col].sum()
        elif aggregation == 'mean':
            grouped = plot_df.groupby(plot_df[date_col].dt.date)[value_col].mean()
        elif aggregation == 'count':
            grouped = plot_df.groupby(plot_df[date_col].dt.date)[value_col].count()
        elif aggregation == 'median':
            grouped = plot_df.groupby(plot_df[date_col].dt.date)[value_col].median()
        else:
            grouped = plot_df.groupby(plot_df[date_col].dt.date)[value_col].sum()
        
        # Plot
        ax.plot(grouped.index, grouped.values, linewidth=2, marker='o', markersize=3)
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{value_col} ({aggregation})', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
        
        plt.tight_layout()
        return fig


class DistributionStrategy(VisualizationStrategy):
    """Strategy for creating distribution plots."""
    
    def create_plot(self, df: pd.DataFrame,
                    column: str,
                    plot_type: str = 'histogram',
                    title: str = "Distribution Analysis") -> plt.Figure:
        """
        Create a distribution plot (histogram or box plot).
        
        Args:
            df: DataFrame
            column: Column name to plot
            plot_type: Type of plot ('histogram' or 'boxplot')
            title: Plot title
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Remove NaN values
        data = df[column].dropna()
        
        if plot_type == 'histogram':
            # Create histogram
            n_bins = min(50, max(10, len(data) // 100))
            ax.hist(data, bins=n_bins, edgecolor='black', alpha=0.7, color='steelblue')
            ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
            
            # Add statistics
            mean_val = data.mean()
            median_val = data.median()
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
            ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'Median: {median_val:.2f}')
            ax.legend()
            
        elif plot_type == 'boxplot':
            # Create box plot
            box = ax.boxplot(data, vert=False, patch_artist=True,
                           boxprops=dict(facecolor='lightblue', alpha=0.7),
                           medianprops=dict(color='red', linewidth=2),
                           whiskerprops=dict(linewidth=1.5),
                           capprops=dict(linewidth=1.5))
            ax.set_xlabel(column, fontsize=12, fontweight='bold')
            ax.set_yticks([])
            
            # Add statistics text
            q1, median, q3 = data.quantile([0.25, 0.5, 0.75])
            stats_text = f'Q1: {q1:.2f}\nMedian: {median:.2f}\nQ3: {q3:.2f}'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel(column, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, axis='x' if plot_type == 'boxplot' else 'y')
        
        plt.tight_layout()
        return fig


class CategoryStrategy(VisualizationStrategy):
    """Strategy for creating categorical analysis plots."""
    
    def create_plot(self, df: pd.DataFrame,
                    column: str,
                    value_col: Optional[str] = None,
                    aggregation: str = 'count',
                    top_n: int = 10,
                    plot_type: str = 'bar',
                    title: str = "Category Analysis") -> plt.Figure:
        """
        Create a categorical plot (bar chart or pie chart).
        
        Args:
            df: DataFrame
            column: Category column name
            value_col: Value column for aggregation (None for count)
            aggregation: Aggregation method
            top_n: Show top N categories
            plot_type: Type of plot ('bar' or 'pie')
            title: Plot title
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Aggregate data
        if value_col is None or aggregation == 'count':
            data = df[column].value_counts().head(top_n)
        else:
            if aggregation == 'sum':
                data = df.groupby(column)[value_col].sum().sort_values(ascending=False).head(top_n)
            elif aggregation == 'mean':
                data = df.groupby(column)[value_col].mean().sort_values(ascending=False).head(top_n)
            elif aggregation == 'median':
                data = df.groupby(column)[value_col].median().sort_values(ascending=False).head(top_n)
            else:
                data = df.groupby(column)[value_col].sum().sort_values(ascending=False).head(top_n)
        
        if plot_type == 'bar':
            # Create bar chart
            colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
            bars = ax.barh(range(len(data)), data.values, color=colors, edgecolor='black', linewidth=0.5)
            ax.set_yticks(range(len(data)))
            ax.set_yticklabels(data.index)
            ax.set_xlabel(f'{aggregation.title()} of {value_col if value_col else "Count"}', 
                         fontsize=12, fontweight='bold')
            ax.set_ylabel(column, fontsize=12, fontweight='bold')
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, data.values)):
                ax.text(val, i, f' {val:,.0f}', va='center', fontsize=9)
            
            ax.invert_yaxis()
            
        elif plot_type == 'pie':
            # Create pie chart
            colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
            wedges, texts, autotexts = ax.pie(data.values, labels=data.index, autopct='%1.1f%%',
                                               colors=colors, startangle=90)
            
            # Enhance text
            for text in texts:
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return fig


class ScatterStrategy(VisualizationStrategy):
    """Strategy for creating scatter plots."""
    
    def create_plot(self, df: pd.DataFrame,
                    x_col: str,
                    y_col: str,
                    color_col: Optional[str] = None,
                    title: str = "Scatter Plot Analysis") -> plt.Figure:
        """
        Create a scatter plot showing relationship between variables.
        
        Args:
            df: DataFrame
            x_col: X-axis column
            y_col: Y-axis column
            color_col: Optional column for color coding
            title: Plot title
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Prepare data
        plot_df = df[[x_col, y_col]].dropna()
        
        if color_col and color_col in df.columns:
            # Colored scatter
            plot_df[color_col] = df[color_col]
            plot_df = plot_df.dropna()
            
            if df[color_col].dtype in ['object', 'category']:
                # Categorical color
                categories = plot_df[color_col].unique()
                colors = plt.cm.Set1(np.linspace(0, 1, len(categories)))
                
                for cat, color in zip(categories, colors):
                    mask = plot_df[color_col] == cat
                    ax.scatter(plot_df[mask][x_col], plot_df[mask][y_col], 
                             label=cat, alpha=0.6, s=50, color=color, edgecolors='black', linewidth=0.5)
                ax.legend(title=color_col, bbox_to_anchor=(1.05, 1), loc='upper left')
            else:
                # Numerical color
                scatter = ax.scatter(plot_df[x_col], plot_df[y_col], 
                                   c=plot_df[color_col], cmap='viridis',
                                   alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
                cbar = plt.colorbar(scatter, ax=ax)
                cbar.set_label(color_col, fontsize=10, fontweight='bold')
        else:
            # Simple scatter
            ax.scatter(plot_df[x_col], plot_df[y_col], 
                      alpha=0.6, s=50, color='steelblue', edgecolors='black', linewidth=0.5)
        
        # Add trend line
        if len(plot_df) > 1:
            z = np.polyfit(plot_df[x_col], plot_df[y_col], 1)
            p = np.poly1d(z)
            ax.plot(plot_df[x_col].sort_values(), p(plot_df[x_col].sort_values()), 
                   "r--", linewidth=2, label='Trend line', alpha=0.8)
            
            # Calculate correlation
            corr = plot_df[x_col].corr(plot_df[y_col])
            ax.text(0.05, 0.95, f'Correlation: {corr:.3f}', 
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax.set_xlabel(x_col, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_col, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


class CorrelationHeatmapStrategy(VisualizationStrategy):
    """Strategy for creating correlation heatmaps."""
    
    def create_plot(self, df: pd.DataFrame,
                    columns: Optional[List[str]] = None,
                    title: str = "Correlation Heatmap") -> plt.Figure:
        """
        Create a correlation heatmap.
        
        Args:
            df: DataFrame
            columns: List of columns to include (None for all numerical)
            title: Plot title
            
        Returns:
            matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Select columns
        if columns:
            corr_df = df[columns].select_dtypes(include=[np.number]).corr()
        else:
            corr_df = df.select_dtypes(include=[np.number]).corr()
        
        # Create heatmap
        sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   ax=ax, vmin=-1, vmax=1)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return fig


# ============================================================================
# VISUALIZATION MANAGER
# ============================================================================

class VisualizationManager:
    """Manager class for creating visualizations using strategies."""
    
    def __init__(self):
        """Initialize visualization manager with strategies."""
        self.strategies = {
            'time_series': TimeSeriesStrategy(),
            'distribution': DistributionStrategy(),
            'category': CategoryStrategy(),
            'scatter': ScatterStrategy(),
            'heatmap': CorrelationHeatmapStrategy()
        }
    
    def create_visualization(self, viz_type: str, df: pd.DataFrame, **kwargs) -> plt.Figure:
        """
        Create a visualization using the specified strategy.
        
        Args:
            viz_type: Type of visualization
            df: DataFrame
            **kwargs: Additional parameters for the strategy
            
        Returns:
            matplotlib Figure
        """
        if viz_type not in self.strategies:
            raise ValueError(f"Unknown visualization type: {viz_type}")
        
        strategy = self.strategies[viz_type]
        return strategy.create_plot(df, **kwargs)
    
    def save_figure(self, fig: plt.Figure, filename: str = None) -> str:
        """
        Save figure to file.
        
        Args:
            fig: matplotlib Figure
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"outputs/plot_{timestamp}.png"

        
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filename