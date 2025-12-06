# Business Intelligence Dashboard

A comprehensive data analysis application built with Python, pandas, and Gradio. This dashboard provides interactive data exploration, visualization, and automated insight generation for business intelligence.

## Features

### Core Capabilities
- **Data Upload & Validation**: Support for CSV and Excel files with automatic data type detection
- **Comprehensive Statistics**: Automated profiling for numerical and categorical columns
- **Interactive Filtering**: Real-time data filtering with multiple criteria
- **Rich Visualizations**: 5+ chart types with user controls and aggregation options
- **Automated Insights**: AI-powered pattern detection and trend analysis
- **Data Export**: Export filtered data and visualizations

### Visualizations
1. **Time Series Plot**: Analyze trends over time with multiple aggregation methods
2. **Distribution Plot**: Histograms and box plots for data distribution
3. **Category Analysis**: Bar charts and pie charts for categorical data
4. **Scatter Plot**: Explore relationships between numerical variables
5. **Correlation Heatmap**: Visualize correlations across all numerical features

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Installation

### Quick Start

1. **Navigate to project folder**
```bash
cd bi_dashboard
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**: Go to `http://localhost:7860`

---

### Troubleshooting Installation Issues

#### Problem: "ModuleNotFoundError: No module named 'gradio'"

This happens when `pip` and `python` use different environments.

**Solution 1 (Recommended):**
```bash
python -m pip install -r requirements.txt
python app.py
```

**Solution 2 (Direct install):**
```bash
python -m pip install gradio pandas matplotlib seaborn plotly numpy openpyxl scipy
python app.py
```

**Solution 3 (For Mac/Linux users):**
```bash
pip3 install -r requirements.txt
python3 app.py
```

**Solution 4 (For conda users):**
```bash
conda install -c conda-forge gradio pandas matplotlib seaborn plotly openpyxl scipy numpy
python app.py
```

#### Why does this happen?

The key is to use **`python -m pip`** instead of just `pip`. This ensures packages install in the same environment where you run `python app.py`.

#### Still having issues?

1. Check your Python version: `python --version` (need 3.8+)
2. Upgrade pip: `python -m pip install --upgrade pip`
3. Try installing packages one by one to identify which one fails

## Usage Guide

### 1. Data Upload
- Click the "Data Upload" tab
- Upload a CSV or Excel file
- View automatic data preview and summary statistics

### 2. Explore Statistics
- Navigate to the "Statistics" tab
- Generate numerical statistics (mean, median, std, quartiles)
- Analyze categorical variables (unique values, frequencies)
- Review missing value reports
- Examine correlation matrices

### 3. Filter Data
- Go to "Filter & Explore" tab
- Apply numerical range filters
- Select categorical values
- View real-time row counts
- Preview filtered results

### 4. Create Visualizations
- Select the "Visualizations" tab
- Choose from 5 chart types
- Select columns and aggregation methods
- Customize plot parameters (top N, colors, etc.)
- Generate interactive plots

### 5. Generate Insights
- Visit the "Insights" tab
- Click "Generate Insights"
- Review automated findings:
  - Top/bottom performers
  - Trends and patterns
  - Outliers and anomalies
  - Correlations
  - Data quality issues

### 6. Export Results
- Navigate to "Export" tab
- Download filtered data as CSV
- Save visualizations as PNG images

## Project Structure

```
bi_dashboard/
│
├── app.py                 # Main Gradio application with UI
├── data_processor.py      # Data loading and processing (Strategy Pattern)
├── visualizations.py      # Chart creation with multiple strategies
├── insights.py           # Automated insight generation
├── utils.py              # Helper functions and utilities
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── data/                # Sample datasets
    └── (your data files)
```

## Architecture

### Strategy Pattern Implementation

The application uses the **Strategy Pattern** for flexible data operations:

#### Data Loading Strategies
```python
# Abstract Strategy
class DataLoaderStrategy(ABC):
    @abstractmethod
    def load(self, file_path: str) -> pd.DataFrame:
        pass

# Concrete Strategies
class CSVLoaderStrategy(DataLoaderStrategy):
    # CSV-specific loading logic
    
class ExcelLoaderStrategy(DataLoaderStrategy):
    # Excel-specific loading logic

# Context
class DataLoader:
    def __init__(self, strategy):
        self._strategy = strategy
```

**Benefits**:
- Easy to add new file formats (JSON, Parquet, SQL)
- Separation of concerns
- Runtime strategy switching
- Testable components

#### Visualization Strategies
```python
class VisualizationStrategy(ABC):
    @abstractmethod
    def create_plot(self, df: pd.DataFrame, **kwargs):
        pass

# Concrete strategies for each chart type
- TimeSeriesStrategy
- DistributionStrategy
- CategoryStrategy
- ScatterStrategy
- CorrelationHeatmapStrategy
```

## 🔧 Key Technologies

- **pandas**: Data manipulation and analysis
- **Gradio**: Web interface and interactivity
- **matplotlib/seaborn**: Static visualizations
- **numpy**: Numerical computations
- **openpyxl**: Excel file support

## Sample Datasets

The application works best with datasets containing:
- **Datetime columns**: For time series analysis
- **Numerical columns**: For statistics and correlations
- **Categorical columns**: For segmentation and grouping

### Recommended Dataset Characteristics
- Rows: 1,000 - 1,000,000
- Columns: 5 - 50
- Mixed data types (numerical, categorical, datetime)

### Suggested Datasets
1. **E-commerce/Retail**: Sales transactions, customer data
2. **Financial**: Stock prices, transaction records
3. **Operations**: Sales performance, inventory data
4. **Any CSV/Excel**: Custom business data

## Educational Value

This project demonstrates:
- **Design Patterns**: Strategy Pattern for flexible architecture
- **pandas Mastery**: Advanced data manipulation techniques
- **UI Development**: Interactive dashboard creation with Gradio
- **Data Visualization**: Multiple chart types with customization
- **Code Organization**: Modular, maintainable structure
- **Error Handling**: Graceful handling of edge cases

## Code Quality Features

- Type hints for better code documentation
- Comprehensive docstrings
- PEP 8 style compliance
- Modular architecture
- Error handling with try/except blocks
- No hardcoded values
- Separation of concerns

## Future Enhancements

Potential additions with more development time:
- Database connectivity (PostgreSQL, MySQL)
- Advanced ML features (clustering, classification)
- Real-time data streaming
- Multi-sheet Excel support
- Custom aggregation functions
- Report generation (PDF/Word)
- User authentication
- Data caching for performance
- More visualization types (treemaps, sunburst, 3D plots)

## License

This project is created for educational purposes as part of a machine learning course assignment.

## Contributing

This is an academic project. For questions or suggestions, please contact the project author.

## Contact

For questions about this project, please reach out through the course platform.

---

**Built with Python, pandas, and Gradio**