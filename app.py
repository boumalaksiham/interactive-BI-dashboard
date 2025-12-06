# """
# Business Intelligence Dashboard - Main Gradio Application
# A comprehensive data analysis tool with interactive visualizations and automated insights.
# """

# # Configure matplotlib backend for non-interactive environments (Hugging Face Spaces)
# import matplotlib
# matplotlib.use('Agg')

# import gradio as gr
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime
# import os

# # Import custom modules
# from data_processor import DataProcessor
# from visualizations_plotly import VisualizationManager  # Use Plotly version for HF compatibility
# from insights import InsightGenerator
# from utils import (
#     validate_dataframe, 
#     get_column_types, 
#     create_summary_text,
#     get_missing_value_summary,
#     convert_df_to_csv
# )


# # ============================================================================
# # GLOBAL STATE
# # ============================================================================

# processor = DataProcessor()
# viz_manager = VisualizationManager()


# # ============================================================================
# # DATA UPLOAD TAB FUNCTIONS
# # ============================================================================

# def upload_file(file):
#     """Handle file upload and display preview with comprehensive error handling."""
#     if file is None:
#         return None, "Please upload a file", None
    
#     try:
#         # Load file
#         df, message = processor.load_file(file)
        
#         if df is None:
#             # Error occurred - display error message clearly
#             return None, f"### Upload Failed\n\n{message}", None
        
#         # Validate the DataFrame
#         is_valid, validation_msg = validate_dataframe(df)
#         if not is_valid:
#             return None, f"### Validation Failed\n\n{validation_msg}", None
        
#         # Create summary
#         summary = create_summary_text(df)
#         preview = df.head(20)
        
#         return preview, f"### Upload Successful\n\n{message}\n\n{summary}", df
        
#     except Exception as e:
#         error_msg = str(e)
#         # Make error messages more user-friendly
#         if "permission" in error_msg.lower():
#             error_msg = "Cannot access the file. Please close it if it's open in another program and try again"
#         elif "memory" in error_msg.lower():
#             error_msg = "File is too large to load into memory. Try a smaller dataset"
        
#         return None, f"### Error Loading File\n\n{error_msg}", None


# def show_data_info(df):
#     """Display detailed data information."""
#     if df is None or df.empty:
#         return "No data loaded"
    
#     info = processor.get_data_info()
#     col_types = get_column_types(df)
    
#     # Format column lists
#     numerical_cols = ", ".join(col_types['numerical']) if col_types['numerical'] else "None"
#     categorical_cols = ", ".join(col_types['categorical']) if col_types['categorical'] else "None"
#     datetime_cols = ", ".join(col_types['datetime']) if col_types['datetime'] else "None"
    
#     info_text = f"""
# ### Dataset Information

# **Dimensions:** {info['n_rows']:,} rows × {info['n_cols']} columns

# **Memory Usage:** {info['memory_mb']:.2f} MB

# **Column Types:**
# - Numerical: {len(col_types['numerical'])} columns ({numerical_cols})
# - Categorical: {len(col_types['categorical'])} columns ({categorical_cols})
# - Datetime: {len(col_types['datetime'])} columns ({datetime_cols})

# **All Columns:**
# """
    
#     for col in df.columns:
#         dtype = str(df[col].dtype)
#         info_text += f"- **{col}** ({dtype})\n"
    
#     return info_text


# # ============================================================================
# # STATISTICS TAB FUNCTIONS
# # ============================================================================

# def show_numerical_stats(df):
#     """Display statistics for numerical columns."""
#     if df is None or df.empty:
#         return pd.DataFrame()
    
#     processor.df = df
#     stats = processor.get_numerical_stats()
    
#     if stats.empty:
#         return pd.DataFrame({"Message": ["No numerical columns found"]})
    
#     return stats


# def show_categorical_stats(df):
#     """Display statistics for categorical columns."""
#     if df is None or df.empty:
#         return pd.DataFrame()
    
#     processor.df = df
#     stats = processor.get_categorical_stats()
    
#     if stats.empty:
#         return pd.DataFrame({"Message": ["No categorical columns found"]})
    
#     return stats


# def show_missing_values(df):
#     """Display missing value report."""
#     if df is None or df.empty:
#         return pd.DataFrame()
    
#     missing_df = get_missing_value_summary(df)
    
#     if missing_df.empty:
#         return pd.DataFrame({"Message": ["✅ No missing values found!"]})
    
#     return missing_df


# def show_correlation(df):
#     """Display correlation matrix."""
#     if df is None or df.empty:
#         return pd.DataFrame()
    
#     processor.df = df
#     corr = processor.get_correlation_matrix()
    
#     if corr.empty:
#         return pd.DataFrame({"Message": ["Not enough numerical columns for correlation"]})
    
#     return corr.round(3)


# # ============================================================================
# # FILTER TAB FUNCTIONS
# # ============================================================================

# def get_filter_options(df):
#     """Get available columns for filtering."""
#     if df is None or df.empty:
#         return [], [], []
    
#     col_types = get_column_types(df)
#     return col_types['numerical'], col_types['categorical'], col_types['datetime']


# def apply_numerical_filter(df, column, min_val, max_val):
#     """Apply numerical range filter."""
#     if df is None or df.empty or not column:
#         return df, f"Rows: {len(df) if df is not None else 0:,}"
    
#     filtered_df = df.copy()
    
#     if min_val is not None:
#         filtered_df = filtered_df[filtered_df[column] >= min_val]
#     if max_val is not None:
#         filtered_df = filtered_df[filtered_df[column] <= max_val]
    
#     return filtered_df, f"Filtered to {len(filtered_df):,} rows (from {len(df):,})"


# def apply_categorical_filter(df, column, selected_values):
#     """Apply categorical filter."""
#     if df is None or df.empty or not column or not selected_values:
#         return df, f"Rows: {len(df) if df is not None else 0:,}"
    
#     filtered_df = df[df[column].isin(selected_values)]
    
#     return filtered_df, f"Filtered to {len(filtered_df):,} rows (from {len(df):,})"


# def apply_date_filter(df, column, start_date, end_date):
#     """Apply date range filter."""
#     if df is None or df.empty or not column:
#         return df, f"Rows: {len(df) if df is not None else 0:,}"
    
#     filtered_df = df.copy()
    
#     try:
#         # Convert string inputs to datetime
#         if start_date:
#             start = pd.to_datetime(start_date)
#             filtered_df = filtered_df[filtered_df[column] >= start]
        
#         if end_date:
#             end = pd.to_datetime(end_date)
#             filtered_df = filtered_df[filtered_df[column] <= end]
        
#         return filtered_df, f"Filtered to {len(filtered_df):,} rows (from {len(df):,})"
    
#     except Exception as e:
#         return df, f"Error: Invalid date format. Use YYYY-MM-DD"


# # ============================================================================
# # VISUALIZATION TAB FUNCTIONS
# # ============================================================================

# def create_time_series_plot(df, date_col, value_col, aggregation):
#     """Create time series visualization."""
#     if df is None or df.empty or not date_col or not value_col:
#         return None
    
#     try:
#         fig = viz_manager.create_visualization(
#             'time_series',
#             df,
#             date_col=date_col,
#             value_col=value_col,
#             aggregation=aggregation,
#             title=f"{value_col} Over Time ({aggregation.title()})"
#         )
#         return fig
#     except Exception as e:
#         print(f"Error creating time series plot: {e}")
#         return None


# def create_distribution_plot(df, column, plot_type):
#     """Create distribution visualization."""
#     if df is None or df.empty or not column:
#         return None
    
#     try:
#         fig = viz_manager.create_visualization(
#             'distribution',
#             df,
#             column=column,
#             plot_type=plot_type,
#             title=f"Distribution of {column}"
#         )
#         return fig
#     except Exception as e:
#         print(f"Error creating distribution plot: {e}")
#         return None


