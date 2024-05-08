sim:
	.python/bin/python3 scripts/sim.py 7

merge:
	@echo usage: .python/bin/python scripts/merge.py 20240505-163334

hiplot:
	@echo usage: .python/bin/python scripts/create_hiplot.py 20240508-114851

plot:
	.python/bin/python scripts/plot.py

test:
	.python/bin/pytest tests

install:
	.python/bin/pip install -e .

init:
	mkdir -p var
	python3 -m venv .python
