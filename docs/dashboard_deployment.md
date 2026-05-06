# Dashboard Deployment Guide

This project includes a Streamlit dashboard in `app.py`.

## Local Run

From WSL:

```bash
cd /mnt/c/Users/efazh/Projects/clinical-survival-analysis
source .venv/bin/activate
make dashboard
```

The dashboard expects reports and figures to already exist. If they do not, run:

```bash
make pipeline
```

## Streamlit Community Cloud

Use this path when you want a simple public demo.

1. Push the repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from this repository.
4. Set the app entrypoint to `app.py`.
5. Ensure `requirements.txt` is used for dependency installation.

Important note: raw METABRIC data is ignored by Git. The dashboard can display the committed report outputs without the raw data, but rerunning the full pipeline in the hosted environment requires a data-access plan.

## Hugging Face Spaces

Use this path if you want the dashboard to sit alongside ML portfolio projects.

1. Create a new Hugging Face Space.
2. Choose the Streamlit SDK.
3. Upload or sync the repository files.
4. Keep `app.py`, `requirements.txt`, `reports/`, and `reports/figures/`.

The hosted dashboard can run from committed reports. Do not upload private, restricted, or non-redistributable clinical raw data unless the dataset license and governance rules explicitly allow it.

## Deployment Checklist

- Confirm `make test` passes locally.
- Confirm `make compile` passes locally.
- Confirm `make pipeline` has refreshed reports.
- Confirm `MODEL_CARD.md` accurately describes limitations.
- Confirm no raw/private clinical data is committed.
- Confirm dashboard tables and figures render from committed report artifacts.
