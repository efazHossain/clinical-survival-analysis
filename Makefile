.PHONY: install test compile pipeline dashboard report clean

PYTHON ?= python
STREAMLIT ?= streamlit

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

test:
	pytest

compile:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m py_compile src/*.py app.py

pipeline:
	$(PYTHON) src/pipeline.py

report:
	$(PYTHON) src/evaluate_models.py

dashboard:
	$(STREAMLIT) run app.py

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