# def create_category_plot(df, column, value_col, aggregation, top_n, plot_type):
#     """Create categorical analysis visualization."""
#     if df is None or df.empty or not column:
#         return None
    
#     try:
#         fig = viz_manager.create_visualization(
#             'category',
#             df,
#             column=column,
#             value_col=value_col if value_col != "None" else None,
#             aggregation=aggregation,
#             top_n=top_n,
#             plot_type=plot_type,
#             title=f"Top {top_n} {column} by {aggregation.title()}"
#         )
#         return fig
#     except Exception as e:
#         print(f"Error creating category plot: {e}")
#         return None


# def create_scatter_plot(df, x_col, y_col, color_col):
#     """Create scatter plot visualization."""
#     if df is None or df.empty or not x_col or not y_col:
#         return None
    
#     try:
#         fig = viz_manager.create_visualization(
#             'scatter',
#             df,
#             x_col=x_col,
#             y_col=y_col,
#             color_col=color_col if color_col != "None" else None,
#             title=f"{y_col} vs {x_col}"
#         )
#         return fig
#     except Exception as e:
#         print(f"Error creating scatter plot: {e}")
#         return None


# def create_heatmap_plot(df):
#     """Create correlation heatmap."""
#     if df is None or df.empty:
#         return None
    
#     try:
#         fig = viz_manager.create_visualization(
#             'heatmap',
#             df,
#             title="Correlation Heatmap"
#         )
#         return fig
#     except Exception as e:
#         print(f"Error creating heatmap: {e}")
#         return None


# def save_plot(fig):
#     """Save Plotly figure to PNG."""
#     if fig is None:
#         return None
    
#     try:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"outputs/plot_{timestamp}.png"
        
#         # Plotly figures have write_image method
#         if hasattr(fig, 'write_image'):
#             fig.write_image(filename, width=1200, height=800)
#             return filename
#         # Matplotlib figures have savefig method (fallback)
#         elif hasattr(fig, 'savefig'):
#             import matplotlib.pyplot as plt
#             fig.savefig(filename, dpi=300, bbox_inches='tight')
#             plt.close(fig)
#             return filename
#         else:
#             print(f"Warning: Received non-figure object of type {type(fig)}")
#             return None
            
#     except Exception as e:
#         print(f"Error saving plot: {e}")
#         import traceback
#         traceback.print_exc()
#         return None


# # ============================================================================
# # INSIGHTS TAB FUNCTIONS
# # ============================================================================

# def generate_insights(df):
#     """Generate automated insights from data."""
#     if df is None or df.empty:
#         return "No data available for insight generation."
    
#     try:
#         insight_gen = InsightGenerator(df)
#         insights_text = insight_gen.format_insights()
#         return insights_text
#     except Exception as e:
#         return f"Error generating insights: {str(e)}"


# # ============================================================================
# # EXPORT FUNCTIONS
# # ============================================================================

# def export_filtered_data(df):
#     """Export filtered data as CSV."""
#     if df is None or df.empty:
#         return None
    
#     try:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"outputs/filtered_data_{timestamp}.csv"
#         df.to_csv(filename, index=False)
#         return filename
#     except Exception as e:
#         print(f"Error exporting data: {e}")
#         return None


# # ============================================================================
# # GRADIO INTERFACE
# # ============================================================================

# def create_dashboard():
#     """Create the main Gradio dashboard interface."""
    
#     with gr.Blocks(title="Business Intelligence Dashboard") as demo:
        
#         # Header
#         gr.Markdown("""
#         # Business Intelligence Dashboard
#         ### Comprehensive Data Analysis & Visualization Platform
        
#         Upload your data, explore statistics, create visualizations, and discover automated insights.
#         """)
        
#         # State to store the dataframe
#         df_state = gr.State(value=None)
#         filtered_df_state = gr.State(value=None)
#         export_fig_state = gr.State(value=None)  # Store matplotlib figure for export
        
#         # ====================================================================
#         # TAB 1: DATA UPLOAD
#         # ====================================================================
        
#         with gr.Tab("Data Upload"):
#             gr.Markdown("### Upload Your Dataset")
#             gr.Markdown("Supported formats: CSV, Excel (.xlsx, .xls)")
            
#             with gr.Row():
#                 with gr.Column(scale=1):
#                     file_input = gr.File(
#                         label="Upload File",
#                         file_types=[".csv", ".xlsx", ".xls"]
#                     )
#                     upload_btn = gr.Button("Load Data", variant="primary", size="lg")
                
#                 with gr.Column(scale=2):
#                     upload_message = gr.Markdown(value="")
            
#             gr.Markdown("### Data Preview")
#             data_preview = gr.Dataframe(
#                 label="First 20 Rows",
#                 interactive=False,
#                 wrap=True
#             )
            
#             with gr.Accordion("Detailed Information", open=False):
#                 data_info = gr.Markdown()
            
#             # Upload button functionality
#             upload_btn.click(
#                 fn=upload_file,
#                 inputs=[file_input],
#                 outputs=[data_preview, upload_message, df_state]
#             ).then(
#                 fn=show_data_info,
#                 inputs=[df_state],
#                 outputs=[data_info]
#             )
        
#         # ====================================================================
#         # TAB 2: STATISTICS
#         # ====================================================================
        
#         with gr.Tab("Statistics"):
#             gr.Markdown("### Summary Statistics & Data Profiling")
            
#             with gr.Tab("Numerical Statistics"):
#                 gr.Markdown("Statistics for numerical columns (count, mean, std, min, max, quartiles)")
#                 numerical_stats_table = gr.Dataframe(
#                     label="Numerical Column Statistics",
#                     interactive=False
#                 )
#                 num_stats_btn = gr.Button("Generate Numerical Statistics")
                
#                 num_stats_btn.click(
#                     fn=show_numerical_stats,
#                     inputs=[df_state],
#                     outputs=[numerical_stats_table]
#                 )
            
#             with gr.Tab("Categorical Statistics"):
#                 gr.Markdown("Statistics for categorical columns (unique values, most common, frequencies)")
#                 categorical_stats_table = gr.Dataframe(
#                     label="Categorical Column Statistics",
#                     interactive=False
#                 )
#                 cat_stats_btn = gr.Button("Generate Categorical Statistics")
                
#                 cat_stats_btn.click(
#                     fn=show_categorical_stats,
#                     inputs=[df_state],
#                     outputs=[categorical_stats_table]
#                 )
            
#             with gr.Tab("Missing Values"):
#                 gr.Markdown("Report of missing values across all columns")
#                 missing_values_table = gr.Dataframe(
#                     label="Missing Value Analysis",
#                     interactive=False
#                 )
#                 missing_btn = gr.Button("Analyze Missing Values")
                
#                 missing_btn.click(
#                     fn=show_missing_values,
#                     inputs=[df_state],
#                     outputs=[missing_values_table]
#                 )
            
#             with gr.Tab("Correlation Matrix"):
#                 gr.Markdown("""
#                 **Correlation between numerical variables**
                
#                 Pearson Correlation Coefficient Formula:
                
#                 r = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]
                
#                 Where:
#                 - r is the correlation coefficient (-1 to +1)
#                 - xᵢ, yᵢ are individual data points
#                 - x̄, ȳ are the means
#                 - Values close to +1 indicate strong positive correlation
#                 - Values close to -1 indicate strong negative correlation
#                 - Values close to 0 indicate weak or no correlation
#                 """)
#                 correlation_table = gr.Dataframe(
#                     label="Correlation Matrix",
#                     interactive=False
#                 )
#                 corr_btn = gr.Button("Calculate Correlations")
                
#                 corr_btn.click(
#                     fn=show_correlation,
#                     inputs=[df_state],
#                     outputs=[correlation_table]
#                 )
        
#         # ====================================================================
#         # TAB 3: FILTER & EXPLORE
#         # ====================================================================
        
