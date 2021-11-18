
#! /bin/bash
sudo docker run -d -p 9000:9000 -p 8000:8000 --name portainer --restart always -v /var/run/docker.sock:/var/run/docker.sock -v /srv/portainer:/data portainer/portainer
sudo docker start portainer
cd ../mongodb
docker-compose up -d
docker exec -it mongo /bin/bash -c "./home/database/products/wait-for-it.sh --timeout=0 localhost:27017"
docker exec -it mongo /bin/bash -c "cd /home/database/products/ && ./import_database.sh"
