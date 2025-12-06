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
        """Create time series plot with proper date aggregation."""
        # Aggregate data by date
        df_copy = df.copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col])
        
        # Determine appropriate time period based on date range
        date_range = (df_copy[date_col].max() - df_copy[date_col].min()).days
        
        if date_range <= 31:
            # Less than a month - group by day
            df_copy['period'] = df_copy[date_col].dt.date
            period_label = "Day"
        elif date_range <= 365:
            # Less than a year - group by week or month
            if date_range <= 90:
                df_copy['period'] = df_copy[date_col].dt.to_period('W').dt.start_time
                period_label = "Week"
            else:
                df_copy['period'] = df_copy[date_col].dt.to_period('M').dt.start_time
                period_label = "Month"
        else:
            # More than a year - group by month
            df_copy['period'] = df_copy[date_col].dt.to_period('M').dt.start_time
            period_label = "Month"
        
        # Group by period and aggregate
        if aggregation == 'sum':
            grouped = df_copy.groupby('period')[value_col].sum().reset_index()
        elif aggregation == 'mean':
            grouped = df_copy.groupby('period')[value_col].mean().reset_index()
        elif aggregation == 'count':
            grouped = df_copy.groupby('period')[value_col].count().reset_index()
        elif aggregation == 'median':
            grouped = df_copy.groupby('period')[value_col].median().reset_index()
        else:
            grouped = df_copy.groupby('period')[value_col].sum().reset_index()
        
        fig = px.line(grouped, x='period', y=value_col, 
                     title=title or f"{value_col} Over Time ({aggregation.title()} by {period_label})")
        
        fig.update_traces(line=dict(color='#2E86AB', width=3), mode='lines+markers')
        fig.update_layout(
            xaxis_title=f"Date ({period_label})",
            yaxis_title=f"{value_col} ({aggregation.title()})",
            hovermode='x unified',
            template='plotly_white',
            xaxis=dict(
                tickformat='%Y-%m-%d' if date_range <= 31 else '%Y-%m',
                tickangle=-45
            )
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
                       plot_type: str = 'bar', value_col: str = None, 
                       aggregation: str = None, title: str = None) -> go.Figure:
        """Create category plot - with optional value aggregation."""
        
        try:
            if value_col and value_col != "None" and aggregation:
                # Aggregate by category and value
                if aggregation == 'sum':
                    grouped = df.groupby(column)[value_col].sum().sort_values(ascending=False).head(top_n)
                elif aggregation == 'mean':
                    grouped = df.groupby(column)[value_col].mean().sort_values(ascending=False).head(top_n)
                elif aggregation == 'count':
                    grouped = df.groupby(column)[value_col].count().sort_values(ascending=False).head(top_n)
                else:
                    grouped = df.groupby(column)[value_col].sum().sort_values(ascending=False).head(top_n)
                
                value_label = f"{value_col} ({aggregation.title()})"
            else:
                # Simple value counts
                grouped = df[column].value_counts().head(top_n)
                value_label = "Count"
            
            if len(grouped) == 0:
                # Return empty figure with message
                fig = go.Figure()
                fig.add_annotation(
                    text=f"No data available for column: {column}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=20)
                )
                return fig
            
            if plot_type == 'bar':
                fig = px.bar(x=grouped.index, y=grouped.values,
                            title=title or f"Top {top_n} {column}",
                            labels={'x': column, 'y': value_label})
                fig.update_traces(marker_color='#06D6A0')
            elif plot_type == 'pie':
                fig = px.pie(values=grouped.values, names=grouped.index,
                            title=title or f"Top {top_n} {column}")
            else:
                fig = px.bar(x=grouped.index, y=grouped.values,
                            title=title or f"Top {top_n} {column}",
                            labels={'x': column, 'y': value_label})
            
            fig.update_layout(template='plotly_white', showlegend=False if plot_type == 'bar' else True)
            return fig
            
        except Exception as e:
            print(f"Error in category plot: {e}")
            # Return empty figure with error message
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating category plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
            return fig
    
    def create_scatter(self, df: pd.DataFrame, x_col: str, y_col: str,
                      color_col: str = None, title: str = None) -> go.Figure:
        """Create scatter plot with optional sampling for large datasets."""
        # Sample if dataset is too large (for performance)
        df_plot = df.copy()
        if len(df_plot) > 10000:
            df_plot = df_plot.sample(n=10000, random_state=42)
        
        # Remove rows with NaN in key columns
        cols_to_check = [x_col, y_col]
        if color_col and color_col != "None":
            cols_to_check.append(color_col)
        
        df_plot = df_plot.dropna(subset=cols_to_check)
        
        if len(df_plot) == 0:
            # Return empty figure with message
            fig = go.Figure()
            fig.add_annotation(
                text="No valid data points to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=20)
            )
            return fig
        
        try:
            if color_col and color_col != "None" and color_col in df_plot.columns:
                fig = px.scatter(df_plot, x=x_col, y=y_col, color=color_col,
                               title=title or f"{y_col} vs {x_col}",
                               opacity=0.6)
            else:
                fig = px.scatter(df_plot, x=x_col, y=y_col,
                               title=title or f"{y_col} vs {x_col}",
                               opacity=0.6)
                fig.update_traces(marker=dict(color='#EF476F', size=5))
            
            # Add correlation coefficient to title
            try:
                corr = df_plot[[x_col, y_col]].corr().iloc[0, 1]
                fig.update_layout(
                    title=f"{title or f'{y_col} vs {x_col}'}<br><sub>Correlation: {corr:.3f}</sub>",
                    template='plotly_white'
                )
            except:
                fig.update_layout(template='plotly_white')
            
            return fig
        except Exception as e:
            print(f"Error in scatter plot: {e}")
            # Return empty figure with error message
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating scatter plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color="red")
            )
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