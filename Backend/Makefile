# Alembic migration tasks for Unix/WSL
PYTHONPATH=..
ALEMBIC=alembic -c alembic.ini

migrate:
	PYTHONPATH=$(PYTHONPATH) $(ALEMBIC) upgrade head

downgrade:
	PYTHONPATH=$(PYTHONPATH) $(ALEMBIC) downgrade -1

revision:
	PYTHONPATH=$(PYTHONPATH) $(ALEMBIC) revision --autogenerate -m "$(m)"

current:
	PYTHONPATH=$(PYTHONPATH) $(ALEMBIC) current
