docker stop web_server
docker rm web_server
docker build . -t bot_web_server/node-web-app
docker-compose up -d