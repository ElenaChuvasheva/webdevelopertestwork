docker-compose exec -T web alembic upgrade head
docker-compose exec -T web pytest