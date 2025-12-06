"""
Plotly-based visualization module for Hugging Face Spaces compatibility.
All visualizations use Plotly instead of matplotlib for proper rendering.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any


class VisualizationManager:
    """Manager for creating Plotly visualizations."""
    
    def __init__(self):
        """Initialize the visualization manager."""
        pass
    
    def create_visualization(self, viz_type: str, df: pd.DataFrame, **kwargs) -> go.Figure:
        """
        Create a visualization based on type.
        
        Args:
            viz_type: Type of visualization
            df: DataFrame to visualize
            **kwargs: Additional parameters
            
        Returns:
            Plotly Figure object
        """
        if viz_type == 'time_series':
            return self.create_time_series(df, **kwargs)
        elif viz_type == 'distribution':
            return self.create_distribution(df, **kwargs)
        elif viz_type == 'category':
            return self.create_category(df, **kwargs)
        elif viz_type == 'scatter':
            return self.create_scatter(df, **kwargs)
        elif viz_type == 'heatmap':
            return self.create_heatmap(df, **kwargs)
        else:
            raise ValueError(f"Unknown visualization type: {viz_type}")
    
    def create_time_series(self, df: pd.DataFrame, date_col: str, value_col: str, 
                          aggregation: str = 'sum', title: str = None) -> go.Figure:
        """Create time series plot."""
        # Aggregate data by date
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        # Group by date and aggregate
        if aggregation == 'sum':
            grouped = df_copy.groupby(date_col)[value_col].sum().reset_index()
        elif aggregation == 'mean':
            grouped = df_copy.groupby(date_col)[value_col].mean().reset_index()
        elif aggregation == 'count':
            grouped = df_copy.groupby(date_col)[value_col].count().reset_index()
        elif aggregation == 'median':
            grouped = df_copy.groupby(date_col)[value_col].median().reset_index()
        else:
            grouped = df_copy.groupby(date_col)[value_col].sum().reset_index()
        
        fig = px.line(grouped, x=date_col, y=value_col, 
                     title=title or f"{value_col} Over Time")
        
        fig.update_traces(line=dict(color='#2E86AB', width=2))
        fig.update_layout(
            xaxis_title=date_col,
            yaxis_title=value_col,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_distribution(self, df: pd.DataFrame, column: str, 
                           plot_type: str = 'histogram', title: str = None) -> go.Figure:
        """Create distribution plot."""
        data = df[column].dropna()
        
        if plot_type == 'histogram':
            fig = px.histogram(df, x=column, nbins=50,
                             title=title or f"Distribution of {column}")
            fig.update_traces(marker_color='#A23B72')
        elif plot_type == 'box':
            fig = px.box(df, y=column, 
                        title=title or f"Box Plot of {column}")
            fig.update_traces(marker_color='#F18F01')
        else:
            fig = px.histogram(df, x=column, nbins=50,
                             title=title or f"Distribution of {column}")
        
        # Add mean and median lines
        mean_val = data.mean()
        median_val = data.median()
        
        if plot_type == 'histogram':
            fig.add_vline(x=mean_val, line_dash="dash", line_color="red",
                         annotation_text=f"Mean: {mean_val:.2f}")
            fig.add_vline(x=median_val, line_dash="dash", line_color="green",
                         annotation_text=f"Median: {median_val:.2f}")
        
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_category(self, df: pd.DataFrame, column: str, top_n: int = 10,
                       plot_type: str = 'bar', title: str = None) -> go.Figure:
        """Create category plot."""
        # Get value counts
        value_counts = df[column].value_counts().head(top_n)
        
        if plot_type == 'bar':
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=title or f"Top {top_n} {column}",
                        labels={'x': column, 'y': 'Count'})
            fig.update_traces(marker_color='#06D6A0')
        elif plot_type == 'pie':
            fig = px.pie(values=value_counts.values, names=value_counts.index,
                        title=title or f"Top {top_n} {column}")
        else:
            fig = px.bar(x=value_counts.index, y=value_counts.values,
                        title=title or f"Top {top_n} {column}",
                        labels={'x': column, 'y': 'Count'})
        
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_scatter(self, df: pd.DataFrame, x_col: str, y_col: str,
                      color_col: str = None, title: str = None) -> go.Figure:
        """Create scatter plot."""
        if color_col and color_col in df.columns:
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                           title=title or f"{y_col} vs {x_col}",
                           trendline="ols")
        else:
            fig = px.scatter(df, x=x_col, y=y_col,
                           title=title or f"{y_col} vs {x_col}",
                           trendline="ols")
            fig.update_traces(marker=dict(color='#EF476F'))
        
        fig.update_layout(template='plotly_white')
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, title: str = None) -> go.Figure:
        """Create correlation heatmap."""
        # Calculate correlation matrix
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numerical_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title=title or "Correlation Heatmap",
            xaxis_title="",
            yaxis_title="",
            template='plotly_white',
            width=800,
            height=800
        )
        
        return fig
    
    def save_figure(self, fig: go.Figure, filename: str) -> None:
        """Save Plotly figure as PNG."""
        fig.write_image(filename, width=1200, height=800)