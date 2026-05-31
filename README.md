# Customer & Sales Lakehouse Analytics Platform

An end-to-end lakehouse analytics project that processes synthetic retail and e-commerce data through Bronze, Silver, and Gold layers using Python, PySpark, Parquet, SQL, and Power BI.

## Objective

Build a local lakehouse-style analytics pipeline that consolidates customer, sales, marketing, web behavior, and support data into business-ready analytical datasets.

## Architecture

```text
Raw CSV files
      ↓
Bronze Layer
raw ingested tables
      ↓
Silver Layer
cleaned, typed, standardized data
      ↓
Gold Layer
fact tables, dimensions, and analytics marts
      ↓
Power BI Dashboard
revenue, customer, marketing, and data quality insights
```

## Current MVP

- Synthetic retail/e-commerce data generation
- Raw CSV data layer
- PySpark Bronze ingestion
- PySpark Silver cleaning and standardization
- PySpark Gold dimensional model
- Data quality checks
- Analytical SQL queries
- Pytest validation

## Run Locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_synthetic_retail_data.py
python -m src.bronze.build_bronze
python -m src.silver.build_silver
python -m src.gold.build_gold
python -m src.quality.run_quality_checks
pytest
```

## Output Layers

```text
data/raw/
data/bronze/
data/silver/
data/gold/
```

## Planned Dashboard Pages

1. Executive Revenue Overview
2. Customer Behavior
3. Marketing & Conversion
4. Pipeline Data Quality

## Privacy

The dataset is fully synthetic and does not represent real customers, companies, transactions, or support records.
