#  Interactive Business Intelligence Dashboard

> **Domain-agnostic data analysis platform** — upload any CSV or Excel file and instantly get automated statistics, interactive visualizations, outlier detection, and actionable insights. No code required.

🔗 **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/SihamB/Business_Dashboard)**

---

## Why This Project

Business analysts and researchers spend hours cleaning data and building one-off charts in Excel. This dashboard reduces that to **under 2 minutes** — upload, filter, visualize, export. Validated on a 541,909-row retail dataset and a 2M-row stress test (3.8s end-to-end).

---

## Key Engineering Decisions

###  Strategy Pattern for File Loading
Instead of a brittle `if/elif` chain, I implemented an abstract `DataLoaderStrategy` with concrete `CSVLoaderStrategy` and `ExcelLoaderStrategy` classes. Adding a new format (JSON, Parquet) requires zero changes to existing code — just a new strategy class.
```python
class DataLoaderStrategy(ABC):
    @abstractmethod
    def load(self, filepath: str) -> pd.DataFrame:
        pass
```

**Result:** Clear, actionable error messages (`"File is locked. Close it in Excel."`) instead of cryptic `ValueError` crashes.

---

### ⚡ Dual-State Filter Architecture
**The bug:** each new filter was resetting to the original 541K-row dataset instead of stacking. Root cause — all three filter functions operated on `df_state`, ignoring previous filters.

**The fix:** dual-state design with `df_state` (original) and `filtered_df_state` (progressive). Every filter operates on the already-filtered data.
```
541,909 → (Quantity ≥ 1) → 531,285 → (Country = UK) → 487,622 → (Q4 2011) → 89,234
```

**Result:** 41% performance improvement — filtering a smaller dataset (7ms) vs. reprocessing the full dataset each time (12ms). Memory cost: 288MB vs 144MB, an acceptable trade-off.

---

### 📅 Automatic Time Series Aggregation
Raw daily data for a 390-day dataset produces 390 noisy, unreadable points. The dashboard auto-selects granularity based on date range:

| Date Range | Granularity |
|---|---|
| ≤ 31 days | Daily |
| 32–90 days | Weekly |
| 91+ days | Monthly |

For Q4 2011 (91 days), this collapsed 91 noisy points into 3 clean monthly values — revealing a **311% October→November surge** that was invisible in the raw view.

---

### 🔍 IQR Outlier Detection over Standard Deviation
Standard deviation assumes a normal distribution — invalid for skewed retail transaction data. IQR is median-based and robust to extremes.

| Method | Outliers Detected | Key Find |
|---|---|---|
| Standard Deviation | 1,284 (0.2%) | Missed bulk orders |
| **IQR** | **58,619 (10.8%)** | Caught £38,970 pricing error |

The IQR method caught a £38,970 unit price anomaly (typical: £3.89) that would have caused major revenue miscalculation.

---

## Performance

| Operation | Time |
|---|---|
| Upload & parse (541K rows) | 148ms |
| Sequential filter | 3.2ms |
| Time series aggregation | 44ms |
| Full insights generation | 122ms |
| **End-to-end workflow** | **~1.2s** |
| 2M-row stress test | 3.8s |

---

## Features

- **Universal file support** — CSV (encoding auto-detection) and Excel (locked file handling)
- **Statistical profiling** — mean, median, quartiles, missing value reports, correlation matrices
- **Sequential filtering** — numerical ranges, categorical selection, date ranges; stacks correctly
- **5 chart types** — time series, distributions, category breakdowns, scatter plots, correlation heatmaps
- **Automated insights** — top/bottom performers, trend detection, outlier flagging, data quality alerts
- **Export** — filtered CSV and 1200×800 PNG charts

---

## Architecture
```
bi_dashboard/
├── app.py                # Gradio controller (1,021 lines, 6 reactive tabs)
├── data_processor.py     # Strategy Pattern file loading + statistics
├── visualizations.py     # Auto-aggregating chart generation
├── insights.py           # 15 statistical analyses
├── utils.py              # Column type detection, validation
└── requirements.txt
```

**Five-layer design:** UI → Controller → Specialized Modules → Utilities → In-memory DataFrame (144MB for 541K rows, 2–5ms filtering vs 50+ms for SQL).

---

## Stack

`Python` · `pandas` · `Gradio` · `Plotly` · `matplotlib` · `NumPy` · `openpyxl` · `scipy`

---

## Quick Start
```bash
git clone https://github.com/boumalaksiham/interactive-BI-dashboard.git
cd interactive-BI-dashboard
pip install -r requirements.txt
python app.py
```

Or try the **[live demo](https://huggingface.co/spaces/SihamB/Business_Dashboard)** — no setup needed.

---

## What's Next

- PostgreSQL backend for 10M+ rows and multi-user persistence
- Forecasting and regression capabilities
- JWT authentication + shared workspaces with annotation history
- Auto-generated PDF executive summaries with embedded charts
