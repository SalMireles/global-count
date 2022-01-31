install:
	pip install --upgrade pip
	pip install poetry==1.1.12
ifeq ($(shell uname -sm),Darwin arm64)
	OPENBLAS="$(shell brew --prefix openblas)" poetry install --no-root
else
	poetry install --no-root
endif