#         with gr.Tab("Filter & Explore"):
#             gr.Markdown("### Interactive Data Filtering")
            
#             # Real-time row count display
#             row_count_display = gr.Markdown(value="**Current Rows:** Load data to begin filtering")
#             filter_status = gr.Markdown(value="")
            
#             with gr.Row():
#                 with gr.Column():
#                     gr.Markdown("#### Numerical Filters")
#                     num_filter_col = gr.Dropdown(
#                         label="Select Numerical Column",
#                         choices=[],
#                         interactive=True,
#                         allow_custom_value=False
#                     )
#                     with gr.Row():
#                         num_min = gr.Number(label="Min Value")
#                         num_max = gr.Number(label="Max Value")
#                     apply_num_filter_btn = gr.Button("Apply Numerical Filter")
                
#                 with gr.Column():
#                     gr.Markdown("#### Categorical Filters")
#                     cat_filter_col = gr.Dropdown(
#                         label="Select Categorical Column",
#                         choices=[],
#                         interactive=True,
#                         allow_custom_value=False
#                     )
#                     cat_filter_values = gr.CheckboxGroup(
#                         label="Select Values",
#                         choices=[]
#                     )
#                     apply_cat_filter_btn = gr.Button("Apply Categorical Filter")
                
#                 with gr.Column():
#                     gr.Markdown("#### Date Range Filters")
#                     date_filter_col = gr.Dropdown(
#                         label="Select Date Column",
#                         choices=[],
#                         interactive=True,
#                         allow_custom_value=False
#                     )
#                     with gr.Row():
#                         date_start = gr.Textbox(label="Start Date (YYYY-MM-DD)", placeholder="2024-01-01")
#                         date_end = gr.Textbox(label="End Date (YYYY-MM-DD)", placeholder="2024-12-31")
#                     apply_date_filter_btn = gr.Button("Apply Date Filter")
            
#             reset_filter_btn = gr.Button("Reset All Filters", variant="secondary")
            
#             # Function to update categorical values based on selected column
#             def update_cat_values(df, col):
#                 if df is None or col is None or col not in df.columns:
#                     return gr.CheckboxGroup(choices=[], value=[])
#                 return gr.CheckboxGroup(
#                     choices=df[col].dropna().unique().tolist()[:50],  # Limit to 50 values
#                     value=[]
#                 )
            
#             # Update categorical values when column is selected
#             cat_filter_col.change(
#                 fn=update_cat_values,
#                 inputs=[df_state, cat_filter_col],
#                 outputs=[cat_filter_values]
#             )
            
#             # Update filter dropdowns when data is loaded
#             df_state.change(
#                 fn=lambda df: (
#                     gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=df.select_dtypes(include=['object', 'category']).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=df.select_dtypes(include=['datetime64']).columns.tolist() if df is not None else []),
#                     f"**Current Rows:** {len(df):,} (unfiltered)" if df is not None else "**Current Rows:** No data loaded"
#                 ),
#                 inputs=[df_state],
#                 outputs=[num_filter_col, cat_filter_col, date_filter_col, row_count_display]
#             )
            
#             gr.Markdown("### Filtered Data Preview")
#             filtered_preview = gr.Dataframe(
#                 label="Filtered Results",
#                 interactive=False
#             )
            
#             # Apply numerical filter
#             apply_num_filter_btn.click(
#                 fn=apply_numerical_filter,
#                 inputs=[df_state, num_filter_col, num_min, num_max],
#                 outputs=[filtered_df_state, filter_status]
#             ).then(
#                 fn=lambda df: (
#                     df.head(100) if df is not None else pd.DataFrame(),
#                     f"**Current Rows:** {len(df):,} (filtered)" if df is not None else "**Current Rows:** 0"
#                 ),
#                 inputs=[filtered_df_state],
#                 outputs=[filtered_preview, row_count_display]
#             )
            
#             # Apply categorical filter
#             apply_cat_filter_btn.click(
#                 fn=apply_categorical_filter,
#                 inputs=[df_state, cat_filter_col, cat_filter_values],
#                 outputs=[filtered_df_state, filter_status]
#             ).then(
#                 fn=lambda df: (
#                     df.head(100) if df is not None else pd.DataFrame(),
#                     f"**Current Rows:** {len(df):,} (filtered)" if df is not None else "**Current Rows:** 0"
#                 ),
#                 inputs=[filtered_df_state],
#                 outputs=[filtered_preview, row_count_display]
#             )
            
#             # Apply date filter
#             apply_date_filter_btn.click(
#                 fn=apply_date_filter,
#                 inputs=[df_state, date_filter_col, date_start, date_end],
#                 outputs=[filtered_df_state, filter_status]
#             ).then(
#                 fn=lambda df: (
#                     df.head(100) if df is not None else pd.DataFrame(),
#                     f"**Current Rows:** {len(df):,} (filtered)" if df is not None else "**Current Rows:** 0"
#                 ),
#                 inputs=[filtered_df_state],
#                 outputs=[filtered_preview, row_count_display]
#             )
            
#             # Reset filters
#             reset_filter_btn.click(
#                 fn=lambda df: (
#                     df, 
#                     f"Reset to {len(df):,} rows" if df is not None else "No data",
#                     f"**Current Rows:** {len(df):,} (unfiltered)" if df is not None else "**Current Rows:** No data"
#                 ),
#                 inputs=[df_state],
#                 outputs=[filtered_df_state, filter_status, row_count_display]
#             ).then(
#                 fn=lambda df: df.head(100) if df is not None else pd.DataFrame(),
#                 inputs=[filtered_df_state],
#                 outputs=[filtered_preview]
#             )
        
#         # ====================================================================
#         # TAB 4: VISUALIZATIONS
#         # ====================================================================
        
#         with gr.Tab("Visualizations"):
#             gr.Markdown("### Create Interactive Visualizations")
            
#             # Use filtered data if available, otherwise use original
#             viz_data_state = gr.State(value=None)
            
#             def get_viz_data(original_df, filtered_df):
#                 return filtered_df if filtered_df is not None else original_df
            
#             with gr.Tab("Time Series"):
#                 gr.Markdown("**Visualize trends over time**")
                
#                 with gr.Row():
#                     ts_date_col = gr.Dropdown(label="Date Column", choices=[], interactive=True, allow_custom_value=False)
#                     ts_value_col = gr.Dropdown(label="Value Column", choices=[], interactive=True, allow_custom_value=False)
#                     ts_agg = gr.Dropdown(
#                         label="Aggregation",
#                         choices=["sum", "mean", "count", "median"],
#                         value="sum",
#                         interactive=True
#                     )
                
#                 ts_plot_btn = gr.Button("Create Time Series Plot", variant="primary")
#                 ts_plot = gr.Plot(label="Time Series Plot")
                
#                 ts_plot_btn.click(
#                     fn=get_viz_data,
#                     inputs=[df_state, filtered_df_state],
#                     outputs=[viz_data_state]
#                 ).then(
#                     fn=create_time_series_plot,
#                     inputs=[viz_data_state, ts_date_col, ts_value_col, ts_agg],
#                     outputs=[ts_plot]
#                 )
            
#             with gr.Tab("Distribution"):
#                 gr.Markdown("**Analyze data distribution with histograms and box plots**")
                
#                 with gr.Row():
#                     dist_col = gr.Dropdown(label="Column", choices=[], interactive=True, allow_custom_value=False)
#                     dist_type = gr.Radio(
#                         label="Plot Type",
#                         choices=["histogram", "boxplot"],
#                         value="histogram"
#                     )
                
#                 dist_plot_btn = gr.Button("Create Distribution Plot", variant="primary")
#                 dist_plot = gr.Plot(label="Distribution Plot")
                
#                 dist_plot_btn.click(
#                     fn=get_viz_data,
#                     inputs=[df_state, filtered_df_state],
#                     outputs=[viz_data_state]
#                 ).then(
#                     fn=create_distribution_plot,
#                     inputs=[viz_data_state, dist_col, dist_type],
#                     outputs=[dist_plot]
#                 )
            
