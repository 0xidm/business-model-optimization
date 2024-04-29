run:
	.python/bin/python3 ./scripts/sim.py

install:
	.python/bin/pip install -e .

init:
	mkdir -p var
	python3.10 -m venv .python
