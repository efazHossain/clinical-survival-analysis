# Data Notes

This project expects the METABRIC clinical data file at:

```text
data/raw/metabric_clinical_data.tsv
```

The raw data is intentionally ignored by Git because clinical datasets can be large or have redistribution restrictions. To reproduce the pipeline, place the METABRIC clinical TSV at the path above, then run:

```bash
python src/pipeline.py
```

The preparation step writes:

- `data/processed/metabric_survival_processed.csv`
- `data/sample/metabric_sample.csv`
- `reports/data_profile.csv`
- `reports/runtime_versions.csv`

Use `reports/data_profile.csv` to confirm row counts, event counts, event rate, and the SHA-256 hash of the raw input used for a run.