#             with gr.Tab("Category Analysis"):
#                 gr.Markdown("**Compare categories with bar charts and pie charts**")
                
#                 with gr.Row():
#                     cat_col = gr.Dropdown(label="Category Column", choices=[], interactive=True, allow_custom_value=False)
#                     cat_value_col = gr.Dropdown(
#                         label="Value Column (optional)",
#                         choices=["None"],
#                         interactive=True,
#                         allow_custom_value=False
#                     )
                
#                 with gr.Row():
#                     cat_agg = gr.Dropdown(
#                         label="Aggregation",
#                         choices=["count", "sum", "mean", "median"],
#                         value="count"
#                     )
#                     cat_top_n = gr.Slider(
#                         label="Top N Categories",
#                         minimum=3,
#                         maximum=20,
#                         value=10,
#                         step=1
#                     )
#                     cat_plot_type = gr.Radio(
#                         label="Plot Type",
#                         choices=["bar", "pie"],
#                         value="bar"
#                     )
                
#                 cat_plot_btn = gr.Button("Create Category Plot", variant="primary")
#                 cat_plot = gr.Plot(label="Category Plot")
                
#                 cat_plot_btn.click(
#                     fn=get_viz_data,
#                     inputs=[df_state, filtered_df_state],
#                     outputs=[viz_data_state]
#                 ).then(
#                     fn=create_category_plot,
#                     inputs=[viz_data_state, cat_col, cat_value_col, cat_agg, cat_top_n, cat_plot_type],
#                     outputs=[cat_plot]
#                 )
            
#             with gr.Tab("Scatter Plot"):
#                 gr.Markdown("**Explore relationships between variables**")
                
#                 with gr.Row():
#                     scatter_x = gr.Dropdown(label="X-Axis", choices=[], interactive=True, allow_custom_value=False)
#                     scatter_y = gr.Dropdown(label="Y-Axis", choices=[], interactive=True, allow_custom_value=False)
#                     scatter_color = gr.Dropdown(
#                         label="Color By (optional)",
#                         choices=["None"],
#                         interactive=True,
#                         allow_custom_value=False
#                     )
                
#                 scatter_plot_btn = gr.Button("Create Scatter Plot", variant="primary")
#                 scatter_plot = gr.Plot(label="Scatter Plot")
                
#                 scatter_plot_btn.click(
#                     fn=get_viz_data,
#                     inputs=[df_state, filtered_df_state],
#                     outputs=[viz_data_state]
#                 ).then(
#                     fn=create_scatter_plot,
#                     inputs=[viz_data_state, scatter_x, scatter_y, scatter_color],
#                     outputs=[scatter_plot]
#                 )
            
#             with gr.Tab("Correlation Heatmap"):
#                 gr.Markdown("**Visualize correlations between all numerical variables**")
                
#                 heatmap_plot_btn = gr.Button("Create Heatmap", variant="primary")
#                 heatmap_plot = gr.Plot(label="Correlation Heatmap")
                
#                 heatmap_plot_btn.click(
#                     fn=get_viz_data,
#                     inputs=[df_state, filtered_df_state],
#                     outputs=[viz_data_state]
#                 ).then(
#                     fn=create_heatmap_plot,
#                     inputs=[viz_data_state],
#                     outputs=[heatmap_plot]
#                 )
            
#             # Update dropdown choices when data changes
#             df_state.change(
#                 fn=lambda df: (
#                     gr.Dropdown(choices=df.select_dtypes(include=['datetime64']).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=df.select_dtypes(include=['object', 'category']).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=["None"] + df.columns.tolist() if df is not None else ["None"]),
#                     gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
#                     gr.Dropdown(choices=["None"] + df.columns.tolist() if df is not None else ["None"]),
#                     gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else [])
#                 ),
#                 inputs=[df_state],
#                 outputs=[ts_date_col, dist_col, cat_col, cat_value_col, scatter_x, scatter_y, scatter_color, ts_value_col]
#             )
        
#         # ====================================================================
#         # TAB 5: INSIGHTS
#         # ====================================================================
        
#         with gr.Tab("Insights"):
#             gr.Markdown("### Automated Data Insights")
#             gr.Markdown("Discover patterns, trends, and anomalies automatically")
            
#             generate_insights_btn = gr.Button(
#                 "Generate Insights",
#                 variant="primary",
#                 size="lg"
#             )
            
#             insights_output = gr.Markdown(value="Click 'Generate Insights' to analyze your data")
            
#             generate_insights_btn.click(
#                 fn=get_viz_data,
#                 inputs=[df_state, filtered_df_state],
#                 outputs=[viz_data_state]
#             ).then(
#                 fn=generate_insights,
#                 inputs=[viz_data_state],
#                 outputs=[insights_output]
#             )
        
#         # ====================================================================
#         # TAB 6: EXPORT
#         # ====================================================================
        
#         with gr.Tab("Export"):
#             gr.Markdown("### Export Your Data and Visualizations")
            
#             with gr.Row():
#                 with gr.Column():
#                     gr.Markdown("#### Export Filtered Data")
#                     export_data_btn = gr.Button("Export to CSV", variant="primary")
#                     export_data_file = gr.File(label="Download Filtered Data")
                    
#                     export_data_btn.click(
#                         fn=get_viz_data,
#                         inputs=[df_state, filtered_df_state],
#                         outputs=[viz_data_state]
#                     ).then(
#                         fn=export_filtered_data,
#                         inputs=[viz_data_state],
#                         outputs=[export_data_file]
#                     )
            
#             gr.Markdown("---")
            
#             gr.Markdown("#### Create & Export Visualization")
#             gr.Markdown("Create a quick visualization and export it as PNG")
            
#             with gr.Row():
#                 with gr.Column(scale=1):
#                     export_viz_type = gr.Radio(
#                         choices=["Distribution", "Time Series", "Category Bar Chart", "Correlation Heatmap"],
#                         label="Visualization Type",
#                         value="Distribution"
#                     )
                    
#                     # Column selectors (will be populated when data is loaded)
#                     export_column = gr.Dropdown(label="Select Column", choices=[], interactive=True)
#                     export_date_col = gr.Dropdown(label="Date Column (for Time Series)", choices=[], interactive=True, visible=False)
                    
#                     # Update column choices when data loads
#                     df_state.change(
#                         fn=lambda df: gr.Dropdown(choices=df.columns.tolist() if df is not None else []),
#                         inputs=[df_state],
#                         outputs=[export_column]
#                     )
                    
#                     df_state.change(
#                         fn=lambda df: gr.Dropdown(choices=df.select_dtypes(include=['datetime64']).columns.tolist() if df is not None else []),
#                         inputs=[df_state],
#                         outputs=[export_date_col]
#                     )
                    
#                     # Show/hide date column based on viz type
#                     def update_column_visibility(viz_type):
#                         return gr.Dropdown(visible=(viz_type == "Time Series"))
                    
#                     export_viz_type.change(
#                         fn=update_column_visibility,
#                         inputs=[export_viz_type],
#                         outputs=[export_date_col]
#                     )
                    
#                     create_export_viz_btn = gr.Button("Create Visualization", variant="primary")
                
#                 with gr.Column(scale=2):
#                     export_viz_plot = gr.Plot(label="Preview")
            
#             with gr.Row():
#                 export_viz_btn = gr.Button("Export as PNG", variant="secondary", size="lg")
#                 export_viz_file = gr.File(label="Download Visualization")
            
#             # Create visualization for export
#             def create_export_visualization(df, viz_type, column, date_col):
#                 """Create a visualization for export - returns both plot and figure."""
#                 if df is None or df.empty or not column:
#                     return None, None
                
