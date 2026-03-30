#  Interactive Business Intelligence Dashboard

> **Domain-agnostic data analysis platform** — upload any CSV or Excel file and instantly get automated statistics, interactive visualizations, outlier detection, and actionable insights. No code required.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?style=flat-square&logo=pandas)
![Gradio](https://img.shields.io/badge/Gradio-4.0-FF7C00?style=flat-square&logo=gradio)
![Plotly](https://img.shields.io/badge/Plotly-5.0-3F4F75?style=flat-square&logo=plotly)

🔗 **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/SihamB/Business_Dashboard)**

---

##  What is This?

Business analysts and researchers spend hours cleaning data and building one-off charts in Excel. This dashboard reduces that to **under 2 minutes** — upload, filter, visualize, export.

Validated on a **541,909-row retail dataset** and a **2M-row stress test** (3.8s end-to-end).

No SQL. No setup. No code.

---

##  System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Gradio UI Layer                          │
│         6 reactive tabs — upload, filter, visualize          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Controller (app.py)                         │
│     Orchestrates all tab interactions and state management   │
└──────┬───────────────┬──────────────────┬───────────────────┘
       │               │                  │
       ▼               ▼                  ▼
┌────────────┐  ┌─────────────┐  ┌───────────────┐
│   Data     │  │Visualization│  │   Insights    │
│ Processor  │  │   Engine    │  │   Engine      │
│(Strategy   │  │(Auto-agg,   │  │(15 statistical│
│ Pattern)   │  │ 5 charts)   │  │  analyses)    │
└────────────┘  └─────────────┘  └───────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│              In-Memory DataFrame (dual-state)                │
│         df_state (original) + filtered_df_state              │
│         144MB for 541K rows │ 2–5ms filtering               │
└─────────────────────────────────────────────────────────────┘
```

---

##  Key Engineering Decisions

### 1. Strategy Pattern for File Loading

Instead of a brittle `if/elif` chain, I implemented an abstract `DataLoaderStrategy` with concrete `CSVLoaderStrategy` and `ExcelLoaderStrategy` classes. Adding a new format (JSON, Parquet) requires zero changes to existing code — just a new strategy class.
```python
class DataLoaderStrategy(ABC):
    @abstractmethod
    def load(self, filepath: str) -> pd.DataFrame:
        pass

class CSVLoaderStrategy(DataLoaderStrategy):
    def load(self, filepath: str) -> pd.DataFrame:
        # auto-detects encoding, handles malformed rows
        ...

class ExcelLoaderStrategy(DataLoaderStrategy):
    def load(self, filepath: str) -> pd.DataFrame:
        # handles locked files, multi-sheet workbooks
        ...
```

**Result:** Clear, actionable error messages (`"File is locked. Close it in Excel."`) instead of cryptic `ValueError` crashes.

---

### 2. Dual-State Filter Architecture

**The bug:** each new filter was resetting to the original 541K-row dataset instead of stacking. Root cause — all three filter functions operated on `df_state`, ignoring previous filters.

**The fix:** dual-state design with `df_state` (original) and `filtered_df_state` (progressive). Every filter operates on the already-filtered data.
```
541,909 → (Quantity ≥ 1) → 531,285 → (Country = UK) → 487,622 → (Q4 2011) → 89,234
```

**Result:** 41% performance improvement — filtering a smaller dataset (7ms) vs. reprocessing the full dataset each time (12ms). Memory cost: 288MB vs 144MB — an acceptable trade-off.

---

### 3. Automatic Time Series Aggregation

Raw daily data for a 390-day dataset produces 390 noisy, unreadable data points. The dashboard auto-selects granularity based on date range:

| Date Range | Granularity |
|---|---|
| ≤ 31 days | Daily |
| 32–90 days | Weekly |
| 91+ days | Monthly |

For Q4 2011 (91 days), this collapsed 91 noisy points into 3 clean monthly values — revealing a **311% October→November revenue surge** that was invisible in the raw daily view.

---

### 4. IQR Outlier Detection over Standard Deviation

Standard deviation assumes a normal distribution — invalid for skewed retail transaction data. IQR is median-based and robust to extremes.

| Method | Outliers Detected | Key Finding |
|---|---|---|
| Standard Deviation | 1,284 (0.2%) | Missed bulk orders |
| **IQR (chosen)** | **58,619 (10.8%)** | Caught £38,970 pricing error |

The IQR method caught a **£38,970 unit price anomaly** (typical: £3.89) that would have caused major revenue miscalculation if left undetected.

---

##  Performance

| Operation | Time |
|---|---|
| Upload & parse (541K rows) | 148ms |
| Sequential filter | 3.2ms |
| Time series aggregation | 44ms |
| Full insights generation | 122ms |
| **End-to-end workflow** | **~1.2s** |
| 2M-row stress test | 3.8s |

---

##  Features

- **Universal file support** — CSV (encoding auto-detection) and Excel (locked file handling)
- **Statistical profiling** — mean, median, quartiles, missing value reports, correlation matrices
- **Sequential filtering** — numerical ranges, categorical selection, date ranges — stacks correctly
- **5 chart types** — time series, distributions, category breakdowns, scatter plots, correlation heatmaps
- **Automated insights** — top/bottom performers, trend detection, outlier flagging, data quality alerts
- **Export** — filtered CSV and 1200×800 PNG charts

---

##  Project Structure
```
bi_dashboard/
├── app.py               # Gradio controller (1,021 lines, 6 reactive tabs)
├── data_processor.py    # Strategy Pattern file loading + statistics
├── visualizations.py    # Auto-aggregating chart generation
├── insights.py          # 15 statistical analyses
├── utils.py             # Column type detection, validation
└── requirements.txt
```

**Five-layer design:** UI → Controller → Specialized Modules → Utilities → In-memory DataFrame.

---

##  Quick Start
```bash
git clone https://github.com/boumalaksiham/interactive-BI-dashboard.git
cd interactive-BI-dashboard
pip install -r requirements.txt
python app.py
```

Or try the **[live demo](https://huggingface.co/spaces/SihamB/Business_Dashboard)** — no setup needed.

---

##  Validated On

- **Online Retail Dataset** — 541,909 rows, 8 columns, UK e-commerce transactions
- **2M-row stress test** — synthetic dataset, 3.8s end-to-end processing
- **Edge cases** — locked Excel files, mixed encodings, missing values, negative quantities, extreme outliers

---

##  Roadmap

- [ ] PostgreSQL backend for 10M+ rows and multi-user persistence
- [ ] Forecasting and regression capabilities
- [ ] JWT authentication + shared workspaces with annotation history
- [ ] Auto-generated PDF executive summaries with embedded charts
- [ ] Natural language querying ("show me revenue by country last quarter")

---

##  Author

**Siham Boumalak**
M.S. Artificial Intelligence — Northeastern University, Khoury College of Computer Sciences
Concentration: Machine Learning | Expected 2027

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](linkedin.com/in/siham-boumalak-11014b210)
[![GitHub](https://img.shields.io/badge/GitHub-boumalaksiham-181717?style=flat-square&logo=github)](https://github.com/boumalaksiham)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Hugging%20Face-FF7C00?style=flat-square&logo=huggingface)](https://huggingface.co/spaces/SihamB/Business_Dashboard)

---

##  Tech Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | Gradio 4.0 |
| Data Processing | pandas 2.0, NumPy |
| Visualization | Plotly, matplotlib |
| File Handling | openpyxl, chardet |
| Statistics | scipy, pandas |
| Design Pattern | Strategy Pattern (file loading) |
| Deployment | Hugging Face Spaces |
