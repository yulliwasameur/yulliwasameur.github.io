PYTHON ?= python3
export PYTHONPATH := src
export MPLCONFIGDIR := $(CURDIR)/.mplconfig

.PHONY: test campaign paper-macros paper-macros-check clean-results

test:
	$(PYTHON) -m unittest discover -s tests -v

campaign:
	$(PYTHON) -m cigma.cli campaign --config configs/default.yaml --output results/default

paper-macros:
	$(PYTHON) scripts/export_paper_macros.py \
		--default-results results/default \
		--llm-results results/llm/evaluation \
		--output ../paper/results_macros.tex

paper-macros-check:
	$(PYTHON) scripts/export_paper_macros.py \
		--default-results results/default \
		--llm-results results/llm/evaluation \
		--output ../paper/results_macros.tex \
		--check

clean-results:
	$(PYTHON) -m cigma.cli clean --output results/default