#                 try:
#                     fig = None
#                     if viz_type == "Distribution":
#                         fig = create_distribution_plot(df, column, "histogram")
#                     elif viz_type == "Time Series" and date_col:
#                         fig = create_time_series_plot(df, date_col, column, "sum")
#                     elif viz_type == "Category Bar Chart":
#                         fig = create_category_plot(df, column, 10, "bar")
#                     elif viz_type == "Correlation Heatmap":
#                         processor.df = df
#                         corr = processor.get_correlation_matrix()
#                         if not corr.empty:
#                             fig = viz_manager.create_visualization('heatmap', df, title="Correlation Matrix")
                    
#                     # Return both the figure (for display) and the figure (for state/export)
#                     return fig, fig
#                 except Exception as e:
#                     print(f"Error creating export visualization: {e}")
#                     return None, None
            
#             create_export_viz_btn.click(
#                 fn=create_export_visualization,
#                 inputs=[df_state, export_viz_type, export_column, export_date_col],
#                 outputs=[export_viz_plot, export_fig_state]
#             )
            
#             export_viz_btn.click(
#                 fn=save_plot,
#                 inputs=[export_fig_state],
#                 outputs=[export_viz_file]
#             )
        
#         # ====================================================================
#         # FOOTER
#         # ====================================================================
        
#         gr.Markdown("""
#         ---
#         **Business Intelligence Dashboard** | Built with Python, pandas, Gradio, matplotlib, and seaborn
#         """)
    
#     return demo


# # ============================================================================
# # MAIN
# # ============================================================================

# if __name__ == "__main__":
#     # Create outputs directory if it doesn't exist
#     os.makedirs("outputs", exist_ok=True)
    
#     # Launch the dashboard
#     demo = create_dashboard()
#     demo.launch(show_error=True)



"""
Business Intelligence Dashboard - Main Gradio Application
A comprehensive data analysis tool with interactive visualizations and automated insights.
"""

# Configure matplotlib backend for non-interactive environments (Hugging Face Spaces)
import matplotlib
matplotlib.use('Agg')

import gradio as gr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Import custom modules
from data_processor import DataProcessor
from visualizations_plotly import VisualizationManager  # Use Plotly version for HF compatibility
from insights import InsightGenerator
from utils import (
    validate_dataframe, 
    get_column_types, 
    create_summary_text,
    get_missing_value_summary,
    convert_df_to_csv
)


# ============================================================================
# GLOBAL STATE
# ============================================================================

processor = DataProcessor()
viz_manager = VisualizationManager()


# ============================================================================
# DATA UPLOAD TAB FUNCTIONS
# ============================================================================

def upload_file(file):
    """Handle file upload and display preview with comprehensive error handling."""
    if file is None:
        return None, "Please upload a file", None
    
    try:
        # Load file
        df, message = processor.load_file(file)
        
        if df is None:
            # Error occurred - display error message clearly
            return None, f"### Upload Failed\n\n{message}", None
        
        # Validate the DataFrame
        is_valid, validation_msg = validate_dataframe(df)
        if not is_valid:
            return None, f"### Validation Failed\n\n{validation_msg}", None
        
        # Create summary
        summary = create_summary_text(df)
        preview = df.head(20)
        
        return preview, f"### Upload Successful\n\n{message}\n\n{summary}", df
        
    except Exception as e:
        error_msg = str(e)
        # Make error messages more user-friendly
        if "permission" in error_msg.lower():
            error_msg = "Cannot access the file. Please close it if it's open in another program and try again"
        elif "memory" in error_msg.lower():
            error_msg = "File is too large to load into memory. Try a smaller dataset"
        
        return None, f"### Error Loading File\n\n{error_msg}", None


def show_data_info(df):
    """Display detailed data information."""
    if df is None or df.empty:
        return "No data loaded"
    
    info = processor.get_data_info()
    col_types = get_column_types(df)
    
    # Format column lists
    numerical_cols = ", ".join(col_types['numerical']) if col_types['numerical'] else "None"
    categorical_cols = ", ".join(col_types['categorical']) if col_types['categorical'] else "None"
    datetime_cols = ", ".join(col_types['datetime']) if col_types['datetime'] else "None"
    
    info_text = f"""
### Dataset Information

**Dimensions:** {info['n_rows']:,} rows × {info['n_cols']} columns

**Memory Usage:** {info['memory_mb']:.2f} MB

**Column Types:**
- Numerical: {len(col_types['numerical'])} columns ({numerical_cols})
- Categorical: {len(col_types['categorical'])} columns ({categorical_cols})
- Datetime: {len(col_types['datetime'])} columns ({datetime_cols})

**All Columns:**
"""
    
    for col in df.columns:
        dtype = str(df[col].dtype)
        info_text += f"- **{col}** ({dtype})\n"
    
    return info_text


# ============================================================================
# STATISTICS TAB FUNCTIONS
# ============================================================================

def show_numerical_stats(df):
    """Display statistics for numerical columns."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    processor.df = df
    stats = processor.get_numerical_stats()
    
    if stats.empty:
        return pd.DataFrame({"Message": ["No numerical columns found"]})
    
    return stats


def show_categorical_stats(df):
    """Display statistics for categorical columns."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    processor.df = df
    stats = processor.get_categorical_stats()
    
    if stats.empty:
        return pd.DataFrame({"Message": ["No categorical columns found"]})
    
    return stats


def show_missing_values(df):
    """Display missing value report."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    missing_df = get_missing_value_summary(df)
    
    if missing_df.empty:
        return pd.DataFrame({"Message": ["✅ No missing values found!"]})
    
    return missing_df


def show_correlation(df):
    """Display correlation matrix."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    processor.df = df
    corr = processor.get_correlation_matrix()
    
    if corr.empty:
        return pd.DataFrame({"Message": ["Not enough numerical columns for correlation"]})
    
    return corr.round(3)


# ============================================================================
# FILTER TAB FUNCTIONS
# ============================================================================

def get_filter_options(df):
    """Get available columns for filtering."""
    if df is None or df.empty:
        return [], [], []
    
    col_types = get_column_types(df)
    return col_types['numerical'], col_types['categorical'], col_types['datetime']


def apply_numerical_filter(df, column, min_val, max_val):
    """Apply numerical range filter."""
    if df is None or df.empty or not column:
        return df, f"Rows: {len(df) if df is not None else 0:,}"
    
    filtered_df = df.copy()
    
    if min_val is not None:
        filtered_df = filtered_df[filtered_df[column] >= min_val]
    if max_val is not None:
        filtered_df = filtered_df[filtered_df[column] <= max_val]
    
    return filtered_df, f"Filtered to {len(filtered_df):,} rows (from {len(df):,})"


def apply_categorical_filter(df, column, selected_values):
    """Apply categorical filter."""
    if df is None or df.empty or not column or not selected_values:
        return df, f"Rows: {len(df) if df is not None else 0:,}"
    
    filtered_df = df[df[column].isin(selected_values)]
    
    return filtered_df, f"Filtered to {len(filtered_df):,} rows (from {len(df):,})"


def apply_date_filter(df, column, start_date, end_date):
    """Apply date range filter."""
    if df is None or df.empty or not column:
        return df, f"Rows: {len(df) if df is not None else 0:,}"
    
    filtered_df = df.copy()
    
    try:
        # Convert string inputs to datetime
        if start_date:
            start = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df[column] >= start]
        
        if end_date:
            end = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df[column] <= end]
        
        return filtered_df, f"Filtered to {len(filtered_df):,} rows (from {len(df):,})"
    
    except Exception as e:
        return df, f"Error: Invalid date format. Use YYYY-MM-DD"


# ============================================================================
# VISUALIZATION TAB FUNCTIONS
# ============================================================================

