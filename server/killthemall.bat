docker-compose stop
docker container prune -f
docker volume prune -f
docker image prune -a -f
docker container ls -a
docker volume ls
docker image ls
docker-compose down --volumes