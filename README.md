# Data Cleaning & Reporting Automation Tool (v1)

A Python tool that loads CSV or Excel files, cleans column names, removes duplicates, standardises dates, flags missing values and invalid emails, saves a cleaned file, and generates a text report.

## Setup

On many Linux systems Python is “externally managed” (PEP 668), so use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

From the project root:

```bash
cd src && python main.py
```

Defaults to `data/raw/sample_data.csv` if you omit `--input`.

Specify a file (paths relative to `src/` if you run from `src/`):

```bash
cd src && ../.venv/bin/python main.py --input "../data/raw/sample_data.csv"
```

Optional minimum salary for review (flags numeric salaries strictly below `N`):

```bash
../.venv/bin/python main.py --input "../data/raw/sample_data.csv" --min-salary 26000
```

(Or use `.venv/bin/python main.py` from `src` if you did not activate the venv.)

Outputs (named from the input file stem, e.g. `sample_data`):

- `data/cleaned/<stem>_cleaned.csv`
- `reports/<stem>_data_quality_report.txt`

## Project structure

- `data/raw/` — input files
- `data/cleaned/` — processed output
- `reports/` — generated reports
- `src/` — Python modules
