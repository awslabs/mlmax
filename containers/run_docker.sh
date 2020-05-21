APP_DIR=$(PWD)
APP_DIR=${APP_DIR%/*}

docker stop basic
docker rm basic
docker rmi basicimage
docker build --tag basicimage basic
docker run -v $APP_DIR:/app -d --name basic basicimage
docker exec -it basic /bin/bash
