build:
	uv run python nbs/build.py
	uv run marimo export html nbs/__init__.py > docs/index.html

install: 
	python -m pip install uv
	uv venv
	uv pip install -e ".[test]"

pypi:
	uv build
	uv publish

check:
	uv run pytest
