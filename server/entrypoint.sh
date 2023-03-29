alembic upgrade head
uvicorn server.app:api --host 0.0.0.0 --port 8000