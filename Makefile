VENV_BIN = .venv/bin

.PHONY: all
all: install

.PHONY: install
install:
	python3 -m venv .venv
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install flake8 mypy pytest build wheel

.PHONY: run
run:
	@if [ ! -d ".venv" ]; then make install; fi
	$(VENV_BIN)/python a_maze_ing.py config.txt

.PHONY: debug
debug:
	$(VENV_BIN)/python -m pdb a_maze_ing.py config.txt

.PHONY: lint
lint:
	@if [ ! -d ".venv" ]; then $(MAKE) install; fi
	$(VENV_BIN)/flake8 . --exclude=.venv,venv
	$(VENV_BIN)/mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs . --exclude "(venv|\.venv)"

.PHONY: lint-strict
lint-strict:
	$(VENV_BIN)/flake8 . --exclude=.venv,venv
	$(VENV_BIN)/mypy --strict --ignore-missing-imports . --exclude "(venv|\.venv)"

.PHONY: build
build:
	$(VENV_BIN)/python -m build --wheel --sdist --outdir .

.PHONY: clean
clean:
	rm -rf __pycache__
	rm -rf mazegen_package/__pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -f *.whl
	rm -f *.tar.gz

.PHONY: fclean
fclean: clean
	rm -rf .venv
	rm -f maze.txt  

.PHONY: re
re: fclean all
