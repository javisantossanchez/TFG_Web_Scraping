#! /bin/bash

mongoimport todos_los_productos.json --port 27017 -u root -p example --authenticationDatabase admin -d nike --collection zapas_nike --jsonArray
