sim:
	.python/bin/python3 scripts/sim.py 7

merge:
	.python/bin/python scripts/merge.py

hiplot:
	.python/bin/python scripts/create_hiplot.py

plot:
	.python/bin/python scripts/plot.py

test:
	.python/bin/pytest tests

install:
	.python/bin/pip install -e .

init:
	mkdir -p var
	python3 -m venv .python