def create_time_series_plot(df, date_col, value_col, aggregation):
    """Create time series visualization."""
    if df is None or df.empty or not date_col or not value_col:
        return None
    
    try:
        fig = viz_manager.create_visualization(
            'time_series',
            df,
            date_col=date_col,
            value_col=value_col,
            aggregation=aggregation,
            title=f"{value_col} Over Time ({aggregation.title()})"
        )
        return fig
    except Exception as e:
        print(f"Error creating time series plot: {e}")
        return None


def create_distribution_plot(df, column, plot_type):
    """Create distribution visualization."""
    if df is None or df.empty or not column:
        return None
    
    try:
        fig = viz_manager.create_visualization(
            'distribution',
            df,
            column=column,
            plot_type=plot_type,
            title=f"Distribution of {column}"
        )
        return fig
    except Exception as e:
        print(f"Error creating distribution plot: {e}")
        return None


def create_category_plot(df, column, value_col, aggregation, top_n, plot_type):
    """Create categorical analysis visualization."""
    if df is None or df.empty or not column:
        return None
    
    try:
        fig = viz_manager.create_visualization(
            'category',
            df,
            column=column,
            value_col=value_col if value_col != "None" else None,
            aggregation=aggregation,
            top_n=top_n,
            plot_type=plot_type,
            title=f"Top {top_n} {column} by {aggregation.title()}"
        )
        return fig
    except Exception as e:
        print(f"Error creating category plot: {e}")
        return None


def create_scatter_plot(df, x_col, y_col, color_col):
    """Create scatter plot visualization."""
    if df is None or df.empty or not x_col or not y_col:
        return None
    
    try:
        fig = viz_manager.create_visualization(
            'scatter',
            df,
            x_col=x_col,
            y_col=y_col,
            color_col=color_col if color_col != "None" else None,
            title=f"{y_col} vs {x_col}"
        )
        return fig
    except Exception as e:
        print(f"Error creating scatter plot: {e}")
        return None


def create_heatmap_plot(df):
    """Create correlation heatmap."""
    if df is None or df.empty:
        return None
    
    try:
        fig = viz_manager.create_visualization(
            'heatmap',
            df,
            title="Correlation Heatmap"
        )
        return fig
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        return None


