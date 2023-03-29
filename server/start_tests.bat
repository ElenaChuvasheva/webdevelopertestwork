docker-compose exec -T db createdb --username=root test_db
docker-compose exec -T db pg_dump --username=root exchange > exchange_dump
docker-compose exec -T db psql --username=root test_db < exchange_dump
docker-compose exec -T web pytest
docker-compose exec -T db dropdb --username=root test_db
