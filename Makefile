plot:
	.python/bin/python scripts/plot.py

sim:
	.python/bin/python3 ./scripts/sim.py

test:
	.python/bin/pytest ./tests

install:
	.python/bin/pip install -e .

init:
	mkdir -p var
	python3.10 -m venv .python
