# Data cleaning & reporting CLI

Python CLI (2025) to **clean and validate** CSV / Excel files for reporting workflows.

## Features

- Normalises **mixed date** columns to ISO dates where possible
- Drops **duplicate** rows (configurable subset of columns)
- Validates **emails** (simple pattern) and optional **numeric** columns
- Configurable **minimum salary** (or any numeric threshold on a named column)
- Writes **cleaned** output and a short **data-quality report** (Markdown)
- Paths resolved from the project root for predictable runs

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python -m clean_reporting clean \
  --input ./samples/messy_hr.csv \
  --output ./out/cleaned.csv \
  --report ./out/report.md \
  --email-col email \
  --salary-col salary \
  --min-salary 20000
```

Excel input:

```bash
python -m clean_reporting clean --input ./data.xlsx --sheet Sheet1 --output ./out/cleaned.csv --report ./out/report.md
```

## Author

[Rafael Borges](https://github.com/rafaelb1998th-ctrl)