def save_plot(fig):
    """Save Plotly figure to PNG."""
    if fig is None:
        return None
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/plot_{timestamp}.png"
        
        # Plotly figures have write_image method
        if hasattr(fig, 'write_image'):
            fig.write_image(filename, width=1200, height=800)
            return filename
        # Matplotlib figures have savefig method (fallback)
        elif hasattr(fig, 'savefig'):
            import matplotlib.pyplot as plt
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            return filename
        else:
            print(f"Warning: Received non-figure object of type {type(fig)}")
            return None
            
    except Exception as e:
        print(f"Error saving plot: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# INSIGHTS TAB FUNCTIONS
# ============================================================================

def generate_insights(df):
    """Generate automated insights from data."""
    if df is None or df.empty:
        return "No data available for insight generation."
    
    try:
        insight_gen = InsightGenerator(df)
        insights_text = insight_gen.format_insights()
        return insights_text
    except Exception as e:
        return f"Error generating insights: {str(e)}"


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_filtered_data(df):
    """Export filtered data as CSV."""
    if df is None or df.empty:
        return None
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/filtered_data_{timestamp}.csv"
        df.to_csv(filename, index=False)
        return filename
    except Exception as e:
        print(f"Error exporting data: {e}")
        return None


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_dashboard():
    """Create the main Gradio dashboard interface."""
    
    with gr.Blocks(title="Business Intelligence Dashboard") as demo:
        
        # Header
        gr.Markdown("""
        # Business Intelligence Dashboard
        ### Comprehensive Data Analysis & Visualization Platform
        
        Upload your data, explore statistics, create visualizations, and discover automated insights.
        """)
        
        # State to store the dataframe
        df_state = gr.State(value=None)
        filtered_df_state = gr.State(value=None)
        export_fig_state = gr.State(value=None)  # Store matplotlib figure for export
        
        # ====================================================================
        # TAB 1: DATA UPLOAD
        # ====================================================================
        
        with gr.Tab("Data Upload"):
            gr.Markdown("### Upload Your Dataset")
            gr.Markdown("Supported formats: CSV, Excel (.xlsx, .xls)")
            
            with gr.Row():
                with gr.Column(scale=1):
                    file_input = gr.File(
                        label="Upload File",
                        file_types=[".csv", ".xlsx", ".xls"]
                    )
                    upload_btn = gr.Button("Load Data", variant="primary", size="lg")
                
                with gr.Column(scale=2):
                    upload_message = gr.Markdown(value="")
            
            gr.Markdown("### Data Preview")
            data_preview = gr.Dataframe(
                label="First 20 Rows",
                interactive=False,
                wrap=True
            )
            
            with gr.Accordion("Detailed Information", open=False):
                data_info = gr.Markdown()
            
            # Upload button functionality
            upload_btn.click(
                fn=upload_file,
                inputs=[file_input],
                outputs=[data_preview, upload_message, df_state]
            ).then(
                fn=show_data_info,
                inputs=[df_state],
                outputs=[data_info]
            )
        
        # ====================================================================
        # TAB 2: STATISTICS
        # ====================================================================
        
        with gr.Tab("Statistics"):
            gr.Markdown("### Summary Statistics & Data Profiling")
            
            with gr.Tab("Numerical Statistics"):
                gr.Markdown("Statistics for numerical columns (count, mean, std, min, max, quartiles)")
                numerical_stats_table = gr.Dataframe(
                    label="Numerical Column Statistics",
                    interactive=False
                )
                num_stats_btn = gr.Button("Generate Numerical Statistics")
                
                num_stats_btn.click(
                    fn=show_numerical_stats,
                    inputs=[df_state],
                    outputs=[numerical_stats_table]
                )
            
            with gr.Tab("Categorical Statistics"):
                gr.Markdown("Statistics for categorical columns (unique values, most common, frequencies)")
                categorical_stats_table = gr.Dataframe(
                    label="Categorical Column Statistics",
                    interactive=False
                )
                cat_stats_btn = gr.Button("Generate Categorical Statistics")
                
                cat_stats_btn.click(
                    fn=show_categorical_stats,
                    inputs=[df_state],
                    outputs=[categorical_stats_table]
                )
            
            with gr.Tab("Missing Values"):
                gr.Markdown("Report of missing values across all columns")
                missing_values_table = gr.Dataframe(
                    label="Missing Value Analysis",
                    interactive=False
                )
                missing_btn = gr.Button("Analyze Missing Values")
                
                missing_btn.click(
                    fn=show_missing_values,
                    inputs=[df_state],
                    outputs=[missing_values_table]
                )
            
            with gr.Tab("Correlation Matrix"):
                gr.Markdown("""
                **Correlation between numerical variables**
                
                Pearson Correlation Coefficient Formula:
                
                r = Σ[(xᵢ - x̄)(yᵢ - ȳ)] / √[Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²]
                
                Where:
                - r is the correlation coefficient (-1 to +1)
                - xᵢ, yᵢ are individual data points
                - x̄, ȳ are the means
                - Values close to +1 indicate strong positive correlation
                - Values close to -1 indicate strong negative correlation
                - Values close to 0 indicate weak or no correlation
                """)
                correlation_table = gr.Dataframe(
                    label="Correlation Matrix",
                    interactive=False
                )
                corr_btn = gr.Button("Calculate Correlations")
                
                corr_btn.click(
                    fn=show_correlation,
                    inputs=[df_state],
                    outputs=[correlation_table]
                )
        
        # ====================================================================
        # TAB 3: FILTER & EXPLORE
        # ====================================================================
        
        with gr.Tab("Filter & Explore"):
            gr.Markdown("### Interactive Data Filtering")
            
            # Real-time row count display
            row_count_display = gr.Markdown(value="**Current Rows:** Load data to begin filtering")
            filter_status = gr.Markdown(value="")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Numerical Filters")
                    num_filter_col = gr.Dropdown(
                        label="Select Numerical Column",
                        choices=[],
                        interactive=True,
                        allow_custom_value=False
                    )
                    with gr.Row():
                        num_min = gr.Number(label="Min Value")
                        num_max = gr.Number(label="Max Value")
                    apply_num_filter_btn = gr.Button("Apply Numerical Filter")
                
                with gr.Column():
                    gr.Markdown("#### Categorical Filters")
                    cat_filter_col = gr.Dropdown(
                        label="Select Categorical Column",
                        choices=[],
                        interactive=True,
                        allow_custom_value=False
                    )
                    cat_filter_values = gr.CheckboxGroup(
                        label="Select Values",
                        choices=[]
                    )
                    apply_cat_filter_btn = gr.Button("Apply Categorical Filter")
                
                with gr.Column():
                    gr.Markdown("#### Date Range Filters")
                    date_filter_col = gr.Dropdown(
                        label="Select Date Column",
                        choices=[],
                        interactive=True,
                        allow_custom_value=False
                    )
                    with gr.Row():
                        date_start = gr.Textbox(label="Start Date (YYYY-MM-DD)", placeholder="2024-01-01")
                        date_end = gr.Textbox(label="End Date (YYYY-MM-DD)", placeholder="2024-12-31")
                    apply_date_filter_btn = gr.Button("Apply Date Filter")
            
            reset_filter_btn = gr.Button("Reset All Filters", variant="secondary")
            
            # Function to update categorical values based on selected column
            def update_cat_values(df, col):
                if df is None or col is None or col not in df.columns:
                    return gr.CheckboxGroup(choices=[], value=[])
                return gr.CheckboxGroup(
                    choices=df[col].dropna().unique().tolist()[:50],  # Limit to 50 values
                    value=[]
                )
            
            # Update categorical values when column is selected
            cat_filter_col.change(
                fn=update_cat_values,
                inputs=[df_state, cat_filter_col],
                outputs=[cat_filter_values]
            )
            
            # Update filter dropdowns when data is loaded
            df_state.change(
                fn=lambda df: (
                    gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=df.select_dtypes(include=['object', 'category']).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=df.select_dtypes(include=['datetime64']).columns.tolist() if df is not None else []),
                    f"**Current Rows:** {len(df):,} (unfiltered)" if df is not None else "**Current Rows:** No data loaded"
                ),
                inputs=[df_state],
                outputs=[num_filter_col, cat_filter_col, date_filter_col, row_count_display]
            )
            
            gr.Markdown("### Filtered Data Preview")
            filtered_preview = gr.Dataframe(
                label="Filtered Results",
                interactive=False
            )
            
            # Apply numerical filter
            apply_num_filter_btn.click(
                fn=apply_numerical_filter,
                inputs=[df_state, num_filter_col, num_min, num_max],
                outputs=[filtered_df_state, filter_status]
            ).then(
                fn=lambda df: (
                    df.head(100) if df is not None else pd.DataFrame(),
                    f"**Current Rows:** {len(df):,} (filtered)" if df is not None else "**Current Rows:** 0"
                ),
                inputs=[filtered_df_state],
                outputs=[filtered_preview, row_count_display]
            )
            
            # Apply categorical filter
            apply_cat_filter_btn.click(
                fn=apply_categorical_filter,
                inputs=[df_state, cat_filter_col, cat_filter_values],
                outputs=[filtered_df_state, filter_status]
            ).then(
                fn=lambda df: (
                    df.head(100) if df is not None else pd.DataFrame(),
                    f"**Current Rows:** {len(df):,} (filtered)" if df is not None else "**Current Rows:** 0"
                ),
                inputs=[filtered_df_state],
                outputs=[filtered_preview, row_count_display]
            )
            
            # Apply date filter
            apply_date_filter_btn.click(
                fn=apply_date_filter,
                inputs=[df_state, date_filter_col, date_start, date_end],
                outputs=[filtered_df_state, filter_status]
            ).then(
                fn=lambda df: (
                    df.head(100) if df is not None else pd.DataFrame(),
                    f"**Current Rows:** {len(df):,} (filtered)" if df is not None else "**Current Rows:** 0"
                ),
                inputs=[filtered_df_state],
                outputs=[filtered_preview, row_count_display]
            )
            
            # Reset filters
            reset_filter_btn.click(
                fn=lambda df: (
                    df, 
                    f"Reset to {len(df):,} rows" if df is not None else "No data",
                    f"**Current Rows:** {len(df):,} (unfiltered)" if df is not None else "**Current Rows:** No data"
                ),
                inputs=[df_state],
                outputs=[filtered_df_state, filter_status, row_count_display]
            ).then(
                fn=lambda df: df.head(100) if df is not None else pd.DataFrame(),
                inputs=[filtered_df_state],
                outputs=[filtered_preview]
            )
        
        # ====================================================================
        # TAB 4: VISUALIZATIONS
        # ====================================================================
        
        with gr.Tab("Visualizations"):
            gr.Markdown("### Create Interactive Visualizations")
            
            # Use filtered data if available, otherwise use original
            viz_data_state = gr.State(value=None)
            
            def get_viz_data(original_df, filtered_df):
                return filtered_df if filtered_df is not None else original_df
            
            with gr.Tab("Time Series"):
                gr.Markdown("**Visualize trends over time**")
                
                with gr.Row():
                    ts_date_col = gr.Dropdown(label="Date Column", choices=[], interactive=True, allow_custom_value=False)
                    ts_value_col = gr.Dropdown(label="Value Column", choices=[], interactive=True, allow_custom_value=False)
                    ts_agg = gr.Dropdown(
                        label="Aggregation",
                        choices=["sum", "mean", "count", "median"],
                        value="sum",
                        interactive=True
                    )
                
                ts_plot_btn = gr.Button("Create Time Series Plot", variant="primary")
                ts_plot = gr.Plot(label="Time Series Plot")
                
                ts_plot_btn.click(
                    fn=get_viz_data,
                    inputs=[df_state, filtered_df_state],
                    outputs=[viz_data_state]
                ).then(
                    fn=create_time_series_plot,
                    inputs=[viz_data_state, ts_date_col, ts_value_col, ts_agg],
                    outputs=[ts_plot]
                )
            
            with gr.Tab("Distribution"):
                gr.Markdown("**Analyze data distribution with histograms and box plots**")
                
                with gr.Row():
                    dist_col = gr.Dropdown(label="Column", choices=[], interactive=True, allow_custom_value=False)
                    dist_type = gr.Radio(
                        label="Plot Type",
                        choices=["histogram", "boxplot"],
                        value="histogram"
                    )
                
                dist_plot_btn = gr.Button("Create Distribution Plot", variant="primary")
                dist_plot = gr.Plot(label="Distribution Plot")
                
                dist_plot_btn.click(
                    fn=get_viz_data,
                    inputs=[df_state, filtered_df_state],
                    outputs=[viz_data_state]
                ).then(
                    fn=create_distribution_plot,
                    inputs=[viz_data_state, dist_col, dist_type],
                    outputs=[dist_plot]
                )
            
            with gr.Tab("Category Analysis"):
                gr.Markdown("**Compare categories with bar charts and pie charts**")
                
                with gr.Row():
                    cat_col = gr.Dropdown(label="Category Column", choices=[], interactive=True, allow_custom_value=False)
                    cat_value_col = gr.Dropdown(
                        label="Value Column (optional)",
                        choices=["None"],
                        interactive=True,
                        allow_custom_value=False
                    )
                
                with gr.Row():
                    cat_agg = gr.Dropdown(
                        label="Aggregation",
                        choices=["count", "sum", "mean", "median"],
                        value="count"
                    )
                    cat_top_n = gr.Slider(
                        label="Top N Categories",
                        minimum=3,
                        maximum=20,
                        value=10,
                        step=1
                    )
                    cat_plot_type = gr.Radio(
                        label="Plot Type",
                        choices=["bar", "pie"],
                        value="bar"
                    )
                
                cat_plot_btn = gr.Button("Create Category Plot", variant="primary")
                cat_plot = gr.Plot(label="Category Plot")
                
                cat_plot_btn.click(
                    fn=get_viz_data,
                    inputs=[df_state, filtered_df_state],
                    outputs=[viz_data_state]
                ).then(
                    fn=create_category_plot,
                    inputs=[viz_data_state, cat_col, cat_value_col, cat_agg, cat_top_n, cat_plot_type],
                    outputs=[cat_plot]
                )
            
            with gr.Tab("Scatter Plot"):
                gr.Markdown("**Explore relationships between variables**")
                
                with gr.Row():
                    scatter_x = gr.Dropdown(label="X-Axis", choices=[], interactive=True, allow_custom_value=False)
                    scatter_y = gr.Dropdown(label="Y-Axis", choices=[], interactive=True, allow_custom_value=False)
                    scatter_color = gr.Dropdown(
                        label="Color By (optional)",
                        choices=["None"],
                        interactive=True,
                        allow_custom_value=False
                    )
                
                scatter_plot_btn = gr.Button("Create Scatter Plot", variant="primary")
                scatter_plot = gr.Plot(label="Scatter Plot")
                
                scatter_plot_btn.click(
                    fn=get_viz_data,
                    inputs=[df_state, filtered_df_state],
                    outputs=[viz_data_state]
                ).then(
                    fn=create_scatter_plot,
                    inputs=[viz_data_state, scatter_x, scatter_y, scatter_color],
                    outputs=[scatter_plot]
                )
            
            with gr.Tab("Correlation Heatmap"):
                gr.Markdown("**Visualize correlations between all numerical variables**")
                
                heatmap_plot_btn = gr.Button("Create Heatmap", variant="primary")
                heatmap_plot = gr.Plot(label="Correlation Heatmap")
                
                heatmap_plot_btn.click(
                    fn=get_viz_data,
                    inputs=[df_state, filtered_df_state],
                    outputs=[viz_data_state]
                ).then(
                    fn=create_heatmap_plot,
                    inputs=[viz_data_state],
                    outputs=[heatmap_plot]
                )
            
            # Update dropdown choices when data changes
            df_state.change(
                fn=lambda df: (
                    gr.Dropdown(choices=df.select_dtypes(include=['datetime64']).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=df.select_dtypes(include=['object', 'category']).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=["None"] + df.columns.tolist() if df is not None else ["None"]),
                    gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else []),
                    gr.Dropdown(choices=["None"] + df.columns.tolist() if df is not None else ["None"]),
                    gr.Dropdown(choices=df.select_dtypes(include=[np.number]).columns.tolist() if df is not None else [])
                ),
                inputs=[df_state],
                outputs=[ts_date_col, dist_col, cat_col, cat_value_col, scatter_x, scatter_y, scatter_color, ts_value_col]
            )
        
        # ====================================================================
        # TAB 5: INSIGHTS
        # ====================================================================
        
        with gr.Tab("Insights"):
            gr.Markdown("### Automated Data Insights")
            gr.Markdown("Discover patterns, trends, and anomalies automatically")
            
            generate_insights_btn = gr.Button(
                "Generate Insights",
                variant="primary",
                size="lg"
            )
            
            insights_output = gr.Markdown(value="Click 'Generate Insights' to analyze your data")
            
            generate_insights_btn.click(
                fn=get_viz_data,
                inputs=[df_state, filtered_df_state],
                outputs=[viz_data_state]
            ).then(
                fn=generate_insights,
                inputs=[viz_data_state],
                outputs=[insights_output]
            )
        
        # ====================================================================
        # TAB 6: EXPORT
        # ====================================================================
        
        with gr.Tab("Export"):
            gr.Markdown("### Export Your Data and Visualizations")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Export Filtered Data")
                    export_data_btn = gr.Button("Export to CSV", variant="primary")
                    export_data_file = gr.File(label="Download Filtered Data")
                    
                    export_data_btn.click(
                        fn=get_viz_data,
                        inputs=[df_state, filtered_df_state],
                        outputs=[viz_data_state]
                    ).then(
                        fn=export_filtered_data,
                        inputs=[viz_data_state],
                        outputs=[export_data_file]
                    )
            
            gr.Markdown("---")
            
            gr.Markdown("#### Create & Export Visualization")
            gr.Markdown("Create a quick visualization and export it as PNG")
            
            with gr.Row():
                with gr.Column(scale=1):
                    export_viz_type = gr.Radio(
                        choices=["Distribution", "Time Series", "Category Bar Chart", "Correlation Heatmap"],
                        label="Visualization Type",
                        value="Distribution"
                    )
                    
                    # Column selectors (will be populated when data is loaded)
                    export_column = gr.Dropdown(label="Select Column", choices=[], interactive=True)
                    export_date_col = gr.Dropdown(label="Date Column (for Time Series)", choices=[], interactive=True, visible=False)
                    
                    # Update column choices when data loads
                    df_state.change(
                        fn=lambda df: gr.Dropdown(choices=df.columns.tolist() if df is not None else []),
                        inputs=[df_state],
                        outputs=[export_column]
                    )
                    
                    df_state.change(
                        fn=lambda df: gr.Dropdown(choices=df.select_dtypes(include=['datetime64']).columns.tolist() if df is not None else []),
                        inputs=[df_state],
                        outputs=[export_date_col]
                    )
                    
                    # Show/hide date column based on viz type
                    def update_column_visibility(viz_type):
                        return gr.Dropdown(visible=(viz_type == "Time Series"))
                    
                    export_viz_type.change(
                        fn=update_column_visibility,
                        inputs=[export_viz_type],
                        outputs=[export_date_col]
                    )
                    
                    create_export_viz_btn = gr.Button("Create Visualization", variant="primary")
                
                with gr.Column(scale=2):
                    export_viz_plot = gr.Plot(label="Preview")
            
            with gr.Row():
                export_viz_btn = gr.Button("Export as PNG", variant="secondary", size="lg")
                export_viz_file = gr.File(label="Download Visualization")
            
            # Create visualization for export
            def create_export_visualization(df, viz_type, column, date_col):
                """Create a visualization for export - returns both plot and figure."""
                if df is None or df.empty:
                    return None, None
                
                try:
                    fig = None
                    if viz_type == "Distribution" and column:
                        fig = create_distribution_plot(df, column, "histogram")
                    elif viz_type == "Time Series" and date_col and column:
                        fig = create_time_series_plot(df, date_col, column, "sum")
                    elif viz_type == "Category Bar Chart" and column:
                        # Pass all required parameters for category plot
                        fig = create_category_plot(df, column, None, None, 10, "bar")
                    elif viz_type == "Correlation Heatmap":
                        # Heatmap doesn't need column selection
                        processor.df = df
                        corr = processor.get_correlation_matrix()
                        if not corr.empty:
                            fig = viz_manager.create_visualization('heatmap', df, title="Correlation Matrix")
                    
                    # Return both the figure (for display) and the figure (for state/export)
                    return fig, fig
                except Exception as e:
                    print(f"Error creating export visualization: {e}")
                    import traceback
                    traceback.print_exc()
                    return None, None
            
            create_export_viz_btn.click(
                fn=create_export_visualization,
                inputs=[df_state, export_viz_type, export_column, export_date_col],
                outputs=[export_viz_plot, export_fig_state]
            )
            
            export_viz_btn.click(
                fn=save_plot,
                inputs=[export_fig_state],
                outputs=[export_viz_file]
            )
        
        # ====================================================================
        # FOOTER
        # ====================================================================
        
        gr.Markdown("""
        ---
        **Business Intelligence Dashboard** | Built with Python, pandas, Gradio, matplotlib, and seaborn
        """)
    
    return demo


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Launch the dashboard
    demo = create_dashboard()
    demo.launch(show_error=True)
