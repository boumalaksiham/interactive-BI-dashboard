# Interactive Business Intelligence Dashboard

A **Gradio** application for exploring uploaded tabular data with pandas and Plotly. Users can inspect data, apply filters, create visualizations, view descriptive insights and export filtered rows or charts.

## An example analysis session

For a sales table, a reviewer can inspect missing values, filter to a relevant subset, choose numeric columns for a compatible chart, and export the filtered rows for follow-up. Date-based views additionally require a suitable date column. The dashboard operates on the uploaded schema rather than assuming one fixed business dataset.

**Design choice:** keep loading/filtering, chart construction, and descriptive insights in separate modules. This lets a reader inspect the transformation behind a chart and distinguish calculated summaries from business interpretation. Automated insights summarize data patterns; they do not supply evidence of causation.

**Start here:** [app.py](app.py) connects the interface to [data_processor.py](data_processor.py), [visualizations_plotly.py](visualizations_plotly.py), and [insights.py](insights.py).

## Workflow

1. Upload a CSV or Excel workbook.
2. Inspect columns, summary statistics and missing values.
3. Apply filters and create compatible visualizations.
4. Explore descriptive insights and correlations.
5. Export filtered data as CSV or a chart as PNG.

The interface accepts `.csv`, `.xlsx` and `.xls`. Modern Excel files use openpyxl; legacy `.xls` files may require an additional reader such as xlrd, which is not included in the dependency manifest. Start with CSV or `.xlsx`.

## Setup

```bash
git clone https://github.com/boumalaksiham/interactive-BI-dashboard.git
cd interactive-BI-dashboard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Use the local address printed by Gradio after launch. The pinned UI dependency is Gradio 5.50.0; the other dependencies mostly use version ranges, so this is not a fully locked environment. The application does not require an LLM API key.

Sample files under `data/` use Git LFS. If a sample opens as a text pointer rather than a dataset, install Git LFS and run `git lfs pull` in the checkout. You can also upload your own dataset.

## Modules and artifacts

| Path | Purpose |
|---|---|
| [app.py](app.py) | Gradio interface, callbacks and exports |
| [data_processor.py](data_processor.py) | CSV/Excel loading, filtering, preprocessing and summaries |
| [visualizations_plotly.py](visualizations_plotly.py) | Plotly visualization helpers |
| [insights.py](insights.py) | Descriptive insights |
| [utils.py](utils.py) | Shared helpers |
| [data/](data/) | Sample retail/Amazon datasets |

The application creates `outputs/` for exported files. Exports are generated files, not committed benchmark results.

## Data requirements and troubleshooting

- Use a rectangular table with column headers. CSV encoding, malformed rows and mixed types may affect loading.
- Time-series charts need a suitable date column; numeric charts need numeric values.
- Empty filters or incompatible column selections may produce no visualization.
- PNG export uses Plotly and Kaleido. If it fails, inspect the terminal error for dependency or renderer requirements; interactive chart display and static export are separate paths.
- Large files are processed in memory. Runtime and memory use depend on data shape and machine resources.

## Evaluation scope

The old stress-test and performance figures are not retained as verified benchmarks because a repeatable benchmark report is not included. Descriptive correlations and automated insights identify patterns, not causal effects or guaranteed business outcomes.

To evaluate the dashboard, preserve the input schema/sample count, machine resources, environment, operation measured and timing method. Test malformed files, missing values, date parsing, empty filters and exports separately.

## Next steps

Add upload/processing regression checks, a reproducible performance benchmark, an environment lockfile and renderer-specific export instructions based on a tested setup.
