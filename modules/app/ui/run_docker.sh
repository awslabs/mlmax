APP_DIR=$(PWD)
#APP_DIR=${APP_DIR%/*}

docker stop app
docker rm app
#docker rmi appimage
docker build --tag appimage .
docker run -v $APP_DIR:/app -p 3000:3000 -d --name app appimage
docker exec -it app /bin/bash
