test-coverage:
	python -m pytest tests/ -v --cov=src --cov-report=html
	python -m pytest tests/ -v --cov=src --cov-report=term-missing
