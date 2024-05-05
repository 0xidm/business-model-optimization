sim:
	.python/bin/python3 scripts/sim.py 7

merge:
	.python/bin/python scripts/merge.py 20240505-163334

hiplot:
	.python/bin/python scripts/create_hiplot.py 20240505-163334

plot:
	.python/bin/python scripts/plot.py

test:
	.python/bin/pytest tests

install:
	.python/bin/pip install -e .

init:
	mkdir -p var
	python3 -m venv .python
