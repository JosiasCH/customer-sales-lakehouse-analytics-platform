# Architecture

```text
Raw CSV files
      ↓
Bronze Layer
      ↓
Silver Layer
      ↓
Gold Layer
      ↓
Power BI
```

Bronze stores raw ingested data. Silver stores cleaned, typed, standardized, and deduplicated datasets. Gold stores business-ready fact tables, dimensions, and analytics marts.
