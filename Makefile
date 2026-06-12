# Stowaway — zero-dependency demo by design.
# `make demo` needs nothing but Python 3.10+. No keys, no pip install.

.PHONY: demo demo-live test data clean

demo:            ## full three-phase audit from committed fixtures (no keys)
	python3 -m stowaway.cli audit --replay

demo-live:       ## same pipeline, real Tavily + Token Factory (.env required)
	python3 -m stowaway.cli audit --live

test:            ## unit + end-to-end tests (stdlib unittest; pytest also works)
	python3 -m unittest discover -s tests -v

data:            ## regenerate the synthetic dataset + fixtures (deterministic)
	python3 scripts/generate_dataset.py

clean:
	rm -f report.md
	find . -name __pycache__ -type d -exec rm -rf {} +
